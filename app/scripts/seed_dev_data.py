import os
import sys
from pathlib import Path

from auth import add_user, load_users

# ------------------------------------------------------------------
# Safety checks
# ------------------------------------------------------------------

ENV = os.getenv("ENV", "dev")
if ENV == "prod":
    raise RuntimeError("seed_dev_data.py must not be run in production")

def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"{name} environment variable must be set")
    return value

DATA_DIR = Path(require_env("PRACTICE_DATA_DIR")).resolve()
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------------
# Seed data
# ------------------------------------------------------------------

ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

STUDENTS = [
    ("student1", "student123"),
    ("student2", "student123"),
]

# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------

def main():
    print("Seeding dev data...")

    users = load_users()

    if ADMIN_USER not in users:
        add_user(
            username=ADMIN_USER,
            password=ADMIN_PASS,
            role="admin",
            force_change=False,
        )
        print(f"Created admin user '{ADMIN_USER}'")
    else:
        print(f"Admin user '{ADMIN_USER}' already exists")

    for username, password in STUDENTS:
        if username not in users:
            add_user(
                username=username,
                password=password,
                role="student",
                force_change=False,
            )
            print(f"Created student '{username}'")
        else:
            print(f"Student '{username}' already exists")

    print("Done.")

if __name__ == "__main__":
    main()