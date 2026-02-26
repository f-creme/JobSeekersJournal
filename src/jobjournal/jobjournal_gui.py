import warnings 

warnings.simplefilter(action="ignore", category=FutureWarning)

import streamlit as st

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
    app = MultiPageApp()

    app.add_page("Vue d'ensemble", overview)
    app.add_page("Ajouter une offre", add_position)

    app.run()
