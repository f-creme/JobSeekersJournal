"""page for consulting registered job offers"""

import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)

import streamlit as st
import pandas as pd
import json

from typing import Literal
import markdown

from streamlit_timeline import timeline

from datetime import date, datetime

today = date.today()

from src.jobjournal.utils.sql.queries import get_positions, get_positions_summary, get_application_by_id, update_application_timeline, delete_application
from src.jobjournal.utils.sql.var import PositionsTable as pt
from src.jobjournal.utils.templ.mappings import interest_map, status_map, status_map_customization, map_days_left

status_map_r = {k: v for v, k in status_map.items()}

def static_table(
    df: pd.DataFrame,
    text_align: Literal["left", "center", "right"] = "center",
    line_color: str = "rgba(150, 150, 150, 0.3)",
) -> None:

    # convertir markdown → HTML
    df_html = df.copy()
    for col in df_html.columns:
        df_html[col] = df_html[col].apply(
            lambda x: markdown.markdown(str(x)) if isinstance(x, str) else x
        )

    common_props = [
        ("text-align", text_align),
        ("border", f"1px solid {line_color}"),
        ("padding", "0.25rem 0.375rem"),
        ("vertical-align", "middle"),
        ("line-height", "1.5rem"),
    ]

    html = (
        df_html.style
        .hide(axis="index")
        .set_table_styles([
            {"selector": "th", "props": common_props},
            {"selector": "td", "props": common_props},
        ])
        .to_html(
            escape=False,   # ← CRUCIAL
            table_attributes='style="width:100%; border-collapse: collapse;"'
        )
    )

    st.html(html)

def my_applications():
    st.markdown("# Mes candidatures")
    st.markdown("---")

    all_pos_dict = get_positions(st.session_state.db_path)

    if not all_pos_dict:
        st.warning("Aucune candidature n'est enregistrée dans la base de données. \n" \
                   "Enregistrez une première candidature sur la page **Ajouter une offre**.")
        st.stop()

    all_pos_dict_r = {v: k for k, v in all_pos_dict.items()}

    selected_pos = st.sidebar.selectbox(label="Sélectionner une offre ou tout afficher",
                                        options=["Toutes"] + [k for k in all_pos_dict_r])
    
    # Case 1: display a summary of all recorded applications
    if selected_pos == "Toutes":
        pos_summary = get_positions_summary(st.session_state.db_path)

        if not pos_summary: # Check the result of the query
            st.error("Une erreur s'est produite lors de la récupération des candidatures.")
            st.stop()

        # Add the numeric status to each element
        for k in pos_summary:
            pos_summary[k]["status_num"] = status_map_r[pos_summary[k][pt.status]]

        # Sort
        sort_field = st.sidebar.selectbox(label="Trier par", options=["ID", "Date de publication", "Statut", "Intérêt"])
        asc_or_desc = st.sidebar.radio(label="Ascendant ou Descendant", options=["Ascendant", "Descendant"])
        if asc_or_desc == "Ascendant":
            rev = False
        else:
            rev = True

        sorted_pos_summary = pos_summary
        if sort_field == "Date de publication":
            sorted_pos_summary = dict(sorted(pos_summary.items(), key=lambda item: item[1][pt.date], reverse=rev))
        if sort_field == "Statut":
            sorted_pos_summary = dict(sorted(pos_summary.items(), key=lambda item: item[1]["status_num"], reverse=rev))
        if sort_field == "Intérêt":
            sorted_pos_summary = dict(sorted(pos_summary.items(), key=lambda item: item[1][pt.interest], reverse=rev))
            
        # Display
        for k in sorted_pos_summary:
            st.markdown(f"### {pos_summary[k][pt.title]}")
            st.markdown(f"**{pos_summary[k][pt.comp]}** *({pos_summary[k][pt.loc]})*")

            date_str = pos_summary[k][pt.date]
            d = datetime.strptime(date_str, "%Y-%m-%d").date()
            date_formatted = d.strftime("%d %b %Y")
            diff_days = (today - d).days
            custom_days = map_days_left(diff_days)

            status_str = pos_summary[k][pt.status]
            status_num = pos_summary[k]["status_num"]

            cl, cm, cr = st.columns(3)
            cm.badge(f"{date_formatted} (il y a {diff_days} jours)", color=custom_days["color"], icon=custom_days["icon"])
            cl.badge(status_str, color=status_map_customization[status_num]["color"], icon=status_map_customization[status_num]["icon"])
            cr.markdown(interest_map[pos_summary[k][pt.interest]])

            st.markdown("---")

    # Case 2: display all information for a specific offer
    else:
        selected_id = all_pos_dict_r[selected_pos]
        data = get_application_by_id(db_path=st.session_state.db_path, idx=selected_id)

        # Check if data have been found
        if not data:
            st.error("Une erreur s'est produite lors de la récupération des candidatures.")
            st.stop()

        # Process some data
        status_str = data[pt.status]
        status_num = status_map_r[status_str]

        date_str = data[pt.date]
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
        date_formatted = d.strftime("%d %b %Y")
        diff_days = (today - d).days
        custom_days = map_days_left(diff_days)

        # Display
        st.markdown(f"### {data[pt.title]}")
        st.markdown(f"**{data[pt.comp]}** *({data[pt.loc]})*")

        c1, c2, c3 = st.columns(3)
        c1.badge(status_str, color=status_map_customization[status_num]["color"], icon=status_map_customization[status_num]["icon"], width="stretch")
        c2.badge(f"{date_formatted} (il y a {diff_days} jours)", color=custom_days["color"], icon=custom_days["icon"])
        c3.markdown(interest_map[data[pt.interest]])

        c1.markdown(f"ℹ️ {data[pt.source]}")
        c2.markdown(f"💸 {data[pt.salary]} € bruts/an")

        with st.expander("Supprimer l'offre de la base de données"):
            if st.button("Confirmer la suppression", use_container_width=True, type="primary"):
                success = delete_application(st.session_state.db_path, selected_id)
                if success:
                    st.success("✅ Candidature supprimée avec succès.")
                else: 
                    st.error("❌ Une erreur s'est produite de la suppression de la candidature.")

        tab1, tab2, tab3, tab4 = st.tabs(["Détails", "Motivations", "Compétences", "Timeline"])
        with tab1:
            st.markdown(f"{data[pt.details]}")

        with tab2:
            st.markdown(f"{data[pt.motivation]}")

        with tab3:
            st.markdown("Compétences clées en adéquation avec le poste :")
            
            skills = json.loads(data[pt.skills])
            skills_df = pd.DataFrame.from_dict(skills, orient="index")
            skills_df.columns = ["Compétence", "Démonstration"]

            static_table(skills_df, "left")

        with tab4:
            tline = json.loads(data[pt.timeline])
            events = {"events": []}

            for key, val in tline.items():
                d = datetime.strptime(val["date"], "%Y-%m-%d")
                events["events"].append({
                    "start_date": {"year": d.year, "month": d.month, "day": d.day},
                    "text": {"headline": val["headline"], "text": val["text"]}
                })

            timeline(events, height=350)

            with st.expander("Ajouter un nouvel évènement dans la chronologie"):
                new_tline = tline
                next_event = str(len(tline))

                new_date = st.date_input(label="Date de l'événènement")
                new_headline = st.text_input(label="Titre")
                new_text = st.text_area(label="Détails")

                if st.button("Ajouter à la chronologie", use_container_width=True, type="primary"):
                    new_tline[next_event] = {}
                    new_tline[next_event]["date"] = new_date.strftime("%Y-%m-%d")
                    new_tline[next_event]["headline"] = new_headline
                    new_tline[next_event]["text"] = new_text

                    new_tline_json = json.dumps(new_tline)

                    success = update_application_timeline(st.session_state.db_path, selected_id, new_tline_json)

                    if success:
                        st.success("✅ Chronologie modifiée avec succès ! \n\nRechargez la page pour voir les modifications.")
                    else: 
                        st.error("❌ Une erreur s'est produite de la modification de la candidature.")