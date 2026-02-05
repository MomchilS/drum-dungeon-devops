import os
import json
from pathlib import Path
from passlib.context import CryptContext
from app.config import PRACTICE_DATA_DIR

# ------------------------------------------------------------------
# Enforce explicit data directory (no silent fallback)
# ------------------------------------------------------------------

if "PRACTICE_DATA_DIR" not in os.environ:
    raise RuntimeError("PRACTICE_DATA_DIR environment variable is not set")

USERS_FILE = PRACTICE_DATA_DIR / "users.json"

# ------------------------------------------------------------------
# Password hashing configuration
# ------------------------------------------------------------------

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)

# ------------------------------------------------------------------
# User loading helpers
# ------------------------------------------------------------------

def load_users():
    if not USERS_FILE.exists():
        return {}

    with open(USERS_FILE, "r") as f:
        return json.load(f)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# ------------------------------------------------------------------
# User management
# ------------------------------------------------------------------

def update_password(username: str, new_password: str):
    users = load_users()

    if username not in users:
        raise KeyError(f"User '{username}' not found")

    users[username]["password"] = hash_password(new_password)
    users[username]["force_change"] = False

    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def delete_user(username: str):
    users = load_users()

    if username in users:
        del users[username]

        with open(USERS_FILE, "w") as f:
            json.dump(users, f, indent=2)

def add_user(username: str, password: str, role: str, force_change: bool):
    users = load_users()

    hashed_password = hash_password(password)

    users[username] = {
        "password": hashed_password,
        "role": role,
        "force_change": force_change,
    }

    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


DATA_DIR = PRACTICE_DATA_DIR
