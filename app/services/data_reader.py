"""
Data reader service with MariaDB-first, JSON-fallback logic.
Reads from MariaDB primarily, falls back to JSON with logging.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import date, datetime

from app.database import DB_AVAILABLE, SessionLocal
from app.config import PRACTICE_DATA_DIR

# Fallback directories
STUDENTS_DIR = PRACTICE_DATA_DIR / "students"
USERS_FILE = PRACTICE_DATA_DIR / "users.json"


def log_fallback(message: str):
    """Log when falling back to JSON storage."""
    print(f"⚠️  DB FALLBACK: {message}")
    print("   Using JSON backup storage")


def get_users() -> Dict[str, Any]:
    """Get users - try MariaDB first, then JSON."""
    if DB_AVAILABLE and SessionLocal:
        try:
            db = SessionLocal()
            users_db = db.query(db.query()._entities[0].class_).all()  # Get User model
            users = {}
            for user in users_db:
                users[user.username] = {
                    "password": user.password,
                    "role": user.role,
                    "force_change": user.force_change
                }
            db.close()
            return users
        except Exception as e:
            log_fallback(f"Failed to read users from MariaDB: {e}")

    # Fallback to JSON
    if USERS_FILE.exists():
        with open(USERS_FILE, "r") as f:
            return json.load(f)

    return {}


def get_student_stats(username: str) -> Optional[Dict[str, Any]]:
    """Get student stats - try MariaDB first, then JSON."""
    if DB_AVAILABLE and SessionLocal:
        try:
            db = SessionLocal()

            # Get student
            student = db.query(db.query()._entities[0].class_).filter_by(username=username).first()
            if not student:
                db.close()
                return None

            # Get XP
            xp = db.query(db.query()._entities[1].class_).filter_by(student_id=student.id).first()

            # Get streak
            streak = db.query(db.query()._entities[2].class_).filter_by(student_id=student.id).first()

            # Get attendance
            attendance_records = db.query(db.query()._entities[3].class_).filter_by(student_id=student.id).all()
            attendance_dates = [str(record.date) for record in attendance_records]

            # Get history events
            history_events = db.query(db.query()._entities[4].class_).filter_by(student_id=student.id).all()

            db.close()

            # Build stats dict
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
                    "current": 1,  # Will be calculated
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
                        "month": None,
                        "count": 0,
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
                }
            }

            # Recalculate level
            from app.services.level_utils import recalculate_levels
            recalculate_levels(stats)

            return stats

        except Exception as e:
            log_fallback(f"Failed to read student stats for {username} from MariaDB: {e}")

    # Fallback to JSON
    stats_file = STUDENTS_DIR / username / "stats.json"
    if stats_file.exists():
        with open(stats_file, "r") as f:
            return json.load(f)

    return None


def get_all_students() -> List[Dict[str, Any]]:
    """Get all students with their stats - try MariaDB first, then JSON."""
    students = []

    if DB_AVAILABLE and SessionLocal:
        try:
            db = SessionLocal()
            students_db = db.query(db.query()._entities[0].class_).all()

            for student in students_db:
                stats = get_student_stats(student.username)
                if stats:
                    students.append({
                        "username": student.username,
                        "xp": stats.get("xp", {}).get("total", 0),
                        "level": stats.get("level", {}).get("current", 1),
                        "display_name": student.display_name or student.username,
                        "avatar": student.avatar or ""
                    })

            db.close()

            if students:  # If we got data from DB, return it
                return students

        except Exception as e:
            log_fallback(f"Failed to read all students from MariaDB: {e}")

    # Fallback to JSON
    if STUDENTS_DIR.exists():
        for student_dir in STUDENTS_DIR.iterdir():
            if not student_dir.is_dir():
                continue

            username = student_dir.name
            stats_file = student_dir / "stats.json"
            if stats_file.exists():
                with open(stats_file, "r") as f:
                    stats = json.load(f)

                students.append({
                    "username": username,
                    "xp": stats.get("xp", {}).get("total", 0),
                    "level": stats.get("level", {}).get("current", 1),
                    "display_name": stats.get("profile", {}).get("name", username),
                    "avatar": stats.get("profile", {}).get("avatar", "")
                })

    return students


def get_leaderboard_data() -> List[Dict[str, Any]]:
    """Get leaderboard data - try MariaDB first, then JSON."""
    students = get_all_students()

    # Sort by XP descending
    students.sort(key=lambda s: s["xp"], reverse=True)

    return students
