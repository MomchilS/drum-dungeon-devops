"""
Database operations for dual-write strategy.
Handles writing to MariaDB while keeping JSON as primary read source.
"""

from sqlalchemy.orm import Session
from app.database import SessionLocal, Student, XP, Attendance, Streak, HistoryEvent, DB_AVAILABLE
from datetime import datetime, date
from typing import Optional


def get_db_session():
    """Get a database session."""
    if not DB_AVAILABLE:
        return None
    return SessionLocal()


def create_or_update_student(db: Session, username: str, display_name: str = None, avatar: str = None) -> Student:
    """Create or update a student in the database."""
    student = db.query(Student).filter(Student.username == username).first()
    if not student:
        student = Student(
            username=username,
            display_name=display_name or username,
            avatar=avatar or "",
            created_at=datetime.now()
        )
        db.add(student)
        db.flush()
    else:
        if display_name:
            student.display_name = display_name
        if avatar:
            student.avatar = avatar
    return student


def update_student_xp(db: Session, student_id: int, total: int, pad_practice: int, attendance: int, consistency: int):
    """Update or create XP record for a student."""
    xp = db.query(XP).filter(XP.student_id == student_id).first()
    if not xp:
        xp = XP(
            student_id=student_id,
            total=total,
            pad_practice=pad_practice,
            attendance=attendance,
            consistency=consistency
        )
        db.add(xp)
    else:
        xp.total = total
        xp.pad_practice = pad_practice
        xp.attendance = attendance
        xp.consistency = consistency


def update_student_streak(db: Session, student_id: int, current: int, longest: int, last_practice_date: Optional[str]):
    """Update or create streak record for a student."""
    streak = db.query(Streak).filter(Streak.student_id == student_id).first()
    last_date = date.fromisoformat(last_practice_date) if last_practice_date else None

    if not streak:
        streak = Streak(
            student_id=student_id,
            current=current,
            longest=longest,
            last_practice_date=last_date
        )
        db.add(streak)
    else:
        streak.current = current
        streak.longest = longest
        streak.last_practice_date = last_date


def add_attendance_record(db: Session, student_id: int, date_str: str, grade: Optional[float] = None):
    """Add an attendance record for a student."""
    attendance_date = date.fromisoformat(date_str)
    attendance = Attendance(
        student_id=student_id,
        date=attendance_date,
        grade=grade
    )
    db.add(attendance)


def add_history_event(db: Session, student_id: int, event_type: str, name: str, date_str: str, grade: Optional[float] = None):
    """Add a history event for a student."""
    event_date = date.fromisoformat(date_str)
    history_event = HistoryEvent(
        student_id=student_id,
        type=event_type,
        name=name,
        date=event_date,
        grade=grade
    )
    db.add(history_event)


def sync_student_data_to_db(db: Session, username: str, stats: dict):
    """Sync complete student data from JSON stats to database."""
    if not DB_AVAILABLE or db is None:
        return  # Skip database operations when DB is not available

    # Create/update student
    profile = stats.get("profile", {})
    student = create_or_update_student(
        db=db,
        username=username,
        display_name=profile.get("name", username),
        avatar=profile.get("avatar", "")
    )

    # Update XP
    xp_data = stats.get("xp", {})
    categories = xp_data.get("categories", {})
    update_student_xp(
        db=db,
        student_id=student.id,
        total=xp_data.get("total", 0),
        pad_practice=categories.get("pad_practice", 0),
        attendance=categories.get("attendance", 0),
        consistency=categories.get("consistency", 0)
    )

    # Update streak
    streak_data = stats.get("streak", {})
    update_student_streak(
        db=db,
        student_id=student.id,
        current=streak_data.get("current", 0),
        longest=streak_data.get("longest", 0),
        last_practice_date=streak_data.get("last_practice_date")
    )

    # Sync attendance records
    attendance_data = stats.get("attendance", {})
    for date_str in attendance_data.get("dates", []):
        # Check if already exists to avoid duplicates
        existing = db.query(Attendance).filter(
            Attendance.student_id == student.id,
            Attendance.date == date.fromisoformat(date_str)
        ).first()
        if not existing:
            add_attendance_record(db, student.id, date_str)

    # Sync history events
    history_events = stats.get("history", {}).get("events", [])
    for event in history_events:
        # Check if already exists to avoid duplicates
        existing = db.query(HistoryEvent).filter(
            HistoryEvent.student_id == student.id,
            HistoryEvent.date == date.fromisoformat(event["date"]),
            HistoryEvent.type == event.get("type", "pad"),
            HistoryEvent.name == event.get("name", "")
        ).first()
        if not existing:
            add_history_event(
                db=db,
                student_id=student.id,
                event_type=event.get("type", "pad"),
                name=event.get("name", ""),
                date_str=event["date"],
                grade=event.get("grade")
            )
