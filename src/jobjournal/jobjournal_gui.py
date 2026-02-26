import warnings 

warnings.simplefilter(action="ignore", category=FutureWarning)

import streamlit as st
import sqlite3
import os

from src.jobjournal.utils.pages.overview import overview
from src.jobjournal.utils.pages.add_position import add_position

class MultiPageApp:
    def __init__(self):
        self.pages = []

    def add_page(self, title, func):
        self.pages.append({"title": title, "function": func})

    def run(self):
        st.set_page_config(page_title="Job Seeker's Journal", layout="wide")

        st.sidebar.markdown("## Menu Principal")
        page = st.sidebar.selectbox(
            "Selectionner une page", self.pages, format_func=lambda page: page["title"]
        )

        st.sidebar.markdown("---")
        page["function"]()

def main():
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

                else:
                    st.toast("❌ Template non disponible.")
                    raise FileNotFoundError(f"{db_templ} not found.")

            # Execute the app
            app = MultiPageApp()

            app.add_page("Vue d'ensemble", overview)
            app.add_page("Ajouter une offre", add_position)

            app.run()

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
