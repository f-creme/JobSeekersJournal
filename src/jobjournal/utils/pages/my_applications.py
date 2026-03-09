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

from src.jobjournal.utils.i18n.loader import t

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

    all_pos_dict = get_positions(st.session_state.db_path)

    if not all_pos_dict:
        st.warning(t("error.empty-database"))
        st.stop()

    all_pos_dict_r = {v: k for k, v in all_pos_dict.items()}

    pos_selector_options = [t("filter.offer-selector.all-option")] + [k for k in all_pos_dict_r]
    selected_pos = st.sidebar.selectbox(label=t("filter.offer-selector.label"),
                                        options=pos_selector_options)
    
    # Case 1: display a summary of all recorded applications
    if selected_pos == pos_selector_options[0]:
        st.markdown(f"# {t('page.applications.title')}")
        st.space("small")

        pos_summary = get_positions_summary(st.session_state.db_path)

        if not pos_summary: # Check the result of the query
            st.error(t("error.missing-applications-data"))
            st.stop()

        # Add the str status to each element
        for k in pos_summary:
            pos_summary[k]["status_str"] = status_map[pos_summary[k][pt.status]]

        # Sort
        offers_sorter_options = [
            t("filter.offers-sorter.options.default"), 
            t("filter.offers-sorter.options.pub-date"),
            t("filter.offers-sorter.options.status"),
            t("filter.offers-sorter.options.interest")
        ]
        sort_field = st.sidebar.selectbox(label=t("filter.offers-sorter.label"), options=offers_sorter_options)

        if sort_field != offers_sorter_options[0]:
            order_options = [t("filter.sorting-options.asc"), t("filter.sorting-options.desc")]
            asc_or_desc = st.sidebar.radio(label=t("filter.sorting-options.label"), options=order_options)
            if asc_or_desc == order_options[0]:
                rev = False
            else:
                rev = True

        sorted_pos_summary = pos_summary
        if sort_field == offers_sorter_options[1]:
            sorted_pos_summary = dict(sorted(pos_summary.items(), key=lambda item: item[1][pt.date], reverse=rev))
        if sort_field == offers_sorter_options[2]:
            sorted_pos_summary = dict(sorted(pos_summary.items(), key=lambda item: item[1][pt.status], reverse=rev))
        if sort_field == offers_sorter_options[3]:
            sorted_pos_summary = dict(sorted(pos_summary.items(), key=lambda item: item[1][pt.interest], reverse=rev))
            
        # Display
        for k in sorted_pos_summary:
            with st.container(border=True, key=f"container_{k}"):
                st.markdown(f"### {pos_summary[k][pt.title]}")
                st.markdown(f"**{pos_summary[k][pt.comp]}** *({pos_summary[k][pt.loc]})*")

                date_str = pos_summary[k][pt.date]
                d = datetime.strptime(date_str, "%Y-%m-%d").date()
                date_formatted = d.strftime("%d %b %Y")
                diff_days = (today - d).days
                custom_days = map_days_left(diff_days)

                status_str = t(pos_summary[k]["status_str"])
                status_num = pos_summary[k][pt.status]

                cl, cm, cr = st.columns(3)
                cm.badge(f"{date_formatted} ({t('page.applications.summary.date1')}{diff_days} {t('page.applications.summary.date2')})", color=custom_days["color"], icon=custom_days["icon"])
                cl.badge(status_str, color=status_map_customization[status_num]["color"], icon=status_map_customization[status_num]["icon"])
                cr.markdown(interest_map[pos_summary[k][pt.interest]])

    # Case 2: display all information for a specific offer
    else:
        selected_id = all_pos_dict_r[selected_pos]
        data = get_application_by_id(db_path=st.session_state.db_path, idx=selected_id)

        # Check if data have been found
        if not data:
            st.error(t("error.missing-applications-data"))
            st.stop()

        # Process some data
        status_num = data[pt.status]
        status_str = t(status_map[status_num])

        date_str = data[pt.date]
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
        date_formatted = d.strftime("%d %b %Y")
        diff_days = (today - d).days
        custom_days = map_days_left(diff_days)

        # Display
        st.markdown(f"## {data[pt.title]}")
        st.markdown(f"**{data[pt.comp]}** *({data[pt.loc]})*")

        c1, c2, c3 = st.columns(3)
        c1.badge(status_str, color=status_map_customization[status_num]["color"], icon=status_map_customization[status_num]["icon"], width="stretch")
        c2.badge(f"{date_formatted} ({t('page.applications.summary.date1')}{diff_days} {t('page.applications.summary.date2')})", color=custom_days["color"], icon=custom_days["icon"])
        c3.markdown(interest_map[data[pt.interest]])

        c1.markdown(f"ℹ️ {data[pt.source]}")
        c2.markdown(f"💸 {data[pt.salary]} {t('page.applications.summary.salary-unit')}")

        with st.expander(t("page.applications.deletion.expander")):
            if st.button(t("page.applications.deletion.confirm"), use_container_width=True, type="primary"):
                success = delete_application(st.session_state.db_path, selected_id)
                if success:
                    st.success(t("message.offer-deletion.success"))
                else: 
                    st.error(t("message.offer-deletion.failure"))

        tab1, tab2, tab3, tab4 = st.tabs([
            t("page.applications.tabs.details.title"),
            t("page.applications.tabs.motivations.title"),
            t("page.applications.tabs.skills.title"),
            t("page.applications.tabs.timeline.title")
        ])
        with tab1:
            st.markdown(f"{data[pt.details]}")

        with tab2:
            st.markdown(f"{data[pt.motivation]}")

        with tab3:
            st.markdown(t("page.applications.tabs.skills.caption"))
            
            skills = json.loads(data[pt.skills])
            skills_df = pd.DataFrame.from_dict(skills, orient="index")
            skills_df.columns = [
                t("page.applications.tabs.skills.table.skill"),
                t("page.applications.tabs.skills.table.experience")
            ]

            static_table(skills_df, "left")

        with tab4:
            tline = json.loads(data[pt.timeline])
            events = {"events": []}

            for key, val in tline.items():
                d = datetime.strptime(val["date"], "%Y-%m-%d")
                events["events"].append({
                    "start_date": {"year": d.year, "month": d.month, "day": d.day},
                    "text": {"headline": t(val["headline"]), "text": val["text"]}
                })

            timeline(events, height=350)

            # Add new event to the timeline
            with st.expander(t("page.applications.tabs.timeline.expander.label")):
                new_tline = tline
                next_event = str(len(tline))

                st.info(t("page.applications.tabs.timeline.expander.info"))

                new_date = st.date_input(label=t("page.applications.tabs.timeline.expander.fields.date"))

                # Auto-fill event's headline
                if not "new_headline_value" in st.session_state:
                    st.session_state["new_headline_value"] = ""

                c1, c2, c3 = st.columns(3)
                columns = [c1, c2, c3]
                for i, (key, status) in enumerate(status_map.items()):
                    col_num = i % 3
                    with columns[col_num]:
                        if st.button(label=f"{status_map_customization[key]["icon"]} {t(status)}", use_container_width=True):
                            st.session_state.new_headline_value = status

                new_headline = st.text_input(label=t("page.applications.tabs.timeline.expander.fields.name"), value=t(st.session_state.new_headline_value))
                new_text = st.text_area(label=t("page.applications.tabs.timeline.expander.fields.details"))

                if st.button(t("page.applications.tabs.timeline.expander.button.label"), use_container_width=True, type="primary"):
                    new_tline[next_event] = {}
                    new_tline[next_event]["date"] = new_date.strftime("%Y-%m-%d")
                    new_tline[next_event]["headline"] = new_headline
                    new_tline[next_event]["text"] = new_text

                    new_tline_json = json.dumps(new_tline)

                    success = update_application_timeline(st.session_state.db_path, selected_id, new_tline_json, new_tline[next_event]["headline"])

                    if success:
                        st.success(t("message.timeline-update.success"))
                    else: 
                        st.error(t("message.timeline-update.failure"))

                    # Reset auto-fill 
                    st.session_state.new_headline_value = ""