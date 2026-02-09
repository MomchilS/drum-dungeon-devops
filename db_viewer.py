#!/usr/bin/env python3
"""
Database Viewer - Visual inspection of MariaDB contents
Run this to see your database data in a readable format.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment
os.environ["PRACTICE_DATA_DIR"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "practice_data")

from app.database import _load_database

# Load the database to check availability
_load_database()

# Now import the database components after loading
from app.database import SessionLocal, User, Student, XP, Attendance, Streak, HistoryEvent
from app.services.db_operations import get_db_session

def view_database():
    """Display all database contents in a readable format."""
    print("🎯 DRUM DUNGEON DATABASE VIEWER")
    print("=" * 50)

    db = get_db_session()
    if db is None:
        print("❌ Cannot connect to database. Please ensure MariaDB is running and database is created.")
        return

    try:
        # Users
        print("\n👥 USERS:")
        print("-" * 20)
        users = db.query(User).all()
        if users:
            for user in users:
                print(f"  Username: {user.username}")
                print(f"  Role: {user.role}")
                print(f"  Force Change: {user.force_change}")
                print()
        else:
            print("  No users found")

        # Students
        print("\n🎓 STUDENTS:")
        print("-" * 20)
        students = db.query(Student).all()
        if students:
            for student in students:
                print(f"  ID: {student.id}")
                print(f"  Username: {student.username}")
                print(f"  Display Name: {student.display_name}")
                print(f"  Avatar: {student.avatar}")
                print(f"  Created: {student.created_at}")
                print()
        else:
            print("  No students found")

        # XP
        print("\n⭐ EXPERIENCE POINTS (XP):")
        print("-" * 30)
        xps = db.query(XP).all()
        if xps:
            for xp in xps:
                print(f"  Student ID: {xp.student_id}")
                print(f"  Total XP: {xp.total}")
                print(f"  Pad Practice: {xp.pad_practice}")
                print(f"  Attendance: {xp.attendance}")
                print(f"  Consistency: {xp.consistency}")
                print()
        else:
            print("  No XP records found")

        # Streaks
        print("\n🔥 STREAKS:")
        print("-" * 15)
        streaks = db.query(Streak).all()
        if streaks:
            for streak in streaks:
                print(f"  Student ID: {streak.student_id}")
                print(f"  Current: {streak.current}")
                print(f"  Longest: {streak.longest}")
                print(f"  Last Practice: {streak.last_practice_date}")
                print()
        else:
            print("  No streak records found")

        # Attendance
        print("\n📅 ATTENDANCE RECORDS:")
        print("-" * 25)
        attendances = db.query(Attendance).all()
        if attendances:
            for att in attendances:
                print(f"  Student ID: {att.student_id}")
                print(f"  Date: {att.date}")
                print(f"  Grade: {att.grade}")
                print()
        else:
            print("  No attendance records found")

        # History Events
        print("\n📜 HISTORY EVENTS:")
        print("-" * 20)
        events = db.query(HistoryEvent).all()
        if events:
            for event in events:
                print(f"  Student ID: {event.student_id}")
                print(f"  Type: {event.type}")
                print(f"  Name: {event.name}")
                print(f"  Date: {event.date}")
                print(f"  Grade: {event.grade}")
                print()
        else:
            print("  No history events found")

        print("\n✅ Database view complete!")

    except Exception as e:
        print(f"❌ Error viewing database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    view_database()
