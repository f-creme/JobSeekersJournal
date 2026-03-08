import warnings 

warnings.simplefilter(action="ignore", category=FutureWarning)

import streamlit as st

from src.jobjournal.utils.i18n.loader import set_language, t

from src.jobjournal.utils.pages.overview import overview
from src.jobjournal.utils.pages.my_applications import my_applications
from src.jobjournal.utils.pages.add_position import add_position
from src.jobjournal.utils.pages.edit_application import edit_application

class MultiPageApp:
    def __init__(self):
        self.pages = []

    def add_page(self, title, func):
        self.pages.append({"title": title, "function": func})

    def run(self):
        st.set_page_config(page_title="Job Seeker's Journal", layout="wide", page_icon="💼")

        with st.sidebar.container(key="sidebar_bottom"): 
            col1, col2 = st.columns([1, 7], vertical_alignment="bottom")
            col1.markdown('<svg xmlns="http://www.w3.org/2000/svg" height="40px" viewBox="0 -960 960 960" width="35px" fill="#A7C4E5"><path d="M325-111.5q-73-31.5-127.5-86t-86-127.5Q80-398 80-480.5t31.5-155q31.5-72.5 86-127t127.5-86Q398-880 480.5-880t155 31.5q72.5 31.5 127 86t86 127Q880-563 880-480.5T848.5-325q-31.5 73-86 127.5t-127 86Q563-80 480.5-80T325-111.5ZM480-162q26-36 45-75t31-83H404q12 44 31 83t45 75Zm-104-16q-18-33-31.5-68.5T322-320H204q29 50 72.5 87t99.5 55Zm208 0q56-18 99.5-55t72.5-87H638q-9 38-22.5 73.5T584-178ZM170-400h136q-3-20-4.5-39.5T300-480q0-21 1.5-40.5T306-560H170q-5 20-7.5 39.5T160-480q0 21 2.5 40.5T170-400Zm216 0h188q3-20 4.5-39.5T580-480q0-21-1.5-40.5T574-560H386q-3 20-4.5 39.5T380-480q0 21 1.5 40.5T386-400Zm268 0h136q5-20 7.5-39.5T800-480q0-21-2.5-40.5T790-560H654q3 20 4.5 39.5T660-480q0 21-1.5 40.5T654-400Zm-16-240h118q-29-50-72.5-87T584-782q18 33 31.5 68.5T638-640Zm-234 0h152q-12-44-31-83t-45-75q-26 36-45 75t-31 83Zm-200 0h118q9-38 22.5-73.5T376-782q-56 18-99.5 55T204-640Z"/></svg>', unsafe_allow_html=True)
            lang = col2.selectbox("nav.lang-selector", ["fr", "en-us"], label_visibility="collapsed")

        st.html(
            """
            <style>
                .st-key-sidebar_bottom {
                    position: absolute;
                    bottom: 15px;
                    width: 93%;
                }
            </style>
            """
            )
        
        set_language(lang)

        st.sidebar.markdown(t("nav.title"))
        page = st.sidebar.selectbox(
            t("nav.page-selector"), self.pages, format_func=lambda page: page["title"]
        )

        st.sidebar.markdown("---")
        page["function"]()

def main():
    app = MultiPageApp()

    app.add_page(t("nav.pages.overview"), overview)
    app.add_page(t("nav.pages.applications"), my_applications)
    app.add_page(t("nav.pages.add_position"), add_position)
    app.add_page(t("nav.pages.update_position"), edit_application)

    app.run()
