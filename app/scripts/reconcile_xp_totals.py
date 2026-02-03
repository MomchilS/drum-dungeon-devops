#!/usr/bin/env python3

import json
from pathlib import Path
from level_utils import required_xp_for_level

STUDENT = "Dodko"
STATS_FILE = Path(f"/srv/practice-data/students/{STUDENT}/stats.json")

with open(STATS_FILE, "r") as f:
    stats = json.load(f)

# -----------------------------
# RECOMPUTE TOTAL XP FROM CATEGORIES
# -----------------------------
categories = stats["xp"]["categories"]
total_xp = sum(categories.values())

stats["xp"]["total"] = total_xp

# -----------------------------
# RECOMPUTE LEVEL STATE
# -----------------------------
current_level = 1
remaining_xp = total_xp

while remaining_xp >= required_xp_for_level(current_level):
    remaining_xp -= required_xp_for_level(current_level)
    current_level += 1

stats["level"]["current"] = current_level
stats["level"]["progress_xp"] = remaining_xp
stats["level"]["xp_to_next"] = (
    required_xp_for_level(current_level) - remaining_xp
)

with open(STATS_FILE, "w") as f:
    json.dump(stats, f, indent=2)

print(" XP totals and levels reconciled from category XP")
