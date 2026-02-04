#!/usr/bin/env python3

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone
from collections import defaultdict, Counter

# ========================
# ARGUMENTS
# ========================
if len(sys.argv) != 3:
    print("Usage: performance_summary.py <Student> <average|best-week|difficulty>")
    sys.exit(1)

STUDENT = sys.argv[1]
MODE = sys.argv[2]

STUDENT_DIR = Path(f"/srv/practice-data/students/{STUDENT}")
PERF_FILE = STUDENT_DIR / "performance.json"

if not PERF_FILE.exists():
    print(f"❌ No performance data for {STUDENT}")
    sys.exit(1)

with open(PERF_FILE, "r") as f:
    data = json.load(f)

# ========================
# HELPERS
# ========================
def parse_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)


# ========================
# MODE: AVERAGE BPM INCREASE
# ========================
if MODE == "average":
    for exercise, sessions in data.items():
        if not sessions:
            continue
        diffs = [
            s["end_bpm"] - s["start_bpm"]
            for s in sessions
        ]
        avg = sum(diffs) / len(diffs)
        print(f"{exercise}: +{avg:.1f} BPM average")

# ========================
# MODE: BEST SESSION THIS WEEK
# ========================
elif MODE == "best-week":
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    best = None

    for exercise, sessions in data.items():
        for s in sessions:
            date = parse_date(s["date"])
            if date < cutoff:
                continue
            diff = s["end_bpm"] - s["start_bpm"]
            if not best or diff > best["diff"]:
                best = {
                    "exercise": exercise,
                    "date": s["date"],
                    "diff": diff,
                    "start": s["start_bpm"],
                    "end": s["end_bpm"],
                    "difficulty": s["difficulty"],
                }

    if not best:
        print("No sessions in the last 7 days.")
    else:
        print("Best session last 7 days:")
        print(f"Exercise:   {best['exercise']}")
        print(f"Date:       {best['date']}")
        print(f"BPM jump:   +{best['diff']} ({best['start']} → {best['end']})")
        print(f"Difficulty: {best['difficulty']}")

# ========================
# MODE: DIFFICULTY TRANSITIONS
# ========================
elif MODE == "difficulty":
    difficulty_counts = Counter()
    transitions = Counter()

    for sessions in data.values():
        last = None
        for s in sorted(sessions, key=lambda x: x["date"]):
            diff = s["difficulty"]
            difficulty_counts[diff] += 1
            if last and last != diff:
                transitions[f"{last} → {diff}"] += 1
            last = diff

    print("Difficulty usage:")
    for diff, count in difficulty_counts.items():
        print(f"{diff:13}: {count} sessions")

    if transitions:
        print("\nTransitions:")
        for t, count in transitions.items():
            print(f"{t}: {count} times")
    else:
        print("\nNo difficulty transitions yet.")

else:
    print("❌ Unknown mode")
    sys.exit(1)
