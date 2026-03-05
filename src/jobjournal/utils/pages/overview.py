import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)

import streamlit as st
import pandas as pd
import plotly.express as px

from src.jobjournal.utils.sql.queries import applications_stats_overview
from src.jobjournal.utils.templ.mappings import status_map

status_map_r = {v: k for k, v in status_map.items()}

from datetime import date, datetime

today = date.today()

def overview() -> None:
    st.markdown("# Vue d'ensemble")
    st.markdown("Suivez l'avancée de votre recherche d'emploi.")
    st.markdown("---")
    
    data = applications_stats_overview(db_path=st.session_state.db_path)
    
    if data:
        col1, col2 = st.columns(2)
        col1.metric("Offres enregistrées", value=data["overall_records"], border=True)
        col1.metric(
            "Offres enregistrées (cette semaine)", border=True, value=data["current_week_records"],
            delta=f"{data['current_week_records'] - data['last_week_records']} par rapport à la semaine précédente"
        )
        col2.metric("Candidatures envoyées", value=data["overall_app"], border=True)
        col2.metric(
            "Candiature envoyées (cette semaine)", border=True, value=data["current_week_app"], 
            delta=f"{data['current_week_app'] - data['last_week_app']} par rapport à la semaine précédente"
        )

        status_d_df = pd.DataFrame().from_dict(data["status_distribution"], orient="index", columns=["count"]).reset_index(names="status")
        status_d_df["num_status"] = status_d_df["status"].apply(lambda x: status_map_r[x])

        fig = px.bar(
            status_d_df.sort_values("num_status", ascending=True), x="status", y="count", color="num_status",
            labels={"status": "Statut de candidature", "count": "Nombre de candidatures", "num_status": "Avancement"},
            title="Répartition des candidatures par statut",
            color_continuous_scale="Tealgrn"
        )
        fig.update_layout(
            title_x=0.25,
            coloraxis_showscale=False
        )
        st.plotly_chart(fig, width="stretch")

    return None