from __future__ import annotations

from typing import List, Dict, Any, Optional

import asyncpg

from .rpg.races import races
from .rpg.classes import classes
from .rpg.locations import locations

from .utils.xp import xp_to_level, level_to_xp


class NickOrIDUsed(Exception):
    pass


class UnknownPlayer(Exception):
    pass


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
    async def create(
        cls,
        conn: asyncpg.Connection,
        discord_id: int,
        nick: str,
        race_id: int,
        class_id: int,
        location_id: Optional[int] = None,
    ) -> Player:

        if location_id is None:
            location_id = race_id

        try:
            data = await conn.fetchrow(
                (
                    "INSERT INTO players (discord_id, nick, race, class, location)"
                    "VALUES ($1, $2, $3, $4, $5) RETURNING *"
                ),
                discord_id,
                nick,
                race_id,
                class_id,
                location_id,
            )
        except asyncpg.UniqueViolationError:  # TODO: parse e.detail to get problematic key or check beforehand
            raise NickOrIDUsed

        return cls.from_data(data)

    async def delete(self, conn: asyncpg.Connection) -> None:
        data = await conn.fetch(
            "DELETE FROM players WHERE discord_id = $1 RETURNING *",
            self.discord_id,
        )

        if data is None:
            raise UnknownPlayer

    @classmethod
    async def from_id(
        cls, discord_id: int, conn: asyncpg.Connection
    ) -> Player:
        data = await conn.fetchrow(
            "SELECT * FROM players WHERE discord_id = $1", discord_id
        )

        if data is None:
            raise UnknownPlayer

        return cls.from_data(data)

    @classmethod
    async def from_nick(cls, nick: str, conn: asyncpg.Connection) -> Player:
        data = await conn.fetchrow(
            "SELECT * FROM players WHERE nick = $1", nick
        )

        if data is None:
            raise UnknownPlayer

        return cls.from_data(data)

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

    def __str__(self) -> str:
        return self.nick

    def __repr__(self) -> str:
        return f"<Player discord_id={self.discord_id} nick={self.nick}>"
