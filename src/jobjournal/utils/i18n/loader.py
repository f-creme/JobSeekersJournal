import json
import streamlit as st
from pathlib import Path


_locales_path = Path(__file__).parent / "locales"

# @st.cache_data
def _load_file(lang: str):
    """
    Load JSON file corresponding to the language
    """
    if not lang:
        lang = "fr"
        
    lang_file = _locales_path / f"{lang}.json"

    if not lang_file.exists():
        raise FileNotFoundError(f"Lang file not found: {lang_file}")
    
    with open(lang_file, "r", encoding="utf-8") as f:
        return json.load(f)
    

def set_language(lang: str = None):
    st.session_state["translations"] = _load_file(lang)

    
def t(key: str) -> str:
    """
    Translate a hierachical key
    """
    if not "translations" in st.session_state:
        return key
    
    keys = key.split(".")
    val = st.session_state["translations"]

    try:
        for k in keys:
            if k in val:
                val = val[k]
            else:
                return key
        return val
    except KeyError:
        return key