# App

This folder contains the Drum Dungeon FastAPI application.

## Purpose

The app provides browser-based admin and student workflows for managing students, attendance, practice progress, XP, streaks, history, and leaderboard data.

## Runtime Model

The current runtime is PostgreSQL-only:

- Auth users are read from and written to PostgreSQL.
- Student profiles, XP, attendance, streaks, and history are stored in PostgreSQL.
- JSON files are not used as a live fallback.
- JSON migration/maintenance scripts are legacy helpers only.

The app expects database and session configuration through environment variables such as `DATABASE_URL`, `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS`, and `SESSION_SECRET_KEY`.

## Key Files and Directories

| Path | Purpose |
| --- | --- |
| `main.py` | FastAPI routes, session middleware, dashboards, health check |
| `auth.py` | Password hashing and user management backed by PostgreSQL |
| `database.py` | SQLAlchemy engine/session initialization and DB availability state |
| `models.py` | SQLAlchemy models for users, students, XP, attendance, streaks, history |
| `services/` | Runtime service logic for attendance, data reads, DB writes, levels, medals |
| `templates/` | Jinja2 HTML templates for login, admin, student, and leaderboard pages |
| `static/` | Static images, avatars, and backgrounds |
| `scripts/` | Admin/bootstrap and legacy maintenance helpers |
| `requirements.txt` | Python runtime dependencies |

## Local Validation

From the repository root:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r app/requirements.txt
python -m compileall app tests
python -m unittest discover -s tests
```

The unit tests use an isolated test database setup and are intended to verify PostgreSQL-only auth and student runtime behavior without touching staging or production.

## Health Check

The app exposes:

```text
/health
```

A healthy runtime returns database connectivity as `connected`. If DB configuration or connectivity is unavailable, the endpoint returns unhealthy status so deployment checks can fail safely.

## Legacy Data Helpers

Scripts related to old JSON data are retained only for explicit maintenance or import/export use. They should not be treated as the active source of truth for the deployed app.
