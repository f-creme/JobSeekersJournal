import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)

import streamlit as st
import pandas as pd
import logging
import json

from src.jobjournal.utils.i18n.loader import t

from src.jobjournal.utils.sql.queries import get_positions, get_application_by_id, edit_application_by_id
from src.jobjournal.utils.sql.var import PositionsTable as pt
from src.jobjournal.utils.templ.mappings import status_map, interest_map, pre_application_status_map

def edit_application():
    st.markdown(f"# {t('page.update-poistion.title')}")
    st.markdown("---")

    all_positions_dict = get_positions(db_path=st.session_state.db_path)

    if not all_positions_dict:
        st.warning(t("error.empty-database"))
        st.stop()

    all_positions_dict_r = {v: k for k, v in all_positions_dict.items()}
    all_positions_list = [x for x in all_positions_dict_r]
    selected_position = st.sidebar.selectbox(label=t("filter.offer-selector.label"), options=all_positions_list)
    selected_id = all_positions_dict_r[selected_position]

    if selected_id:
        data = get_application_by_id(db_path=st.session_state.db_path, idx=selected_id)

        if data:
            _local_status_map = {k: t(v) for k, v in status_map.items()}
            _local_pre_application_status_map = {k: t(v) for k, v in pre_application_status_map.items()}
            _actual_status = status_map[data[pt.status]]

            position = st.text_input(label=t("form.fields.position.title.label"), value=data[pt.title])
            company = st.text_input(label=t("form.fields.position.company.label"), value=data[pt.comp])
            location = st.text_input(label=t("form.fields.position.location.label"), value=data[pt.loc],
                                     help=t("form.fields.position.location.help"))
            source = st.text_input(label=t("form.fields.position.source.label"), value=data[pt.source])
            pub_date = st.date_input(label=t("form.fields.position.pub-date.label"), value=data[pt.date])
            salary = st.number_input(label=t("form.fields.position.salary.label"), value=data[pt.salary], step=10.0, min_value=0.0)

            status = st.selectbox(label=t("form.fields.position.status.label"), 
                                  options=[t(_actual_status)] + [v for k, v in _local_status_map.items()],
                                  help=t("form.fields.position.status.help"))
            interest = st.selectbox(label=t("form.fields.position.interest.label"), 
                                    options=[interest_map[data[pt.interest]]] + [interest_map[k] for k in interest_map],
                                    help=t("form.fields.position.interest.help"))
                
            details = st.text_area(label=t("form.fields.position.details.label"), value=data[pt.details],
                                   help=t("form.fields.position.details.help"))
            motivations = st.text_area(label=t("form.fields.position.motivations.label"), value=data[pt.motivation],
                                       help=t("form.fields.position.motivations.help"))

            old_skills = json.loads(data[pt.skills])
            with st.expander(t("form.expander.skills.label")):
                st.markdown(t("form.expander.skills.caption"))
                st.info(t("form.expander.skills.info"))
                cl1, cr1 = st.columns(2)
                skills = {}
                for skill_id in range(5):
                    skills[skill_id] = {}
                    skills[skill_id]["skill"] = cl1.text_area(label=f"{t('form.expander.skills.skill-label')}{skill_id+1}", value=old_skills[str(skill_id)]["skill"])
                    skills[skill_id]["proof"] = cr1.text_area(label=f"{t('form.expander.skills.proof-label')}{skill_id+1}", value=old_skills[str(skill_id)]["proof"])

            old_tl = json.loads(data[pt.timeline])
            with st.expander(t('form.expander.timeline.label')):
                st.markdown(t('form.expander.timeline.caption'))
                st.info(t('form.expander.timeline.info'))
                st.warning(t('form.expander.timeline.warning'))
                cl2, cr2, cr3 = st.columns(3)
                events = {} 
                for event_id in old_tl:
                    events[event_id] = {}
                    new_date = cl2.date_input(label=f"{t('form.expander.timeline.field.date')}{int(event_id)+1}", value=old_tl[event_id]["date"])
                    events[event_id]["date"] = str(new_date)
                    _locale_headline = cr2.text_input(label=f"{t('form.expander.timeline.field.title')}{int(event_id)+1}", value=t(old_tl[event_id]["headline"]))
                    _locale_headline = next((status_map[k] for k, v in _local_status_map.items() if v==_locale_headline), _locale_headline)
                    events[event_id]["headline"] = next((pre_application_status_map[k] for k, v in _local_pre_application_status_map.items() if v==_locale_headline), _locale_headline)
                    events[event_id]["text"] = cr3.text_input(label=f"{t('form.expander.timeline.field.content')}{int(event_id)+1}", value=old_tl[event_id]["text"])
                
            if st.button(t("form.button.update-position.label"), use_container_width=True, type="primary"):
                skills_json = json.dumps(skills)
                events_json = json.dumps(events)
                status_num = next((k for k, v in _local_status_map.items() if v==status), None)
                interest_num = next((k for k, v in interest_map.items() if v==interest), None)

                success = edit_application_by_id(
                    db_path=st.session_state.db_path, idx=selected_id, 
                    position=position, source=source, pub_date=pub_date, status=status_num, 
                    company=company, location=location, salary=salary, interest=interest_num,
                    details=details, motivations=motivations, skills=skills_json, timeline=events_json     
                )

                if success:
                    st.success(t("message.update-position.success"))
                else: 
                    st.error(t("message.update-position.failure"))
    return None