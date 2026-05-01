"""
Database module - completely optional for testing.
Only loads when MariaDB is available.
"""

import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, User, Student, XP, Attendance, Streak, HistoryEvent

# Initialize all variables to None by default - NO database operations during import
DB_AVAILABLE = False
engine = None
SessionLocal = None

logger = logging.getLogger(__name__)

def _build_database_url():
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        return database_url

    db_host = os.environ.get("DB_HOST")
    db_port = os.environ.get("DB_PORT", "5432")
    db_name = os.environ.get("DB_NAME")
    db_user = os.environ.get("DB_USER")
    db_pass = os.environ.get("DB_PASS")

    if all([db_host, db_name, db_user, db_pass]):
        return f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

    return None


def _load_database():
    """Load database components only when explicitly called."""
    global DB_AVAILABLE, engine, SessionLocal

    if DB_AVAILABLE:  # Already loaded
        return

    try:
        # Prefer DATABASE_URL, fallback to DB_* environment variables
        DATABASE_URL = _build_database_url()
        
        if not DATABASE_URL:
            logger.warning("DATABASE_URL environment variable not set. Running in JSON-only mode.")
            DB_AVAILABLE = False
            return

        # Create engine with connection pooling
        engine = create_engine(
            DATABASE_URL,
            echo=False,  # Set to True for SQL debugging
            pool_size=10,           # Connections per instance
            max_overflow=20,        # Extra connections
            pool_pre_ping=True,     # Verify connections before using
            pool_recycle=3600       # Recycle connections after 1 hour
        )
        
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        # Test connection by creating tables
        Base.metadata.create_all(bind=engine)
        DB_AVAILABLE = True
        logger.info("Database connection successful!")

    except Exception as e:
        # Print error for debugging (logger might not be configured)
        print(f"Warning: Database not available: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        logger.warning(f"Database not available: {e}")
        logger.warning("Running in JSON-only mode for testing")
        DB_AVAILABLE = False

def get_db():
    """FastAPI dependency for database sessions."""
    if not DB_AVAILABLE or SessionLocal is None:
        # Return a dummy generator when DB is not available
        return iter([])
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Export models for use in other modules
__all__ = [
    "DB_AVAILABLE",
    "engine",
    "SessionLocal",
    "Base",
    "User",
    "Student",
    "XP",
    "Attendance",
    "Streak",
    "HistoryEvent",
    "_load_database",
    "get_db"
]
