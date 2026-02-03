#!/usr/bin/env python3

import os
import json
from pathlib import Path

#LEADERBOARD_FILE = Path("/srv/practice-data/leaderboard.json")

if "PRACTICE_DATA_DIR" not in os.environ:
    print("PRACTICE_DATA_DIR not set")
    exit(1)

BASE_DIR = Path(os.environ["PRACTICE_DATA_DIR"])
LEADERBOARD_FILE = BASE_DIR / "leaderboard.json"

if not LEADERBOARD_FILE.exists():
    print(" Leaderboard file not found.")
    print("Run generate_leaderboard.py first.")
    exit(1)

with open(LEADERBOARD_FILE, "r") as f:
    leaderboard = json.load(f)

students = leaderboard.get("students", [])

print("\n LEADERBOARD")
print("-" * 40)

if not students:
    print("No students found.")
    exit(0)

for i, s in enumerate(students, start=1):
    flame = "" if s["streak"] >= 3 else ""
    print(
        f"{i:>2}. "
        f"{s['name']:<10} | "
        f"Lv {s['level']:<2} | "
        f"XP {s['xp_total']:<4} | "
        f"Streak {s['streak']:<2} {flame}"
        f"Medals {s.get('medals',0):<2} "
    )

print("-" * 40)
print(f"Last updated: {leaderboard['generated_at']}\n")
