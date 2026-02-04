#!/usr/bin/env python3

import sys
import json
from pathlib import Path

from medals import medal_labels

# ========================
# ARGUMENTS
# ========================
if len(sys.argv) != 2:
    print("Usage: student_stats.py <StudentName>")
    sys.exit(1)

STUDENT = sys.argv[1]

STUDENT_DIR = Path(f"/srv/practice-data/students/{STUDENT}")
STATS_FILE = STUDENT_DIR / "stats.json"

if not STATS_FILE.exists():
    print(f"❌ Student '{STUDENT}' not found.")
    sys.exit(1)

# ========================
# LOAD STATS
# ========================
with open(STATS_FILE, "r") as f:
    stats = json.load(f)

labels = medal_labels()
earned_medals = stats.get("medals", [])

# ========================
# OUTPUT
# ========================
print(f"\n👤 Student: {STUDENT}")
print("-" * 40)

print(f"Level:           {stats['level']['current']}")
print(f"XP:              {stats['xp']['total']}")
print(f"Current streak:  {stats['streak']['current']} days")
print(f"Longest streak:  {stats['streak']['longest']} days")

print("\n🏅 Medals Earned", end="")

if earned_medals:
    print(f" ({len(earned_medals)})")
    for mid in earned_medals:
        name = labels.get(mid, mid)
        print(f"- {name}")
else:
    print("\n(No medals yet)")

print("-" * 40)
