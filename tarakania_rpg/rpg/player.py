from __future__ import annotations

from typing import List, Dict, Any, Optional

import asyncpg

from rpg.items import Item
from rpg.races import races
from rpg.classes import classes
from rpg.locations import locations

from utils.xp import xp_to_level, level_to_xp


class NickOrIDUsed(Exception):
    pass


class UnknownPlayer(Exception):
    pass


class PlayerStats:
    def __init__(self, equipment: List[Item]):
        self._items = equipment

        self._health: Optional[int] = None
        self._mana: Optional[int] = None
        self._will: Optional[int] = None
        self._protection: Optional[int] = None
        self._damage: Optional[int] = None
        self._strength: Optional[int] = None
        self._magic_strength: Optional[int] = None

    def _calculate_health(self) -> int:
        # TODO
        return 0

    def _calculate_mana(self) -> int:
        # TODO
        return 0

    def _calculate_will(self) -> int:
        # TODO
        return 0

    def _calculate_protection(self) -> int:
        # TODO
        return 0

    def _calculate_damage(self) -> int:
        # TODO
        return 0

    def _calculate_strength(self) -> int:
        # TODO
        return 0

    def _calculate_magic_strength(self) -> int:
        # TODO
        return 0

    @property
    def health(self) -> int:
        if self._health is None:
            self._health = self._calculate_health()

        return self._health

    @property
    def mana(self) -> int:
        if self._mana is None:
            self._mana = self._calculate_mana()

        return self._mana

    @property
    def will(self) -> int:
        if self._will is None:
            self._will = self._calculate_will()

        return self._will

    @property
    def protection(self) -> int:
        if self._protection is None:
            self._protection = self._calculate_protection()

        return self._protection

    @property
    def damage(self) -> int:
        if self._damage is None:
            self._damage = self._calculate_damage()

        return self._damage

    @property
    def strength(self) -> int:
        if self._strength is None:
            self._strength = self._calculate_strength()

        return self._strength

    @property
    def magic_strength(self) -> int:
        if self._magic_strength is None:
            self._magic_strength = self._calculate_magic_strength()

        return self._magic_strength


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
        self.inventory = [Item.from_id(i) for i in inventory]

        # TODO: pass equipment instead
        self.stats = PlayerStats(self.inventory)

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
