import sqlite3 
import logging
import pandas as pd
import streamlit as st

from src.jobjournal.utils.sql.var import PositionsTable as pt
from src.jobjournal.utils.sql.var import ContactsTable as ct

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
        cs = cn.cursor()

        query = f"INSERT INTO {pt.table_pos} ({cols_to_insert}) VALUES ({values_placehoder});"
        cs.execute(query, values)
        
        last_id = cs.lastrowid

        cn.commit()
        cs.close()
        cn.close()

        logging.info(f"ID {last_id} inserted in {pt.table_pos}.")

        return True
    
    except Exception as e:
        print("An error occured while writing the database\n", e)
        logging.error(f"An error occured while writing the database :\nQuery: {query}\nException: {e}")

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
        logging.error(f"Unable to get requested data: \n\t{query} \n\t{e}")
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
        logging.error(f"Unable to get requested data: \n\tQuery: {query} \n\tValues: {value} \n\t{e}")
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
        cs = cn.cursor()

        query = f"UPDATE {pt.table_pos} SET {cols_to_update} WHERE {pt.id} = ?;"
        cs.execute(query, values)

        cn.commit()
        cs.close()
        cn.close()

        logging.info(f"ID {idx} update in {pt.table_pos}.")
        return True

    except Exception as e:
        logging.error(f"Unable to edit ID {idx} in {pt.table_pos}. \n\tQuery: {query} \n\tValues: {values}")
        return False