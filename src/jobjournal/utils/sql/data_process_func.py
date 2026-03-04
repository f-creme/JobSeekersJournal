import json

from datetime import date, datetime, timedelta

today = date.today()

from src.jobjournal.utils.templ.mappings import status_map

def week_category(date):
    d = datetime.strptime(date, "%Y-%m-%d").date()
    last_monday = today - timedelta(days=today.weekday())
    monday_before = last_monday - timedelta(days=7)

    if last_monday <= d <= today: 
        return "current"
    elif monday_before <= d < last_monday:
        return "last_week"
    else:
        return "older"

def extract_record_week_category(timeline_json):
    timeline_dict = json.loads(timeline_json)
    for entry in timeline_dict.values():
        if entry.get("headline") == "Enregistrement":
            return week_category(entry["date"])
    return None

def extract_application_week_category(timeline_json):
    timeline_dict = json.loads(timeline_json)
    for entry in timeline_dict.values():
        if entry.get("headline") == status_map[3]:
            return week_category(entry["date"])
    return None   