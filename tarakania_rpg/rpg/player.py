from __future__ import annotations

from typing import List, Dict, Any, Optional

import asyncpg

from rpg.items import Item
from rpg.races import races
from rpg.classes import classes
from rpg.locations import locations

from utils.xp import xp_to_level, level_to_xp


BASE_STAT_VALUE = 10

LEVEL_TO_STAT_RATIO = 15

VITALITY_TO_HEALTH_RATIO = 20
INTELLIGENCE_TO_MANA_RATIO = 20
AGILITY_TO_ACTION_POINTS_RATIO = 0.1


class NickOrIDUsed(Exception):
    pass


class UnknownPlayer(Exception):
    pass


class PlayerStats:
    def __init__(self, equipment: List[Item], level: int):
        self._player_equipment = equipment
        self._player_level = level

        # main stats
        self._will: Optional[int] = None
        self._agility: Optional[int] = None
        self._strength: Optional[int] = None
        self._vitality: Optional[int] = None
        self._protection: Optional[int] = None
        self._intelligence: Optional[int] = None
        self._magic_strength: Optional[int] = None

        # secondary stats
        self._mana: Optional[int] = None
        self._health: Optional[int] = None
        self._action_points: Optional[int] = None

        self._modifiers = {
            "will": 0,
            "agility": 0,
            "strength": 0,
            "vitality": 0,
            "protection": 0,
            "intelligence": 0,
            "magic_strength": 0,
            "mana": 0,
            "health": 0,
            "action_points": 0,
        }

        self._modifiers_calculated = False

    def _calculate_modifiers(self) -> None:
        if self._modifiers_calculated:
            return

        for item in self._player_equipment:
            modifiers = getattr(item, "modifiers", None)
            if modifiers is None:
                continue

            for k, v in modifiers.items():
                self._modifiers[k] = self._modifiers[k] + v

        self._modifiers_calculated = True

    def _calculate_will(self) -> int:
        self._calculate_modifiers()

        return (
            BASE_STAT_VALUE
            + LEVEL_TO_STAT_RATIO * self._player_level
            + self._modifiers["will"]
        )

    def _calculate_agility(self) -> int:
        self._calculate_modifiers()

        return (
            BASE_STAT_VALUE
            + LEVEL_TO_STAT_RATIO * self._player_level
            + self._modifiers["agility"]
        )

    def _calculate_strength(self) -> int:
        self._calculate_modifiers()

        return (
            BASE_STAT_VALUE
            + LEVEL_TO_STAT_RATIO * self._player_level
            + self._modifiers["strength"]
        )

    def _calculate_vitality(self) -> int:
        self._calculate_modifiers()

        return (
            BASE_STAT_VALUE
            + LEVEL_TO_STAT_RATIO * self._player_level
            + self._modifiers["vitality"]
        )

    def _calculate_protection(self) -> int:
        self._calculate_modifiers()

        return (
            BASE_STAT_VALUE
            + LEVEL_TO_STAT_RATIO * self._player_level
            + self._modifiers["protection"]
        )

    def _calculate_intelligence(self) -> int:
        self._calculate_modifiers()

        return (
            BASE_STAT_VALUE
            + LEVEL_TO_STAT_RATIO * self._player_level
            + self._modifiers["intelligence"]
        )

    def _calculate_magic_strength(self) -> int:
        self._calculate_modifiers()

        return (
            BASE_STAT_VALUE
            + LEVEL_TO_STAT_RATIO * self._player_level
            + self._modifiers["magic_strength"]
        )

    def _calculate_mana(self) -> int:
        self._calculate_modifiers()

        return (
            self.intelligence * INTELLIGENCE_TO_MANA_RATIO
            + self._modifiers["mana"]
        )

    def _calculate_health(self) -> int:
        self._calculate_modifiers()

        return (
            self.vitality * VITALITY_TO_HEALTH_RATIO
            + self._modifiers["health"]
        )

    def _calculate_action_points(self) -> int:
        self._calculate_modifiers()

        return (
            int(self.agility * AGILITY_TO_ACTION_POINTS_RATIO)
            + self._modifiers["action_points"]
        )

    @property
    def will(self) -> int:
        if self._will is None:
            self._will = self._calculate_will()

        return self._will

    @property
    def agility(self) -> int:
        if self._agility is None:
            self._agility = self._calculate_agility()

        return self._agility

    @property
    def strength(self) -> int:
        if self._strength is None:
            self._strength = self._calculate_strength()

        return self._strength

    @property
    def vitality(self) -> int:
        if self._vitality is None:
            self._vitality = self._calculate_vitality()

        return self._vitality

    @property
    def protection(self) -> int:
        if self._protection is None:
            self._protection = self._calculate_protection()

        return self._protection

    @property
    def intelligence(self) -> int:
        if self._intelligence is None:
            self._intelligence = self._calculate_intelligence()

        return self._intelligence

    @property
    def magic_strength(self) -> int:
        if self._magic_strength is None:
            self._magic_strength = self._calculate_magic_strength()

        return self._magic_strength

    @property
    def mana(self) -> int:
        if self._mana is None:
            self._mana = self._calculate_mana()

        return self._mana

    @property
    def health(self) -> int:
        if self._health is None:
            self._health = self._calculate_health()

        return self._health

    @property
    def action_points(self) -> int:
        if self._action_points is None:
            self._action_points = self._calculate_action_points()

        return self._action_points

    def __repr__(self) -> str:
        return f"<PlayerStats health={self.health} mana={self.mana} action_points={self.action_points}>"


class Player:

    __slots__ = (
        "discord_id",
        "nick",
        "race",
        "class_",
        "location",
        "xp",
        "money",
        "inventory",
        "equipment",
        "stats",
    )

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
        # equipment: List[int]
    ):
        self.discord_id = discord_id
        self.nick = nick
        self.race = races[race]
        self.class_ = classes[class_]
        self.location = locations[location]
        self.xp = xp
        self.money = money
        self.inventory = [Item.from_id(i) for i in inventory]
        # self.equipment = [Item.from_id(i) for i in equipment]

        # TODO: pass equipment instead
        self.stats = PlayerStats(self.inventory, self.level)

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
        return f"<Player discord_id={self.discord_id} nick={self.nick} stats={self.stats}>"
