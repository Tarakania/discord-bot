from __future__ import annotations

from typing import List, Dict, Any

from rpg.races import races
from rpg.classes import classes
from rpg.locations import locations

from utils.xp import xp_to_level, level_to_xp


class Player:
    def __init__(
        self,
        *,
        discord_id: int,
        nick: str,
        race: int,
        class_: int,
        location: int,
        xp: int,
        money: int,
        inventory: List[int],
    ):
        self.discord_id = discord_id
        self.nick = nick
        self.race = races[race]
        self.class_ = classes[class_]
        self.location = locations[location]
        self.xp = xp
        self.money = money
        self.inventory = inventory

    @classmethod
    def from_data(cls, data: Dict[str, Any]) -> Player:
        return cls(
            discord_id=data["discord_id"],
            nick=data["nick"],
            race=data["race"],
            class_=data["class"],
            location=data["location"],
            xp=data["xp"],
            money=data["money"],
            inventory=data["inventory"],
        )

    @property
    def level(self) -> int:
        return xp_to_level(self.xp)

    @property
    def xp_to_next_level(self) -> int:
        return level_to_xp(self.level + 1) - self.xp
