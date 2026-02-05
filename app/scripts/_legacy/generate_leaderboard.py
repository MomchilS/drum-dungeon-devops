import os
import json
from pathlib import Path
from datetime import datetime, timezone

# Environment-aware base directory
BASE_DIR = Path(os.environ.get("PRACTICE_DATA_DIR", "/srv/practice-data"))
STUDENTS_DIR = BASE_DIR / "students"
OUTPUT_FILE = BASE_DIR / "leaderboard.json"

students = []

if not STUDENTS_DIR.exists():
    raise RuntimeError(f"Students directory not found: {STUDENTS_DIR}")

for student_dir in STUDENTS_DIR.iterdir():
    if not student_dir.is_dir():
        continue

    stats_file = student_dir / "stats.json"
    if not stats_file.exists():
        continue

    with open(stats_file, "r") as f:
        stats = json.load(f)

    students.append({
        "name": stats["student"],
        "level": stats["level"]["current"],
        "xp_total": stats["xp"]["total"],
        "streak": stats["streak"]["current"],
        "medals": len(stats.get("medals", [])),
    })

# Sort by:
# 1) level desc
# 2) xp_total desc
# 3) streak desc
students.sort(
    key=lambda s: (
        s["level"],
        s["xp_total"],
        s["streak"],
    ),
    reverse=True,
)

leaderboard = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "students": students,
}

with open(OUTPUT_FILE, "w") as f:
    json.dump(leaderboard, f, indent=2)

print("✅ Leaderboard generated")
