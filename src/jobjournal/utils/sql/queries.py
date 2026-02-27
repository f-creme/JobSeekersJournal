import sqlite3 
import logging
import pandas as pd
import streamlit as st

from src.jobjournal.utils.sql.var import PositionsTable as pt
from src.jobjournal.utils.sql.var import ContactsTable as ct

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

        query = f"INSERT INTO {pt.table_pos} ({cols_to_insert}) VALUES ({values_placehoder});"
        cs.execute(query, values)
        
        last_id = cs.lastrowid

        cn.commit()
        cs.close()
        cn.close()

        return True
    
    except Exception as e:
        print("An error occured while writing the database\n", e)
        logging.error(f"An error occured: {query} | params={str(values)}")

        return False

def get_positions(db_path: str) -> dict:
    """
    Get all positions recorded in the database
    """

    try:
        cn = sqlite3.connect(db_path)
        cs = cn.cursor()

        query = f"SELECT {pt.id}, {pt.comp}, {pt.title} FROM {pt.table_pos};" 
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

        query = f"SELECT {pt.id}, {pt.comp}, {pt.title}, {pt.loc}, {pt.date}, {pt.interest}, {pt.status} FROM {pt.table_pos};" 
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

        query = f"SELECT * FROM {pt.table_pos} WHERE {pt.id} = ?;"
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

        query = f"UPDATE {pt.table_pos} SET {cols_to_update} WHERE {pt.id} = ?;"
        cs.execute(query, values)

        cn.commit()
        cs.close()
        cn.close()

        return True

    except Exception as e:
        logging.error(f"An error occured: {query} | params={str(values)}")
        return False
    
def update_application_timeline(db_path: str, idx: int, events) -> bool:
    """
    Update the timeline field of a selected application with its ID
    """

    try:
        cn = sqlite3.connect(db_path)
        cs = LoggingCursor(cn.cursor())

        query = f"UPDATE {pt.table_pos} SET {pt.timeline} = ? WHERE {pt.id} = ?;"
        values = (events, idx)

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

        query = f"DELETE FROM {pt.table_pos} WHERE {pt.id} = ?;"
        values = (idx, )
        cs.execute(query, values)

        cn.commit()
        cs.close()
        cn.close()

        return True
    
    except Exception as e:
        logging.error(f"An error occured: {query} | params={str(values)}")
        return False