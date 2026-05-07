from datetime import datetime, timezone
from typing import Optional

from app.services.level_utils import recalculate_levels
from app.services.medals import check_and_award_medals
from app.services.data_reader import get_student_stats
from app.services.db_operations import require_db_session, sync_student_data_to_db


ATTENDANCE_XP = 20
CONSISTENCY_BONUS_XP = 10


def apply_attendance(student: str, date_str: str, grade: Optional[int] = None):
    stats = get_student_stats(student)
    if stats is None:
        raise ValueError(f"Student not found: {student}")

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
    history = stats.setdefault("history", {})
    events = history.setdefault("events", [])

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
    if attendance["current_month"]["count"] == 4:
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
    events.append({
        "type": "attendance",
        "name": "Private Lesson",
        "date": date_str,
        "grade": grade,
    })
    history["last_xp_event"] = "attendance"
    history["last_updated"] = datetime.now(timezone.utc).isoformat()

    # --------------------------------------------------
    # SAVE TO POSTGRESQL
    # --------------------------------------------------
    db = require_db_session()
    try:
        sync_student_data_to_db(db, student, stats)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
