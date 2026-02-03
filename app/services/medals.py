# =========================================
# Medals / Achievements Engine
# =========================================

MEDALS = {
    "streak": {
        15: ("streak_15", "Disciplined novice"),
        30: ("streak_30", "Doesn't miss"),
        60: ("streak_60", "Habit monster"),
    },
    "level": {
        5: ("level_5", "4 on the floor"),
        10: ("level_10", "Groovin"),
        15: ("level_15", "Beat killer"),
        20: ("level_20", "Chops, chops, chops!"),
        30: ("level_30", "Lean, mean drum machine!"),
    },
}


def check_and_award_medals(stats: dict) -> bool:
    """
    Checks stats and awards medals if conditions are met.
    Returns True if at least one medal was added.
    """
    awarded = False
    medals = set(stats.setdefault("medals", []))

    # ---- Streak medals ----
    streak = stats["streak"]["current"]
    for threshold, (mid, _) in MEDALS["streak"].items():
        if streak >= threshold and mid not in medals:
            medals.add(mid)
            awarded = True

    # ---- Level medals ----
    level = stats["level"]["current"]
    for threshold, (mid, _) in MEDALS["level"].items():
        if level >= threshold and mid not in medals:
            medals.add(mid)
            awarded = True

    stats["medals"] = sorted(medals)
    return awarded


def medal_labels():
    """Return ID → display name map"""
    return {
        mid: name
        for category in MEDALS.values()
        for _, (mid, name) in category.items()
    }
