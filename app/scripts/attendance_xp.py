#!/usr/bin/env python3

from medals import check_and_award_medals
import sys
import json
from datetime import datetime, timezone
from pathlib import Path

from level_utils import recalculate_levels

# ========================
# ARGS
# ========================
if len(sys.argv) != 2:
    print("Usage: attendance_xp.py <student_name>")
    sys.exit(1)

STUDENT = sys.argv[1]

ATTENDANCE_XP = 20
MONTHLY_BONUS_XP = 10

STATS_FILE = Path(
    f"/srv/practice-data/students/{STUDENT}/stats.json"
)

if not STATS_FILE.exists():
    print(f" Student '{STUDENT}' not found")
    sys.exit(1)

# ========================
# LOAD STATS
# ========================
with open(STATS_FILE, "r") as f:
    stats = json.load(f)

now = datetime.now(timezone.utc)
current_month = now.strftime("%Y-%m")

attendance = stats["attendance"]
categories = stats["xp"]["categories"]

# ========================
# MONTH ROLLOVER
# ========================
if attendance["current_month"]["month"] != current_month:
    attendance["current_month"] = {
        "month": current_month,
        "count": 0,
        "bonus_awarded": False,
    }

# ========================
# APPLY ATTENDANCE XP
# ========================
attendance["lifetime_lessons"] += 1
attendance["current_month"]["count"] += 1

categories["attendance"] += ATTENDANCE_XP

# ========================
# MONTHLY CONSISTENCY BONUS
# ========================
if (
    attendance["current_month"]["count"] >= 4
    and not attendance["current_month"]["bonus_awarded"]
):
    categories["consistency"] += MONTHLY_BONUS_XP
    attendance["current_month"]["bonus_awarded"] = True

# ========================
# RECOMPUTE TOTAL + LEVELS
# ========================
stats["xp"]["total"] = sum(categories.values())
recalculate_levels(stats)

# ========================
# HISTORY
# ========================
stats["history"]["last_xp_event"] = "attendance"
stats["history"]["last_updated"] = now.isoformat()

# ========================
# SAVE
# ========================
with open(STATS_FILE, "w") as f:
    json.dump(stats, f, indent=2)

print(f" Attendance XP recorded for {STUDENT}")
