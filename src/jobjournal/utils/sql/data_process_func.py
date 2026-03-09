import json

from datetime import date, datetime, timedelta

today = date.today()

from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

_geocode = None

def get_geocode():
    global _geocode
    if _geocode is None:
        geolocator = Nominatim(user_agent="jsj-test (contact.fcreme@gmail.com)")
        _geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1, max_retries=2, error_wait_seconds=2)
    return _geocode

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
        if entry.get("headline") == "data.status.-1":
            return week_category(entry["date"])
    return None

def extract_application_week_category(timeline_json):
    timeline_dict = json.loads(timeline_json)
    for entry in timeline_dict.values():
        if entry.get("headline") == status_map[3]:
            return week_category(entry["date"])
    return None

def extract_places(places: str) -> list:
    """
    Format the job location(s) indicated in the forms
    """
    
    l = [loc.strip() for loc in places.split(", ")]
    l_ = [loc.split("(")[0].strip().lower() for loc in l]

    return l_

def find_place_coordinates(place: str) -> tuple:
    """
    Use geopy to find the latitude and longitude of a place given its name

    :return tuple:  (latitude, longitude)
    """
    geocode = get_geocode()
    results = geocode(place)
    if results:
        return (results.latitude, results.longitude)
    else:
        return None