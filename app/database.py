"""
Database module - completely optional for testing.
Only loads when MariaDB is available.
"""

# Initialize all variables to None by default - NO database operations during import
DB_AVAILABLE = False
engine = None
SessionLocal = None
Base = None
User = None
Student = None
XP = None
Attendance = None
Streak = None
HistoryEvent = None

def _load_database():
    """Load database components only when explicitly called."""
    global DB_AVAILABLE, engine, SessionLocal, Base, User, Student, XP, Attendance, Streak, HistoryEvent

    if DB_AVAILABLE:  # Already loaded
        return

    try:
        from app.config import ENV
        import os
        from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, Float, Text, ForeignKey, DateTime
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import sessionmaker, relationship

        # Database URL based on environment
        if ENV == "local":
            DATABASE_URL = "mysql+pymysql://root:Naruto6767momo@localhost/drum_dungeon"
        else:
            DATABASE_URL = os.environ.get("DATABASE_URL", "mysql+pymysql://user:pass@db/drum_dungeon")

        engine = create_engine(DATABASE_URL, echo=True)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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

        # Test connection by creating tables
        Base.metadata.create_all(bind=engine)
        DB_AVAILABLE = True
        print("Database connection successful!")

    except Exception as e:
        print(f"Warning: Database not available: {e}")
        print("Running in JSON-only mode for testing")
        DB_AVAILABLE = False

def get_db():
    if not DB_AVAILABLE or SessionLocal is None:
        # Return a dummy generator when DB is not available
        return iter([])
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# DO NOT load database on import - only when explicitly called
# _load_database()  # Commented out - only call when needed
