import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)

import streamlit as st
import json

from datetime import date

from src.jobjournal.utils.sql.queries import add_new_position
from src.jobjournal.utils.templ.mappings import status_map, interest_map

def add_position() -> None:
    st.markdown("# Ajouter une nouveau poste")
    st.markdown("---")

    cl, cr = st.columns(2)
    # column c1
    with cl:
        position = st.text_input(label="Titre")
        source = st.text_input(label="Source")
        pub_date = st.date_input(label="Date de publication")
        status = st.selectbox(label="Statut",
                              options=[status_map[k] for k in status_map])

    # column c2
    with cr:
        company = st.text_input(label="Entreprise")
        location = st.text_input(label="Localisation", )
        salary = st.number_input(label="Salaire (€ bruts annuel)", step=10, min_value=0)
        interest = st.selectbox(label="Intérêt", 
                                options=[interest_map[k] for k in interest_map])
        
    details = st.text_area(label="Détails")
    motivations = st.text_area(label="Motivations")

    with st.expander("Compétences ciblées"):
        cl1, cr1 = st.columns(2)
        skills = {}
        for skill_id in range(5):
            skills[skill_id] = {}
            skills[skill_id]["skill"] = cl1.text_area(label=f"Compétence {skill_id+1}")
            skills[skill_id]["proof"] = cr1.text_area(label=f"Expérience associée {skill_id+1}")

    # Write to the database
    if st.button("Ajouter à la base de données", type="primary", use_container_width=True):

        interest_num = next((k for k, v in interest_map.items() if v==interest), None)

        tl = {}
        tl["0"] = {"date": pub_date.isoformat(), "headline": "Publication", "text": "Publication de l'offre en ligne."}
        tl["1"] = {"date": date.today().isoformat(), "headline": "Enregistrement", "text": "Enregistrement de l'offre dans la base de données."}
        tl_json = json.dumps(tl)

        skills_json = json.dumps(skills)

        success = add_new_position(
            db_path=st.session_state.db_path, 
            position=position, source=source, pub_date=pub_date, status=status, 
            company=company, location=location, salary=salary, interest=interest_num,
            details=details, motivations=motivations, skills=skills_json, timeline=tl_json     
        )
        if success:
            st.success("✅ Offre ajoutée à la base de donnée !")
        else: 
            st.error("❌ Une erreur s'est produite lors de l'ajout de l'offre à la base de données.")
            
    return None