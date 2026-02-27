"""page for consulting registered job offers"""

import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)

import streamlit as st

from datetime import date, datetime

today = date.today()

from src.jobjournal.utils.sql.queries import get_positions, get_positions_summary
from src.jobjournal.utils.sql.var import PositionsTable as pt
from src.jobjournal.utils.templ.mappings import interest_map, status_map, status_map_customization, map_days_left

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
        status_map_r = {k: v for v, k in status_map.items()}
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
            cl.badge(f"{date_formatted} (il y a {diff_days} jours)", color=custom_days["color"], icon=custom_days["icon"])
            cm.badge(status_str, color=status_map_customization[status_num]["color"], icon=status_map_customization[status_num]["icon"])
            cr.markdown(interest_map[pos_summary[k][pt.interest]])

            st.markdown("---")