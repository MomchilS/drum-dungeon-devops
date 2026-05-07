import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.database as database
from app.models import Base, User, XP, HistoryEvent
from app.auth import add_user, load_users, update_password, verify_password
from app.services.attendance import apply_attendance
from app.services.data_reader import get_student_stats
from app.services.db_operations import create_or_update_student, initialize_student_records


class PostgresOnlyRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.previous_state = (
            database.DB_AVAILABLE,
            database.engine,
            database.SessionLocal,
        )
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=engine)
        database.DB_AVAILABLE = True
        database.engine = engine
        database.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def tearDown(self):
        database.DB_AVAILABLE, database.engine, database.SessionLocal = self.previous_state

    def test_auth_uses_database_without_users_json(self):
        add_user("student1", "temporary-password", "student", True)

        users = load_users()
        self.assertIn("student1", users)
        self.assertTrue(verify_password("temporary-password", users["student1"]["password"]))

        update_password("student1", "new-password")

        db = database.SessionLocal()
        try:
            user = db.query(User).filter(User.username == "student1").first()
            self.assertIsNotNone(user)
            self.assertFalse(user.force_change)
            self.assertTrue(verify_password("new-password", user.password))
        finally:
            db.close()

    def test_auth_fails_clearly_when_database_unavailable(self):
        database.DB_AVAILABLE = False
        database.SessionLocal = None

        with self.assertRaises(RuntimeError):
            load_users()

    def test_student_attendance_persists_to_database_only(self):
        db = database.SessionLocal()
        try:
            student = create_or_update_student(db, "student1", "Student One", "default.png")
            initialize_student_records(db, student.id)
            db.commit()
        finally:
            db.close()

        apply_attendance("student1", "2026-05-04", grade=9)

        stats = get_student_stats("student1")
        self.assertEqual(stats["xp"]["categories"]["attendance"], 20)
        self.assertEqual(stats["attendance"]["dates"], ["2026-05-04"])

        db = database.SessionLocal()
        try:
            xp = db.query(XP).first()
            history = db.query(HistoryEvent).first()
            self.assertEqual(xp.attendance, 20)
            self.assertEqual(history.type, "attendance")
            self.assertEqual(history.grade, 9)
        finally:
            db.close()


if __name__ == "__main__":
    unittest.main()
