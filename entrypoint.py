import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)

import streamlit as st
import sqlite3
import logging
import os

# Configure log file for the operations on the database
if "db_log" not in st.session_state:
    st.session_state["db_log"] = "db.log"

logging.basicConfig(
    filename=st.session_state.db_log,
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(message)s",
)

from src.jobjournal.jobjournal_gui import main

if __name__=="__main__":
    # Check if environ. var. for db path has been defined
    if "db_path" not in st.session_state:
        if "JOBJOURNAL_DB_PATH" in os.environ:
            st.session_state["db_path"] = os.environ["JOBJOURNAL_DB_PATH"]

            # Check if the db exists, if not : create an empty database using the template
            if not os.path.isfile(st.session_state.db_path):
                st.toast("Création d'une nouvelle base donnée...")

                db_templ = "src/jobjournal/utils/templ/db.init.sql"
                if os.path.isfile(db_templ):
                    with sqlite3.connect(st.session_state.db_path) as conn:
                        with open(db_templ, "r", encoding="utf-8") as templ:
                            conn.executescript(templ.read())

                    st.toast("✅ Base de données crée avec succès.")
                    logging.info("Database created successfully")

                else:
                    st.toast("❌ Template non disponible.")
                    logging.info(f"Unable to find the database's template at {db_templ}")
                    raise FileNotFoundError(f"{db_templ} not found.")

        else:
            st.markdown("# Job Seeker's Journal")
            st.error("⚠️ La variable d'environnement JOBJOURNAL_DB_PATH n'existe pas.")
            st.markdown(
                "Pour utiliser l'application, définir l'emplacement de la base de données " \
                "dans la variable d'environnement JOBJOURNAL_DB_PATH, puis relancer l'application."
            )

            st.code(
                "$ export JOBJOURNAL_DB_PATH=/path/to/database\n" \
                "$ pdm run streamlit run entrypoint.py", 
                language="bash"
            )

            st.stop()

    # Run app
    main()