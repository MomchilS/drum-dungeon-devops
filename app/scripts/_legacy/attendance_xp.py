import json
from datetime import datetime
from app.services.level_utils import recalculate_levels
from app.services.medals import check_and_award_medals
from app.main import STUDENTS_DIR


ATTENDANCE_XP = 20
CONSISTENCY_BONUS_XP = 10


def apply_attendance(student: str, date: str):
    stats_file = STUDENTS_DIR / student / "stats.json"

    if not stats_file.exists():
        raise RuntimeError(f"Stats file not found for student: {student}")

    with open(stats_file, "r") as f:
        stats = json.load(f)

    # --------------------------------------------------
    # ENSURE STRUCTURE (CRITICAL DEFENSIVE LAYER)
    # --------------------------------------------------

    # Attendance
    attendance = stats.setdefault("attendance", {})
    if not isinstance(attendance, dict):
        attendance = {}
        stats["attendance"] = attendance

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
    if not isinstance(xp, dict):
        xp = {}
        stats["xp"] = xp

    categories = xp.setdefault("categories", {})
    if not isinstance(categories, dict):
        categories = {}
        xp["categories"] = categories

    categories.setdefault("attendance", 0)
    categories.setdefault("consistency", 0)

    # --------------------------------------------------
    # APPLY ATTENDANCE
    # --------------------------------------------------
    attendance["lifetime_lessons"] += 1
    attendance["dates"].append(date)

    categories["attendance"] += ATTENDANCE_XP

    # --------------------------------------------------
    # MONTHLY LOGIC
    # --------------------------------------------------
    now = datetime.utcnow()
    current_month = now.strftime("%Y-%m")

    if attendance["current_month"]["month"] != current_month:
        attendance["current_month"] = {
            "month": current_month,
            "count": 0,
            "bonus_awarded": False,
        }

    attendance["current_month"]["count"] += 1

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
    # HISTORY
    # --------------------------------------------------
    history = stats.setdefault("history", {})
    history["last_xp_event"] = "attendance"
    history["last_updated"] = now.isoformat()

    # --------------------------------------------------
    # SAVE
    # --------------------------------------------------
    with open(stats_file, "w") as f:
        json.dump(stats, f, indent=2)