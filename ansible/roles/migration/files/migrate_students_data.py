#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, date
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--db-host", required=True)
    parser.add_argument("--db-port", type=int, default=5432)
    parser.add_argument("--db-name", required=True)
    parser.add_argument("--db-user", required=True)
    parser.add_argument("--db-pass", required=True)
    return parser.parse_args()


def parse_date(value):
    if not value:
        return None
    return date.fromisoformat(value)


def main():
    args = parse_args()
    data_dir = Path(args.data_dir)
    users_file = data_dir / "users.json"

    conn = psycopg2.connect(
        host=args.db_host,
        port=args.db_port,
        dbname=args.db_name,
        user=args.db_user,
        password=args.db_pass,
    )
    conn.autocommit = False

    users_count = 0
    students_count = 0
    events_count = 0

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    username VARCHAR(50) PRIMARY KEY,
                    password VARCHAR(255) NOT NULL,
                    role VARCHAR(20) NOT NULL,
                    force_change BOOLEAN DEFAULT FALSE
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS students (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE,
                    display_name VARCHAR(100),
                    avatar VARCHAR(255),
                    created_at TIMESTAMP
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS xp (
                    id SERIAL PRIMARY KEY,
                    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
                    total INTEGER DEFAULT 0,
                    pad_practice INTEGER DEFAULT 0,
                    attendance INTEGER DEFAULT 0,
                    consistency INTEGER DEFAULT 0
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS attendance (
                    id SERIAL PRIMARY KEY,
                    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
                    date DATE NOT NULL,
                    grade DOUBLE PRECISION
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS streaks (
                    id SERIAL PRIMARY KEY,
                    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
                    current INTEGER DEFAULT 0,
                    longest INTEGER DEFAULT 0,
                    last_practice_date DATE
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS history_events (
                    id SERIAL PRIMARY KEY,
                    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
                    type VARCHAR(20) NOT NULL,
                    name VARCHAR(255),
                    date DATE NOT NULL,
                    grade DOUBLE PRECISION
                );
                """
            )

            cur.execute("TRUNCATE history_events, attendance, streaks, xp, students, users RESTART IDENTITY CASCADE")

            if users_file.exists():
                users_data = json.loads(users_file.read_text(encoding="utf-8"))
                user_rows = [
                    (
                        username,
                        payload.get("password", ""),
                        payload.get("role", "student"),
                        payload.get("force_change", False),
                    )
                    for username, payload in users_data.items()
                ]
                if user_rows:
                    execute_values(
                        cur,
                        "INSERT INTO users (username, password, role, force_change) VALUES %s",
                        user_rows,
                    )
                    users_count = len(user_rows)

            for student_dir in data_dir.iterdir():
                if not student_dir.is_dir():
                    continue
                stats_file = student_dir / "stats.json"
                if not stats_file.exists():
                    continue

                stats = json.loads(stats_file.read_text(encoding="utf-8"))
                username = student_dir.name
                profile = stats.get("profile", {})
                xp_data = stats.get("xp", {})
                categories = xp_data.get("categories", {})
                streak = stats.get("streak", {})
                attendance_data = stats.get("attendance", {})
                history_events = stats.get("history", {}).get("events", [])

                cur.execute(
                    """
                    INSERT INTO students (username, display_name, avatar, created_at)
                    VALUES (%s, %s, %s, %s) RETURNING id
                    """,
                    (
                        username,
                        profile.get("name", username),
                        profile.get("avatar", ""),
                        datetime.utcnow(),
                    ),
                )
                student_id = cur.fetchone()[0]
                students_count += 1

                cur.execute(
                    """
                    INSERT INTO xp (student_id, total, pad_practice, attendance, consistency)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        student_id,
                        xp_data.get("total", 0),
                        categories.get("pad_practice", 0),
                        categories.get("attendance", 0),
                        categories.get("consistency", 0),
                    ),
                )

                cur.execute(
                    """
                    INSERT INTO streaks (student_id, current, longest, last_practice_date)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        student_id,
                        streak.get("current", 0),
                        streak.get("longest", 0),
                        parse_date(streak.get("last_practice_date")),
                    ),
                )

                attendance_rows = [
                    (student_id, parse_date(date_str), None)
                    for date_str in attendance_data.get("dates", [])
                    if date_str
                ]
                if attendance_rows:
                    execute_values(
                        cur,
                        "INSERT INTO attendance (student_id, date, grade) VALUES %s",
                        attendance_rows,
                    )

                history_rows = []
                for event in history_events:
                    event_date = event.get("date")
                    if not event_date:
                        continue
                    history_rows.append(
                        (
                            student_id,
                            event.get("type", "pad"),
                            event.get("name", ""),
                            parse_date(event_date),
                            event.get("grade"),
                        )
                    )
                if history_rows:
                    execute_values(
                        cur,
                        "INSERT INTO history_events (student_id, type, name, date, grade) VALUES %s",
                        history_rows,
                    )
                    events_count += len(history_rows)

        conn.commit()
        print(f"Users migrated: {users_count}")
        print(f"Students migrated: {students_count}")
        print(f"History events migrated: {events_count}")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
