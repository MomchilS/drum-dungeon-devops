import os
import json
from pathlib import Path
from datetime import datetime

from app.services.level_utils import recalculate_levels
from app.services.medals import check_and_award_medals
from app.services.db_operations import get_db_session, sync_student_data_to_db


# --------------------------------------------------
# ENVIRONMENT-AWARE BASE DIR
# --------------------------------------------------
BASE_DIR = Path(os.environ.get("PRACTICE_DATA_DIR", "/srv/practice-data"))
STUDENTS_DIR = BASE_DIR / "students"


ATTENDANCE_XP = 20
CONSISTENCY_BONUS_XP = 10


def apply_attendance(student: str, date_str: str):
    stats_file = STUDENTS_DIR / student / "stats.json"

    if not stats_file.exists():
        raise ValueError(f"Student not found: {student}")

    with open(stats_file, "r") as f:
        stats = json.load(f)

    # --------------------------------------------------
    # ENSURE STRUCTURE (CRITICAL FIX)
    # --------------------------------------------------

    # Attendance
    attendance = stats.setdefault("attendance", {})
    attendance.setdefault("lifetime_lessons", 0)
    attendance.setdefault("dates", [])
    attendance.setdefault(
        "current_month",
        {
            "month": None,
            "count": 0,
            "bonus_awarded": False,
        },
    )

    # XP
    xp = stats.setdefault("xp", {})
    categories = xp.setdefault("categories", {})
    categories.setdefault("attendance", 0)
    categories.setdefault("consistency", 0)

    # History
    stats.setdefault("history", {})

    # --------------------------------------------------
    # MONTH ROLLOVER LOGIC (YYYY-MM)
    # --------------------------------------------------
    month = date_str[:7]

    if attendance["current_month"]["month"] != month:
        attendance["current_month"] = {
            "month": month,
            "count": 0,
            "bonus_awarded": False,
        }

    # --------------------------------------------------
    # APPLY ATTENDANCE XP
    # --------------------------------------------------
    attendance["lifetime_lessons"] += 1
    attendance["current_month"]["count"] += 1
    attendance["dates"].append(date_str)

    categories["attendance"] += ATTENDANCE_XP

    # --------------------------------------------------
    # MONTHLY CONSISTENCY BONUS
    # --------------------------------------------------
    if (
        attendance["current_month"]["count"] >= 4
        and not attendance["current_month"]["bonus_awarded"]
    ):
        categories["consistency"] += CONSISTENCY_BONUS_XP
        attendance["current_month"]["bonus_awarded"] = True

    # --------------------------------------------------
    # RECOMPUTE TOTAL XP + LEVELS
    # --------------------------------------------------
    xp["total"] = sum(categories.values())
    recalculate_levels(stats)
    check_and_award_medals(stats)

    # --------------------------------------------------
    # HISTORY META
    # --------------------------------------------------
    stats["history"]["last_xp_event"] = "attendance"
    stats["history"]["last_updated"] = datetime.utcnow().isoformat()

    # --------------------------------------------------
    # SAVE TO JSON
    # --------------------------------------------------
    with open(stats_file, "w") as f:
        json.dump(stats, f, indent=2)

    # --------------------------------------------------
    # DUAL-WRITE: SYNC TO DATABASE
    # --------------------------------------------------
    db = get_db_session()
    if db is not None:
        try:
            sync_student_data_to_db(db, student, stats)
            db.commit()
        except Exception as e:
            print(f"Warning: Failed to sync attendance to database: {e}")
            db.rollback()
        finally:
            db.close()
