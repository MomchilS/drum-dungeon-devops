#!/usr/bin/env python3
"""
Migration script to import existing JSON data into MariaDB.
Run this once after setting up the DB.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set environment
os.environ["PRACTICE_DATA_DIR"] = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "practice_data")

import json
from pathlib import Path
from datetime import datetime
from app.config import PRACTICE_DATA_DIR

# Load the database first
from app.database import _load_database
_load_database()

# Now import the database components after loading
from app.database import SessionLocal, User, Student, XP, Attendance, Streak, HistoryEvent

def migrate_users():
    users_file = PRACTICE_DATA_DIR / "users.json"
    if not users_file.exists():
        print("No users.json found, skipping user migration")
        return

    with open(users_file, "r") as f:
        users_data = json.load(f)

    db = SessionLocal()
    try:
        for username, user_data in users_data.items():
            user = User(
                username=username,
                password=user_data["password"],
                role=user_data["role"],
                force_change=user_data.get("force_change", False)
            )
            db.add(user)
        db.commit()
        print(f"Migrated {len(users_data)} users")
    finally:
        db.close()

def migrate_students():
    students_dir = PRACTICE_DATA_DIR / "students"
    if not students_dir.exists():
        print("No students directory found, skipping student migration")
        return

    db = SessionLocal()
    try:
        for student_dir in students_dir.iterdir():
            if not student_dir.is_dir():
                continue

            username = student_dir.name
            stats_file = student_dir / "stats.json"
            if not stats_file.exists():
                continue

            with open(stats_file, "r") as f:
                stats = json.load(f)

            # Create student
            student = Student(
                username=username,
                display_name=stats.get("profile", {}).get("name", username),
                avatar=stats.get("profile", {}).get("avatar", ""),
                created_at=datetime.now()
            )
            db.add(student)
            db.flush()  # Get student.id

            # Create XP
            xp_data = stats.get("xp", {})
            xp = XP(
                student_id=student.id,
                total=xp_data.get("total", 0),
                pad_practice=xp_data.get("categories", {}).get("pad_practice", 0),
                attendance=xp_data.get("categories", {}).get("attendance", 0),
                consistency=xp_data.get("categories", {}).get("consistency", 0)
            )
            db.add(xp)

            # Create Streak
            streak_data = stats.get("streak", {})
            streak = Streak(
                student_id=student.id,
                current=streak_data.get("current", 0),
                longest=streak_data.get("longest", 0),
                last_practice_date=streak_data.get("last_practice_date")
            )
            db.add(streak)

            # Create Attendance
            attendance_data = stats.get("attendance", {})
            for date_str in attendance_data.get("dates", []):
                attendance = Attendance(
                    student_id=student.id,
                    date=date_str,
                    grade=None  # Will be updated from history
                )
                db.add(attendance)

            # Create History Events
            for event in stats.get("history", {}).get("events", []):
                history_event = HistoryEvent(
                    student_id=student.id,
                    type=event.get("type", "pad"),
                    name=event.get("name", ""),
                    date=event["date"],
                    grade=event.get("grade")
                )
                db.add(history_event)

        db.commit()
        print(f"Migrated students data")
    finally:
        db.close()

if __name__ == "__main__":
    print("Starting migration to MariaDB...")
    migrate_users()
    migrate_students()
    print("Migration complete!")
