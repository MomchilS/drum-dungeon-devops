"""
Data reader service for runtime PostgreSQL reads.
JSON import/export is handled by explicit maintenance scripts, not live requests.
"""

from typing import Dict, List, Optional, Any

import app.database as database
from app.models import User, Student, XP, Attendance, Streak, HistoryEvent

def _require_db_session():
    if not database.DB_AVAILABLE or not database.SessionLocal:
        raise RuntimeError("Database is required for runtime data reads")
    return database.SessionLocal()


def get_users() -> Dict[str, Any]:
    """Get users from PostgreSQL."""
    db = _require_db_session()
    try:
        users_db = db.query(User).all()
        return {
            user.username: {
                "password": user.password,
                "role": user.role,
                "force_change": user.force_change
            }
            for user in users_db
        }
    finally:
        db.close()


def get_student_stats(username: str) -> Optional[Dict[str, Any]]:
    """Get student stats from PostgreSQL."""
    db = _require_db_session()
    try:
        student = db.query(Student).filter(Student.username == username).first()
        if not student:
            return None

        xp = db.query(XP).filter(XP.student_id == student.id).first()
        streak = db.query(Streak).filter(Streak.student_id == student.id).first()
        attendance_records = db.query(Attendance).filter(Attendance.student_id == student.id).all()
        history_events = db.query(HistoryEvent).filter(HistoryEvent.student_id == student.id).all()

        attendance_dates = [str(record.date) for record in attendance_records]
        current_month = None
        current_month_count = 0
        if attendance_records:
            latest_month = max(record.date for record in attendance_records).strftime("%Y-%m")
            current_month = latest_month
            current_month_count = sum(
                1 for record in attendance_records
                if record.date.strftime("%Y-%m") == latest_month
            )

        stats = {
            "xp": {
                "total": xp.total if xp else 0,
                "categories": {
                    "pad_practice": xp.pad_practice if xp else 0,
                    "attendance": xp.attendance if xp else 0,
                    "consistency": xp.consistency if xp else 0
                }
            },
            "level": {
                "current": 1,
                "progress_xp": 0,
                "xp_to_next": 10
            },
            "streak": {
                "current": streak.current if streak else 0,
                "longest": streak.longest if streak else 0,
                "last_practice_date": str(streak.last_practice_date) if streak and streak.last_practice_date else None
            },
            "attendance": {
                "dates": attendance_dates,
                "lifetime_lessons": len(attendance_dates),
                "current_month": {
                    "month": current_month,
                    "count": current_month_count,
                    "bonus_awarded": False
                }
            },
            "profile": {
                "name": student.display_name or username,
                "avatar": student.avatar or ""
            },
            "history": {
                "events": [
                    {
                        "type": event.type,
                        "name": event.name or "",
                        "date": str(event.date),
                        "grade": event.grade
                    }
                    for event in history_events
                ]
            },
            "medals": []
        }

        from app.services.level_utils import recalculate_levels
        recalculate_levels(stats)
        return stats
    finally:
        db.close()


def get_all_students() -> List[Dict[str, Any]]:
    """Get all students with their stats from PostgreSQL."""
    students = []
    db = _require_db_session()
    try:
        students_db = db.query(Student).all()
        usernames = [student.username for student in students_db]
    finally:
        db.close()

    for username in usernames:
        stats = get_student_stats(username)
        if stats:
            students.append({
                "username": username,
                "xp": stats.get("xp", {}).get("total", 0),
                "level": stats.get("level", {}).get("current", 1),
                "display_name": stats.get("profile", {}).get("name", username),
                "avatar": stats.get("profile", {}).get("avatar", "")
            })

    return students


def get_leaderboard_data() -> List[Dict[str, Any]]:
    """Get leaderboard data from PostgreSQL."""
    students = get_all_students()

    # Sort by XP descending
    students.sort(key=lambda s: s["xp"], reverse=True)

    return students
