import sqlite3 
import logging

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
