import os
import json
from datetime import datetime, timezone
from pathlib import Path

from services.exercises import DAILY_EXERCISES
from app.services.medals import check_and_award_medals
from app.services.level_utils import recalculate_levels

# ========================
# ENVIRONMENT / CONFIG
# ========================

STUDENT = os.environ.get("STUDENT")
if not STUDENT:
    raise RuntimeError("STUDENT env variable not set")

EXERCISE_ID = os.environ.get("EXERCISE_ID")
if not EXERCISE_ID:
    raise RuntimeError("EXERCISE_ID not set")

BASE_DIR = Path(os.environ.get("PRACTICE_DATA_DIR", "/srv/practice-data"))
STUDENTS_DIR = BASE_DIR / "students"
STATS_FILE = STUDENTS_DIR / STUDENT / "stats.json"

# ========================
# LOAD STATS
# ========================

if not STATS_FILE.exists():
    raise RuntimeError(f"Stats file not found for student: {STUDENT}")

with open(STATS_FILE, "r") as f:
    stats = json.load(f)

# ========================
# RESOLVE XP FROM EXERCISES
# ========================

xp_gain = None

for exercises in DAILY_EXERCISES.values():
    for ex in exercises:
        if ex["id"] == EXERCISE_ID:
            xp_gain = ex.get("xp", 5)
            break
    if xp_gain is not None:
        break

# Safety fallback
if xp_gain is None:
    xp_gain = 5

# ========================
# APPLY XP
# ========================

stats["xp"]["categories"]["pad_practice"] += xp_gain
stats["xp"]["total"] = sum(stats["xp"]["categories"].values())

# ========================
# LEVELS & MEDALS
# ========================

recalculate_levels(stats)
check_and_award_medals(stats)

# ========================
# HISTORY META
# ========================

stats["history"]["last_xp_event"] = "pad_practice"
stats["history"]["last_updated"] = datetime.now(timezone.utc).isoformat()

# ========================
# SAVE STATS
# ========================

with open(STATS_FILE, "w") as f:
    json.dump(stats, f, indent=2)
