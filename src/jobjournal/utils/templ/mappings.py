status_map = {
    0: "A traiter",
    1: "Candidature en préparation",
    2: "Candidature prête pour envoie",
    3: "Candaditure envoyée",
    4: "Echanges en cours",
    5: "Entretien à venir",
    6: "Attente de décision recruteur",
    7: "Attente de ma décision",
    8: "Acceptée", 
    9: "Refus recruteur",
    10: "Refus personnel"
}

status_map_customization = {
    0: {"color": "red", "icon": "🚩"},
    1: {"color": "orange", "icon": "📖"},
    2: {"color": "orange", "icon": "🏁"},
    3: {"color": "green", "icon": "📤"},
    4: {"color": "blue", "icon": "💬"},
    5: {"color": "blue", "icon": "👔"},
    6: {"color": "yellow", "icon": "⏳"},
    7: {"color": "yellow", "icon": "⏳"},
    8: {"color": "gray", "icon": "✅"}, 
    9: {"color": "gray", "icon": "⛔"},
    10: {"color": "gray", "icon": "🛑"}
}

interest_map = {
    0: "✩", 1: "⭐", 2: "⭐⭐", 3: "⭐⭐⭐", 4: "⭐⭐⭐⭐", 5: "⭐⭐⭐⭐⭐"
}

def map_days_left(x):
    bins_dict = {
        5: {"color": "green", "icon": "🆕"},
        10: {"color": "blue", "icon": "⏩"},
        15: {"color": "yellow", "icon": "🔥"},
        21: {"color": "orange", "icon": "🚨"},
        365: {"color": "gray", "icon": "💀"}
    }

    for thresh in sorted(bins_dict):
        if x < thresh:
            color = bins_dict[thresh]["color"]
            icon = bins_dict[thresh]["icon"]
            return {"color": color, "icon": icon}
    return None
        