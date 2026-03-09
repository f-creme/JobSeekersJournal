import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)

import streamlit as st
import json

from datetime import date

from src.jobjournal.utils.i18n.loader import t

from src.jobjournal.utils.sql.queries import add_new_position
from src.jobjournal.utils.templ.mappings import status_map, interest_map

def add_position() -> None:
    st.markdown(f"# {t('page.new-position.title')}")
    st.markdown("---")

    cl, cr = st.columns(2)
    # column c1
    with cl:
        position = st.text_input(label=t("form.fields.position.title.label"))
        source = st.text_input(label=t("form.fields.position.source.label"))
        pub_date = st.date_input(label=t("form.fields.position.pub-date.label"))
        
        _local_status_map = {k: t(v) for k, v in status_map.items()}
        status = st.selectbox(label=t("form.fields.position.status.label"),
                              options=[_local_status_map[x] for x in _local_status_map],
                              help=t("form.fields.position.status.help"))

    # column c2
    with cr:
        company = st.text_input(label=t("form.fields.position.company.label"))
        location = st.text_input(label=t("form.fields.position.location.label"), help=t("form.fields.position.location.help"))
        salary = st.number_input(label=t("form.fields.position.salary.label"), step=10, min_value=0, help=t("form.fields.position.salary.help"))
        interest = st.selectbox(label=t("form.fields.position.interest.label"), 
                                options=[interest_map[k] for k in interest_map],
                                help=t("form.fields.position.interest.help"))
        
    details = st.text_area(
        label=t("form.fields.position.details.label"), help=t("form.fields.position.details.help")
    )
    motivations = st.text_area(
        label=t("form.fields.position.motivations.label"), help=t("form.fields.position.motivations.help")
    )

    with st.expander(t("form.expander.skills.label")):
        st.markdown(t("form.expander.skills.caption"))
        st.info(t("form.expander.skills.info"))
        cl1, cr1 = st.columns(2)
        skills = {}
        for skill_id in range(5):
            skills[skill_id] = {}
            skills[skill_id]["skill"] = cl1.text_area(label=f"{t('form.fields.position.skills.skill-label')}{skill_id+1}")
            skills[skill_id]["proof"] = cr1.text_area(label=f"{t('form.fields.position.skills.proof-label')}{skill_id+1}")

    # Write to the database
    if st.button(t("form.button.add-position.label"), type="primary", use_container_width=True):

        interest_num = next((k for k, v in interest_map.items() if v==interest), None)
        status_num = next((k for k, v in _local_status_map.items() if v==status), None)

        tl = {}
        tl["0"] = {"date": pub_date.isoformat(), "headline": "data.status.-2", "text": ""}
        tl["1"] = {"date": date.today().isoformat(), "headline": "data.status.-1", "text": ""}
        tl_json = json.dumps(tl)

        skills_json = json.dumps(skills)

        success = add_new_position(
            db_path=st.session_state.db_path, 
            position=position, source=source, pub_date=pub_date, status=status_num, 
            company=company, location=location, salary=salary, interest=interest_num,
            details=details, motivations=motivations, skills=skills_json, timeline=tl_json     
        )
        if success:
            st.success(t("message.new-position.success"))
        else: 
            st.error(t("message.new-position.failure"))
            
    return None