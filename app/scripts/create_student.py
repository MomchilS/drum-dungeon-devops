#!/usr/bin/env python3

import os
import sys
import shutil
from pathlib import Path
import subprocess
import json

# --------------------------------------------------
# Enforce environment (NO silent fallback)
# --------------------------------------------------

if "PRACTICE_DATA_DIR" not in os.environ:
    print(" PRACTICE_DATA_DIR environment variable is not set", file=sys.stderr)
    sys.exit(1)

BASE_DIR = Path(os.environ["PRACTICE_DATA_DIR"])
STUDENTS_DIR = BASE_DIR / "students"

def log(msg: str):
    print(msg.encode("ascii", errors="replace").decode())

# --------------------------------------------------
# Arguments
# --------------------------------------------------

if len(sys.argv) != 2:
    print("Usage: create_student.py <StudentName>", file=sys.stderr)
    sys.exit(1)

STUDENT = sys.argv[1]
STUDENT_DIR = STUDENTS_DIR / STUDENT

STUDENTS_DIR.mkdir(parents=True, exist_ok=True)

if STUDENT_DIR.exists():
    print(" Student already exists", file=sys.stderr)
    sys.exit(1)

# --------------------------------------------------
# Create directory structure
# --------------------------------------------------

(STUDENT_DIR / "taskwarrior").mkdir(parents=True)
(STUDENT_DIR / "taskwarrior" / "hooks").mkdir(parents=True)

# --------------------------------------------------
# Optional: copy hooks from template student
# --------------------------------------------------

TEMPLATE_STUDENT = STUDENTS_DIR / "Dodko"
TEMPLATE_HOOKS = TEMPLATE_STUDENT / "taskwarrior" / "hooks"

if TEMPLATE_HOOKS.exists():
    shutil.copytree(
        TEMPLATE_HOOKS,
        STUDENT_DIR / "taskwarrior" / "hooks",
        dirs_exist_ok=True
    )
else:
    print("No template hooks found, continuing without them")

# --------------------------------------------------
# Optional: init Taskwarrior DB
# --------------------------------------------------

TASKDATA_DIR = STUDENT_DIR / "taskwarrior"

try:
    subprocess.run(
        ["task", "init"],
        env={**os.environ, "TASKDATA": str(TASKDATA_DIR)},
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
except FileNotFoundError:
    print("Taskwarrior not installed, skipping init")

# --------------------------------------------------
# Optional: copy task definitions from template
# --------------------------------------------------

TEMPLATE_TASKDATA = TEMPLATE_STUDENT / "taskwarrior"

if TEMPLATE_TASKDATA.exists():
    for item in TEMPLATE_TASKDATA.iterdir():
        if item.name in {"data", "taskd", "undo.data"}:
            continue
        if item.is_file():
            shutil.copy(item, TASKDATA_DIR / item.name)
else:
    print("No template taskwarrior data found, continuing")

# --------------------------------------------------
# Create fresh stats.json
# --------------------------------------------------

stats = {
    "student": STUDENT,

    "profile": {
        "avatar": "default.png"
    },

    "xp": {
        "total": 0,
        "categories": {
            "pad_practice": 0,
            "consistency": 0,
            "attendance": 0,
        },
    },
    "level": {
        "current": 1,
        "progress_xp": 0,
        "xp_to_next": 100,
    },
    "streak": {
        "current": 0,
        "longest": 0,
        "last_practice_date": None,
    },
    "attendance": {
        "lifetime_lessons": 0,
        "current_month": {
            "month": None,
            "count": 0,
            "bonus_awarded": False,
        },
    },
    "milestones": {
        "3_day": False,
        "7_day": False,
        "15_day": False,
        "30_day": False,
        "45_day": False,
        "60_day": False,
    },
    "history": {
        "last_xp_event": None,
        "last_updated": None,
    },
}

with open(STUDENT_DIR / "stats.json", "w") as f:
    json.dump(stats, f, indent=2)

print(f" Student created: {STUDENT}")
sys.exit(0)
