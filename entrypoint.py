import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)

import streamlit as st
import sqlite3
import logging
import os

# Configure log file for the operations on the database
if "db_log" not in st.session_state:
    st.session_state["db_log"] = "data/db.log"

logging.basicConfig(
    filename=st.session_state.db_log,
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(message)s",
)

from src.jobjournal.jobjournal_gui import main

if __name__=="__main__":
    # Check if environ. var. for db path has been defined
    if "db_path" not in st.session_state:
        st.session_state["db_path"] = "data/database.db"

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

    # Check if nominatim user agent variable is defined
    if "NOMINATIM_USER_AGENT" in os.environ:
        st.session_state.nominatim = os.environ["NOMINATIM_USER_AGENT"]
    else:
        st.markdown("# Job Seeker's Journal")
        st.error("⚠️ The environment variable NOMINATIM_USER_AGENT does not exist.")
        st.markdown(
            "To use the app, set a user agent name for the Nominatim search engine " \
            "in the NOMINATIM_USER_AGENT environment variable, then restart the application."
        )

        st.markdown("* **Using Docker:**")
        st.code(
            'export NOMINATIM_USER_AGENT="jsj/0.1 (+your-email@domain.com)"\n' \
            'docker run -p 8501:8501 -v path/local/data:/app/data -e NOMINATIM_USER_AGENT="$NOMINATIM_USER_AGENT" jobseekersjournal_image jobseekersjournal',
            language="bash"
        )
        st.markdown("* **or after a manual installation:**")
        st.code(
            'export NOMINATIM_USER_AGENT="jsj/0.1 (+your-email@domain.com)"\n' \
            "uv run streamlit run entrypoint.py", 
            language="bash"
        )

        st.stop()
        
    # Run app
    main()