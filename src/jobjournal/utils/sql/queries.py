import sqlite3 
import logging
import random

import numpy as np
import pandas as pd
import streamlit as st

from datetime import date, datetime, timedelta

today = date.today()

from src.jobjournal.utils.sql.var import (PositionsTable as pt, PlacesTable as placest, JoinTable1 as j1)
from src.jobjournal.utils.sql.var import ContactsTable as ct

from src.jobjournal.utils.sql.data_process_func import *

from src.jobjournal.utils.templ.mappings import status_map

status_map_r = {k: v for v, k in status_map.items()}

class LoggingCursor:
    def __init__(self, cursor):
        self.__cursor = cursor
    
    def execute(self, query, params=None):
        full_query = query
        if params:
            try:
                full_query = query % tuple(map(repr, params))
            except TypeError:
                full_query = query + " | params=" + str(params)

        logging.info(f"Executed query: {full_query}")
        return self.__cursor.execute(query, params or ())
    
    def executemany(self, query, seq_of_params):
        logging.info(f"Executed many: {query}, | params={seq_of_params}")
        return self.__cursor.executemany(query, seq_of_params)
    
    def __getattr__(self, attr):
        return getattr(self.__cursor, attr)

def get_locations(db_path: str, force_update: bool = False) -> dict:
    if not "locations" in st.session_state or force_update==True:
        with sqlite3.connect(db_path) as cn:
            cs = cn.cursor()
            cs.execute("SELECT * FROM places;")

            data = cs.fetchall()
            cols = [d[0] for d in cs.description]
            df = pd.DataFrame(data, columns=cols).set_index(placest.place)

        return df.to_dict("index")
    else:
        return st.session_state.locations

def record_location(db_path: str, location: str, idx: int):
    # Process location string
    location_list = extract_places(location)

    # Get recorded locations
    st.session_state.locations = get_locations(db_path)

    # Find places to add to the places table
    places_not_in_db = [loc for loc in location_list if loc not in st.session_state.locations]

    # Add new places in the places table, with associated coordinates
    places_coord = []
    for place in places_not_in_db:
        res = find_place_coordinates(place)
        if res:
            places_coord.append((place, res[0], res[1]))

    # print("begin : ", st.session_state.locations, "\n")
    if len(places_coord) > 0:
        with sqlite3.connect(db_path) as cn:
            cs = LoggingCursor(cn.cursor())
            
            try: 
                query = f"INSERT INTO {placest._NAME} ({placest.place}, {placest.lat}, {placest.lon}) VALUES (?, ?, ?);"
                cs.executemany(query, places_coord)

            except:
                logging.error(f"An error occured: {query} | params={str(places_coord)}")
                return False
            
        # Update st.session_state.locations to have updated (place, id) couples
        st.session_state.locations = get_locations(db_path, force_update=True)

        # print("updated :", st.session_state.locations, "\n")

    # Update join table
    values_join_table = []
    for place in location_list:
        if place in st.session_state.locations:
            values_join_table.append((st.session_state.locations[place][placest.id], idx))

    # print("values to add in join table :", values_join_table, "\n")

    if len(values_join_table) > 0:
        with sqlite3.connect(db_path) as cn:
            try:
                cs = LoggingCursor(cn.cursor())

                # Delete all entries with selected position's id
                cs.execute(f"DELETE FROM {j1._NAME} WHERE {j1.pos} = ?;", (idx, ))

                # Insert new entries
                cs.executemany(
                    f"INSERT INTO {j1._NAME} ({j1.place}, {j1.pos}) VALUES (?, ?);",
                    values_join_table
                )

                cn.commit()

                return True

            except: 
                cn.rollback()
                logging.error(f"An error occured while updating position-places join table with {j1.pos} = {idx}")
                return False

    return True

def add_new_position(
        db_path: str,
        position: str, source: str, pub_date, status: int,
        company: str, location: str, salary: float, interest: int,
        details: str, motivations: str, skills: dict, timeline: dict
) -> bool :
    
    cols_to_insert = ", ".join([
        pt.date, pt.title, pt.comp, pt.loc, pt.source, pt.interest, pt.status,
        pt.salary, pt.details, pt.skills, pt.motivation, pt.timeline
    ])

    values = (
        pub_date, position, company, location, source, interest, status,
        salary, details, skills, motivations, timeline
    )

    values_placehoder = ", ".join(["?" for k in range(len(values))])

    try:
        cn = sqlite3.connect(db_path)
        cs = LoggingCursor(cn.cursor())

        query = f"INSERT INTO {pt._NAME} ({cols_to_insert}) VALUES ({values_placehoder});"
        cs.execute(query, values)
        
        last_id = cs.lastrowid

        cn.commit()
        cs.close()
        cn.close()
    
    except Exception as e:
        print("An error occured while writing the database\n", e)
        logging.error(f"An error occured: {query} | params={str(values)}")

        return False
    
    loc_recorded = record_location(db_path=db_path, location=location, idx=last_id)
    if loc_recorded:
        return True
    else:
        return False

def get_positions(db_path: str) -> dict:
    """
    Get all positions recorded in the database
    """

    try:
        cn = sqlite3.connect(db_path)
        cs = cn.cursor()

        query = f"SELECT {pt.id}, {pt.comp}, {pt.title} FROM {pt._NAME};" 
        cs.execute(query)

        data = cs.fetchall()
        cols = [desc[0] for desc in cs.description]

        cs.close()
        cn.close()

        df = pd.DataFrame(data=data, columns=cols)
        df["synthetic"] = df.apply(lambda x: f"{x[pt.comp]} | {x[pt.title]}", axis=1)
        
        mapping = df.set_index(pt.id)["synthetic"].to_dict()
        return mapping

    except Exception as e:
        logging.error(f"An error occured: {query}")
        return False

def get_positions_summary(db_path: str) -> dict:
    """
    Get basic information about all positions recorded in the database
    """

    try:
        cn = sqlite3.connect(db_path)
        cs = cn.cursor()

        query = f"SELECT {pt.id}, {pt.comp}, {pt.title}, {pt.loc}, {pt.date}, {pt.interest}, {pt.status} FROM {pt._NAME};" 
        cs.execute(query)

        data = cs.fetchall()
        cols = [desc[0] for desc in cs.description]

        cs.close()
        cn.close()

        df = pd.DataFrame(data=data, columns=cols)

        mapping = df.set_index(pt.id, drop=True).to_dict("index")
        return mapping

    except Exception as e:
        logging.error(f"An error occured: {query}")
        return False

def get_application_by_id(db_path: str, idx: id) -> dict:
    """
    Get information about a specific application according to its id
    """

    try:
        cn = sqlite3.connect(db_path)
        cs = cn.cursor()

        query = f"SELECT * FROM {pt._NAME} WHERE {pt.id} = ?;"
        value = (idx, )

        cs.execute(query, value)

        data = cs.fetchall()
        cols = [desc[0] for desc in cs.description]
        df = pd.DataFrame(data=data, columns=cols)
        
        mapping = df.iloc[0].to_dict()

        cs.close()
        cn.close()

        return mapping
    
    except Exception as e:
        st.toast("❌ Récupération des données impossible.")
        logging.error(f"An error occured: {query} | params={str(value)}")
        return  False

def edit_application_by_id(
    db_path: str, idx: int, 
    position: str, source: str, pub_date, status: int,
    company: str, location: str, salary: float, interest: int,
    details: str, motivations: str, skills: dict, timeline: dict
) -> bool :
    
    cols_to_update = [
        pt.date, pt.title, pt.comp, pt.loc, pt.source, pt.interest, pt.status,
        pt.salary, pt.details, pt.skills, pt.motivation, pt.timeline
    ]
    cols_to_update = [f"{x} = ?" for x in cols_to_update]
    cols_to_update = ", ".join(cols_to_update)

    values = (
        pub_date, position, company, location, source, interest, status,
        salary, details, skills, motivations, timeline, idx
    )

    try:
        cn = sqlite3.connect(db_path)
        cs = LoggingCursor(cn.cursor())

        query = f"UPDATE {pt._NAME} SET {cols_to_update} WHERE {pt.id} = ?;"
        cs.execute(query, values)

        cn.commit()
        cs.close()
        cn.close()

    except Exception as e:
        logging.error(f"An error occured: {query} | params={str(values)}")
        return False
    
    loc_record = record_location(db_path=db_path, location=location, idx=idx)

    if not loc_record:
        return False

    return True
    
def update_application_timeline(db_path: str, idx: int, events, last_headline: str) -> bool:
    """
    Update the timeline field of a selected application with its ID. 
    Check if the newest element of the timeline corresponds to a status change accordingly
    """

    try:
        cn = sqlite3.connect(db_path)
        cs = LoggingCursor(cn.cursor())

        # Update the timeline
        query = f"UPDATE {pt._NAME} SET {pt.timeline} = ? WHERE {pt.id} = ?;"
        values = (events, idx)

        cs.execute(query, values)

        # Check if the status needs to be changed
        if last_headline in status_map_r:
            query = f"UPDATE {pt._NAME} SET {pt.status} = ? WHERE {pt.id} = ?;"
            values = (last_headline, idx)
            cs.execute(query, values)

        cn.commit()
        cs.close()
        cn.close()

        return True
    
    except Exception as e:
        logging.error(f"An error occured: {query} | params={str(values)}")
        return False
    
def delete_application(db_path: str, idx: int) -> bool:
    """
    Delete a job offer from the database according to its ID
    """

    try: 
        cn = sqlite3.connect(db_path)
        cs = LoggingCursor(cn.cursor())

        query = f"DELETE FROM {pt._NAME} WHERE {pt.id} = ?;"
        values = (idx, )
        cs.execute(query, values)

        cn.commit()
        cs.close()
        cn.close()

        return True
    
    except Exception as e:
        logging.error(f"An error occured: {query} | params={str(values)}")
        return False 

def applications_stats_overview(db_path: str) -> dict:
    """
    """

    try:
        cn = sqlite3.connect(db_path)
        cs = cn.cursor()

        query = f"SELECT {pt.timeline}, {pt.status} FROM {pt._NAME};"
        cs.execute(query)
        
        data = cs.fetchall()

        cs.close()
        cn.close()
    
    except Exception as e:
        logging.error(f"An error occured: {query}")
        return False
    
    # Process data
    if not data:
        return False
    
    df = pd.DataFrame(data, columns=["timeline", "status_str"])
    df["application_sent"] = df["status_str"].apply(lambda x: status_map_r[x] >= 3)
    df["record_week"] = df["timeline"].apply(extract_record_week_category)
    df["application_week"] = df["timeline"].apply(extract_application_week_category)

    processed_data = {
        "overall_records": len(data),
        "current_week_records": int(df["record_week"].value_counts()["current"]),
        "last_week_records": int(df["record_week"].value_counts()["last_week"]),
        "overall_app": int(df["application_sent"].value_counts()[True]),
        "current_week_app": int(df["application_week"].value_counts()["current"]),
        "last_week_app": int(df["application_week"].value_counts()["last_week"]),
        "status_distribution": df["status_str"].value_counts().to_dict()        
    }

    return processed_data

def applications_places_overview(db_path: str) -> dict:

    with sqlite3.connect(db_path) as cn:

        query = "SELECT " \
        f"t1.{pt.title}, t1.{pt.comp}, t1.{pt.status}, {pt.loc}, {pt.interest}, " \
        f"t2.{placest.place}, t2.{placest.lat}, t2.{placest.lon} " \
        f"FROM {j1._NAME} AS t " \
        f"LEFT JOIN {pt._NAME} AS t1 ON t1.{pt.id} = t.{j1.pos} " \
        f"LEFT JOIN {placest._NAME} AS t2 ON t2.{placest.id} = t.{j1.place};"

        try:
            cs = cn.cursor()
            cs.execute(query)

            data = cs.fetchall()
            cols = [c[0] for c in cs.description]
            data_df = pd.DataFrame(data, columns=cols)

            cs.close()

        except Exception as e:
            logging.error(f"An error occured: {query}")
            return False
        
        return data_df.to_dict("index")