import os
import json
from pathlib import Path
from datetime import datetime

from app.services.level_utils import recalculate_levels
from app.services.medals import check_and_award_medals

# Environment-aware base directory
BASE_DIR = Path(os.environ.get("PRACTICE_DATA_DIR", "/srv/practice-data"))
STUDENTS_DIR = BASE_DIR / "students"


def apply_attendance(student: str, date_str: str):
    stats_file = STUDENTS_DIR / student / "stats.json"

    if not stats_file.exists():
        raise ValueError("Student not found")

    with open(stats_file, "r") as f:
        stats = json.load(f)

    attendance = stats["attendance"]
    categories = stats["xp"]["categories"]

    # Month reset logic (YYYY-MM)
    month = date_str[:7]
    if attendance["current_month"]["month"] != month:
        attendance["current_month"] = {
            "month": month,
            "count": 0,
            "bonus_awarded": False
        }

    # Apply attendance XP
    attendance["lifetime_lessons"] += 1
    attendance["current_month"]["count"] += 1
    categories["attendance"] += 20

    # Monthly bonus
    if (
        attendance["current_month"]["count"] >= 4
        and not attendance["current_month"]["bonus_awarded"]
    ):
        categories["consistency"] += 10
        attendance["current_month"]["bonus_awarded"] = True

    # Recalculate totals
    stats["xp"]["total"] = sum(categories.values())
    recalculate_levels(stats)
    check_and_award_medals(stats)

    stats["history"]["last_xp_event"] = "attendance"
    stats["history"]["last_updated"] = datetime.utcnow().isoformat()

    with open(stats_file, "w") as f:
        json.dump(stats, f, indent=2)
