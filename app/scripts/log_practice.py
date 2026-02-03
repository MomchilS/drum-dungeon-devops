#!/usr/bin/env python3

import sys
import json
from pathlib import Path
from datetime import datetime, timezone

# ========================
# ARGUMENTS
# ========================
if len(sys.argv) != 5:
    print("Usage: log_practice.py <Student> <ExerciseName> <StartBPM> <EndBPM>")
    sys.exit(1)

STUDENT = sys.argv[1]
EXERCISE = sys.argv[2]
START_BPM = int(sys.argv[3])
END_BPM = int(sys.argv[4])

BASE_DIR = Path("/srv/practice-data/students")
STUDENT_DIR = BASE_DIR / STUDENT
PERF_FILE = STUDENT_DIR / "performance.json"

if not STUDENT_DIR.exists():
    print(f" Student '{STUDENT}' not found")
    sys.exit(1)

# ========================
# DIFFICULTY LOGIC
# ========================
def get_difficulty(end_bpm: int) -> str:
    if end_bpm <= 90:
        return "easy"
    elif end_bpm <= 140:
        return "intermediate"
    else:
        return "advanced"

difficulty = get_difficulty(END_BPM)

# ========================
# LOAD OR INIT FILE
# ========================
if PERF_FILE.exists():
    with open(PERF_FILE, "r") as f:
        performance = json.load(f)
else:
    performance = {}

# ========================
# APPEND ENTRY
# ========================
entry = {
    "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    "start_bpm": START_BPM,
    "end_bpm": END_BPM,
    "difficulty": difficulty,
}

performance.setdefault(EXERCISE, []).append(entry)

# ========================
# SAVE
# ========================
with open(PERF_FILE, "w") as f:
    json.dump(performance, f, indent=2)

print(
    f" Logged practice: {STUDENT} | {EXERCISE} | "
    f"{START_BPM}→{END_BPM} BPM ({difficulty})"
)
