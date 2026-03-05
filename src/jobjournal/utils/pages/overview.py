import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)

import streamlit as st
import pandas as pd
import plotly.express as px

import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster

from src.jobjournal.utils.sql.queries import applications_stats_overview, applications_places_overview
from src.jobjournal.utils.sql.var import PlacesTable, PositionsTable
from src.jobjournal.utils.templ.mappings import status_map, status_map_customization, interest_map

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

    map_data = applications_places_overview(db_path=st.session_state.db_path)

    if map_data:
        st.markdown("### Répartition géographique des candidatures")
        with st.container(width="stretch", border=True):
            col_map, col_info = st.columns([2, 1], vertical_alignment="center")

            with col_map:
                m = folium.Map(location=[47.3215806, 5.0414701], zoom_start=5)
                marker_cluster = MarkerCluster(
                        icon_create_function="""
                        function(cluster) {
                            return L.divIcon({
                                html: '<div style="background-color:#fc7cb6;color:black;border-radius:50%;padding:10px;">'
                                    + cluster.getChildCount() +
                                    '</div>',
                                className: 'marker-cluster',
                                iconSize: new L.Point(60, 60)
                            });
                        }
                    """
                ).add_to(m)
                # Add markers
                for key, record in map_data.items():
                    coords = [record[PlacesTable.lat], record[PlacesTable.lon]]

                    folium.Marker(
                        location=coords,
                        popup=key,
                        tooltip=f"{record[PlacesTable.place].capitalize()} - {record[PositionsTable.comp]}",
                        icon=folium.Icon(color="blue", prefix="fa")
                    ).add_to(marker_cluster)

                st_map = st_folium(m, width=750, return_on_hover=False)

            with col_info:
                if st_map["last_object_clicked_popup"]:
                    selected_key = int(st_map["last_object_clicked_popup"].strip())
                    selected_data = map_data[selected_key]

                    status = selected_data[PositionsTable.status]
                    color, icon = status_map_customization[status_map_r[status]]["color"], status_map_customization[status_map_r[status]]["icon"]

                    st.markdown("#### Job sélectionné")
                    st.markdown(f"* **Poste**: {selected_data[PositionsTable.title]}")                    
                    st.markdown(f"* **Entreprise**: {selected_data[PositionsTable.comp]}")
                    st.markdown(f"* **Lieu**: {selected_data[PositionsTable.loc]}")
                    st.markdown(
                        f":{color}-badge[{icon} {status}] :yellow-badge[{interest_map[selected_data[PositionsTable.interest]]}]"
                    )                 

    if not map_data and not data:
        st.info(
            "Aucune candidature n'est enregistrée dans la base de données. " \
            "Enregistrez une première candidature sur la page **Ajouter une offre**."
        )

    return None