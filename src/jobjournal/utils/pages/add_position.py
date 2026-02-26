import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)

import streamlit as st

def add_position() -> None:
    st.markdown("# Ajouter une nouveau poste")
    st.markdown("---")

    return None