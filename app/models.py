"""
Database models for Drum Dungeon application.
Extracted from database.py for better organization.
"""

from sqlalchemy import Column, Integer, String, Boolean, Date, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    username = Column(String(50), primary_key=True, index=True)
    password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # 'admin' or 'student'
    force_change = Column(Boolean, default=False)


class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    display_name = Column(String(100))
    avatar = Column(String(255))
    created_at = Column(DateTime, default=None)


class XP(Base):
    __tablename__ = "xp"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    total = Column(Integer, default=0)
    pad_practice = Column(Integer, default=0)
    attendance = Column(Integer, default=0)
    consistency = Column(Integer, default=0)


class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    date = Column(Date, nullable=False)
    grade = Column(Float)


class Streak(Base):
    __tablename__ = "streaks"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    current = Column(Integer, default=0)
    longest = Column(Integer, default=0)
    last_practice_date = Column(Date)


class HistoryEvent(Base):
    __tablename__ = "history_events"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    type = Column(String(20), nullable=False)  # 'pad' or 'attendance'
    name = Column(String(255))
    date = Column(Date, nullable=False)
    grade = Column(Float)
