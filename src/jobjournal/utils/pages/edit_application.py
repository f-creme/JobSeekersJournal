import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)

import streamlit as st
import pandas as pd
import logging
import json

from src.jobjournal.utils.sql.queries import get_positions, get_application_by_id, edit_application_by_id
from src.jobjournal.utils.sql.var import PositionsTable as pt

def edit_application():
    st.markdown("# Détailler ou modifier une candidature")
    st.markdown("---")

    all_positions_dict = get_positions(db_path=st.session_state.db_path)

    if not all_positions_dict:
        st.warning("Aucune candidature n'est enregistrée dans la base de données. \n" \
                   "Enregistrez une première candidature sur la page **Ajouter une offre**.")
        st.stop()

    all_positions_dict_r = {v: k for k, v in all_positions_dict.items()}
    all_positions_list = [x for x in all_positions_dict_r]
    selected_position = st.sidebar.selectbox(label="Sélectionner une candidature", options=all_positions_list)
    selected_id = all_positions_dict_r[selected_position]

    if selected_id:
        data = get_application_by_id(db_path=st.session_state.db_path, idx=selected_id)

        if data:
            status_map = {
                0: "A traiter",
                1: "Candidature en préparation",
                2: "Candidature prête pour envoie",
                3: "Candaditure envoyée",
                4: "Echanges en cours",
                5: "Entretien à venir",
                6: "Attente de décision recruteur",
                7: "Attente de ma décision",
                8: "Acceptée", 
                9: "Refus recruteur",
                10: "Refus personnel"
            }

            interest_map = {
                0: "✩", 1: "⭐", 2: "⭐⭐", 3: "⭐⭐⭐", 4: "⭐⭐⭐⭐", 5: "⭐⭐⭐⭐⭐"
            }


            position = st.text_input(label="Titre", value=data[pt.title])
            company = st.text_input(label="Entreprise", value=data[pt.comp])
            location = st.text_input(label="Localisation", value=data[pt.loc])
            source = st.text_input(label="Source", value=data[pt.source])
            pub_date = st.date_input(label="Date de publication", value=data[pt.date])
            salary = st.number_input(label="Salaire (€ bruts annuel)", value=data[pt.salary], step=10.0, min_value=0.0)

            status = st.selectbox(label="Statut", options=[data[pt.status]] + [status_map[k] for k in status_map])
            interest = st.selectbox(label="Intérêt", options=[interest_map[data[pt.interest]]] + [interest_map[k] for k in interest_map])
                
            details = st.text_area(label="Détails", value=data[pt.details])
            motivations = st.text_area(label="Motivations", value=data[pt.motivation])

            old_skills = json.loads(data[pt.skills])
            with st.expander("Compétences ciblées"):
                cl1, cr1 = st.columns(2)
                skills = {}
                for skill_id in range(5):
                    skills[skill_id] = {}
                    skills[skill_id]["skill"] = cl1.text_area(label=f"Compétence {skill_id+1}", value=old_skills[str(skill_id)]["skill"])
                    skills[skill_id]["proof"] = cr1.text_area(label=f"Expérience associée {skill_id+1}", value=old_skills[str(skill_id)]["proof"])

            old_tl = json.loads(data[pt.timeline])
            with st.expander("Timeline"):
                cl2, cr2 = st.columns(2)
                events = {} 
                for event_id in old_tl:
                    events[event_id] = {}
                    new_date = cl2.date_input(label=f"Date {int(event_id)+1}", value=old_tl[event_id]["date"])
                    events[event_id]["date"] = str(new_date)
                    events[event_id]["action"] = cr2.text_input(label=f"Action {int(event_id)+1}", value=old_tl[event_id]["action"])
                
            if st.button("Modifier les détails de la candidature", use_container_width=True, type="primary"):
                skills_json = json.dumps(skills)
                events_json = json.dumps(events)
                interest_num = next((k for k, v in interest_map.items() if v==interest), None)

                success = edit_application_by_id(
                    db_path=st.session_state.db_path, idx=selected_id, 
                    position=position, source=source, pub_date=pub_date, status=status, 
                    company=company, location=location, salary=salary, interest=interest_num,
                    details=details, motivations=motivations, skills=skills_json, timeline=events_json     
                )

                if success:
                    st.success("✅ Candidature modifiée avec succès !")
                else: 
                    st.error("❌ Une erreur s'est produite de la modification de la candidature.")
    return None