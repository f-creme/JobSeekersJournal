status_map = {
    0: "data.status.0",
    1: "data.status.1",
    2: "data.status.2",
    3: "data.status.3",
    4: "data.status.4",
    5: "data.status.5",
    6: "data.status.6",
    7: "data.status.7",
    8: "data.status.8", 
    9: "data.status.9",
    10: "data.status.10"
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

pre_application_status_map = {
    -2: "data.status.-2",
    -1: "data.status.-1"
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
        