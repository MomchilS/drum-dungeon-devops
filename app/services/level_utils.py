# =========================================
# Level utilities (single source of truth)
# =========================================

def required_xp_for_level(level: int) -> int:
    """
    XP required to advance FROM this level to the next.
    Level 1 -> 2 = 100 XP
    Each next level costs +25 XP
    """
    return 100 + (level - 1) * 25


def recalculate_levels(stats: dict) -> None:
    """
    Recalculate level, progress_xp, and xp_to_next
    from stats["xp"]["total"].

    Mutates stats in-place.
    """
    total_xp = stats["xp"]["total"]

    current_level = 1
    remaining_xp = total_xp

    while remaining_xp >= required_xp_for_level(current_level):
        remaining_xp -= required_xp_for_level(current_level)
        current_level += 1

    stats["level"]["current"] = current_level
    stats["level"]["progress_xp"] = remaining_xp
    stats["level"]["xp_to_next"] = (
        required_xp_for_level(current_level) - remaining_xp
    )
