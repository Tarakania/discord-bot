import math


def xp_to_level(xp: int) -> int:
    return int((math.sqrt(625 + 100 * xp) - 25) / 50)


def level_to_xp(level: int) -> int:
    return 25 * level * (1 + level)
