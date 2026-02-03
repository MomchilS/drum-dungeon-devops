#!/usr/bin/env python3

from medals import check_and_award_medals
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

STUDENT = os.environ.get("STUDENT")

if not STUDENT:
    raise RuntimeError("STUDENT env variable not set")


STATS_FILE = Path(f"/srv/practice-data/students/{STUDENT}/stats.json")

MILESTONES = {
    3: 15,
    7: 15,
    15: 15,
    30: 15,
    45: 15,
    60: 35
}

DAILY_POST_60_BONUS = 5


def today():
    return datetime.now(timezone.utc).date()


def main():
    with open(STATS_FILE) as f:
        stats = json.load(f)

    streak = stats["streak"]
    xp = stats["xp"]

    last_date_raw = streak["last_practice_date"]
    today_date = today()

    if last_date_raw:
        last_date = datetime.strptime(last_date_raw, "%Y-%m-%d").date()
        delta = (today_date - last_date).days

        if delta == 0:
            print("Already logged practice today.")
            return
        elif delta == 1:
            streak["current"] += 1
        else:
            streak["current"] = 1
    else:
        streak["current"] = 1

    streak["last_practice_date"] = today_date.isoformat()
    streak["longest"] = max(streak["longest"], streak["current"])

    awarded_xp = 0
    current_streak = streak["current"]

    if current_streak in MILESTONES:
        milestone_key = f"{current_streak}_day"
        if not stats["milestones"][milestone_key]:
            awarded_xp += MILESTONES[current_streak]
            stats["milestones"][milestone_key] = True

    if current_streak > 60:
        awarded_xp += DAILY_POST_60_BONUS

    if awarded_xp > 0:
        xp["categories"]["consistency"] += awarded_xp
        xp["total"] += awarded_xp

    stats["history"]["last_xp_event"] = "streak"
    stats["history"]["last_updated"] = datetime.now(timezone.utc).isoformat()

    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2)

    print(f"Streak updated: {streak['current']} days (+{awarded_xp} XP)")


if __name__ == "__main__":
    main()
