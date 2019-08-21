from __future__ import annotations

from contextlib import suppress
from typing import List, Dict, Any, Optional, Iterator, Union

import asyncpg

from rpg.items import Item, Equippable, Weapon, Armor
from rpg.race import Race
from rpg.class_ import Class
from rpg.location import Location

from utils.xp import xp_to_level, level_to_xp


BASE_STAT_VALUE = 10
BASE_ACTION_PONTS_VALUE = 4

LEVEL_TO_STAT_RATIO = 15

VITALITY_TO_HEALTH_RATIO = 20
INTELLIGENCE_TO_MANA_RATIO = 20
AGILITY_TO_ACTION_POINTS_RATIO = 0.1


class ItemNotFound(Exception):
    pass


class ItemAlreadyEquipped(Exception):
    pass


class ItemAlreadyUnequipped(Exception):
    pass


class ItemUnequippable(Exception):
    pass


class UnableToEquip(Exception):
    pass


class NickOrIDUsed(Exception):
    pass


class UnknownPlayer(Exception):
    pass


class PlayerInventory:

    __slots__ = ("_items",)

    def __init__(self, *, items: List[int]):
        self._items: List[Item] = list(Item.from_id(i) for i in items)

    async def from_id(
        cls, discord_id: int, conn: asyncpg.Connection
    ) -> PlayerInventory:
        data = await conn.fetchrow(
            "SELECT inventory FROM players WHERE discord_id = $1", discord_id
        )

        if data is None:
            raise UnknownPlayer

        return cls.from_data(data)

    @classmethod
    def from_data(cls, data: List[int]) -> PlayerInventory:
        return cls(items=data)

    @property
    def size(self) -> int:
        return len(self._items)

    async def add(
        self, item: Union[int, Item], player: Player, pool: asyncpg.Pool
    ) -> Item:
        """Add item to player inventory. Returns added item on success."""

        if isinstance(item, int):
            item = Item.from_id(item)

        self._items.append(item)

        await pool.fetch(
            "UPDATE players SET inventory = $1 WHERE discord_id = $2",
            [i.id for i in self._items],
            player.discord_id,
        )

        return item

    async def remove(
        self, item: Union[int, Item], player: Player, pool: asyncpg.Pool
    ) -> Item:
        """
        Remove item from inventory.
        Returns removed item on success.
        """

        if isinstance(item, int):
            item = Item.from_id(item)

        if item not in self:
            raise ItemNotFound

        self._items.remove(item)

        await pool.fetch(
            "UPDATE players SET inventory = $1 WHERE discord_id = $2",
            [i.id for i in self._items],
            player.discord_id,
        )

        return item

    def __contains__(self, obj: object) -> bool:
        """Check if item is in player's inventory."""

        if isinstance(obj, int):
            item: Item = Item.from_id(obj)
        elif isinstance(obj, Item):
            item = obj
        else:
            return False

        return item in self._items

    def __iter__(self) -> Iterator[Item]:
        """Iterate inventory items."""

        yield from self._items


class PlayerEquipmnent:

    # _slots is used to reduce retyping of variables
    _slots = ("weapon", "helmet", "chestplate", "leggings", "boots", "shield")

    __slots__ = _slots

    def __init__(self, **kwargs: Optional[int]):
        # mypy help
        self.weapon: Weapon
        self.helmet: Armor
        self.chestplate: Armor
        self.leggings: Armor
        self.boots: Armor
        self.shield: Armor

        type_map = {
            "weapon": Weapon,
            "helmet": Armor,
            "chestplate": Armor,
            "leggings": Armor,
            "boots": Armor,
            "shield": Armor,
        }

        checked_kwargs = {}
        for name in self._slots:
            instance: Optional[Union[int, Item]] = kwargs.pop(name, None)

            if isinstance(instance, int):
                instance = Item.from_id(instance)

            # make sure include default None values
            checked_kwargs[name] = instance

            if instance is None:
                continue

            cls = type_map[name]

            if not isinstance(instance, cls):
                raise TypeError(f"{instance} is not an instance of {cls}")

        if kwargs:
            raise ValueError(
                f"Unknown argument(s) passed: {tuple(kwargs.keys())}"
            )

        for name, instance in checked_kwargs.items():
            setattr(self, name, instance)

    async def from_id(
        cls, discord_id: int, pool: asyncpg.Pool
    ) -> PlayerEquipmnent:
        data = await pool.fetchrow(
            "SELECT * FROM equipment WHERE discord_id = $1", discord_id
        )

        if data is None:
            raise UnknownPlayer

        return cls.from_data(data)

    @classmethod
    def from_data(cls, data: Dict[str, Any]) -> PlayerEquipmnent:
        return cls(**{name: data[name] for name in cls._slots})

    @staticmethod
    def can_equip(item: Union[int, Equippable], player: Player) -> bool:
        """Check if item can be equipped."""

        if isinstance(item, int):
            item = Equippable.from_id(item)

        if not isinstance(item, Equippable):
            raise ItemUnequippable

        # TODO: level checks
        return True

    async def equip(
        self, item: Union[int, Equippable], player: Player, pool: asyncpg.Pool
    ) -> Optional[Equippable]:
        """Equip item. Returns replaced item on success."""

        if isinstance(item, int):
            item = Equippable.from_id(item)

        if isinstance(item, Weapon):
            slot_name = "weapon"
        elif isinstance(item, Armor):
            slot_name = item.type
        else:
            raise TypeError(f"Unable to equip {item!r}")

        currently_equipped = getattr(self, slot_name)

        if currently_equipped == item:
            raise ItemAlreadyEquipped

        if not player.can_equip(item):
            raise UnableToEquip

        # f-string is safe here because slot_name is checked against _slots in
        # all scenarios
        await pool.fetch(
            f"UPDATE equipment SET {slot_name} = $1 WHERE discord_id = $2",
            item.id,
            player.discord_id,
        )

        setattr(self, slot_name, item)

        return currently_equipped

    async def unequip(
        self, item: Union[int, Equippable], player: Player, pool: asyncpg.Pool
    ) -> Optional[Equippable]:
        if isinstance(item, int):
            item = Equippable.from_id(item)

        if item not in self:
            raise ItemAlreadyUnequipped

        if isinstance(item, Weapon):
            slot_name = "weapon"
        elif isinstance(item, Armor):
            slot_name = item.type
        else:
            raise TypeError(f"Unable to unequip {item!r}")

        # f-string is safe here because slot_name is checked against _slots in
        # all scenarios
        await pool.fetch(
            f"UPDATE equipment SET {slot_name} = $1 WHERE discord_id = $2",
            None,
            player.discord_id,
        )

        setattr(self, slot_name, None)

        return item

    def __contains__(self, obj: object) -> bool:
        if isinstance(obj, int):
            item: Equippable = Equippable.from_id(obj)
        elif isinstance(obj, Equippable):
            item = obj
        else:
            return False

        return item in self.__iter__()

    def __iter__(self) -> Iterator[Equippable]:
        for name in self._slots:
            item = getattr(self, name)

            if item is not None:
                yield item


class PlayerStats:

    __slots__ = (
        "_player_equipment",
        "_player_level",
        "_will",
        "_agility",
        "_strength",
        "_vitality",
        "_protection",
        "_intelligence",
        "_magic_strength",
        "_mana",
        "_health",
        "_action_points",
        "_modifiers",
        "_modifiers_calculated",
    )

    def __init__(self, equipment: PlayerEquipmnent, level: int):
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
                self._modifiers[k] += v

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

        return BASE_ACTION_PONTS_VALUE + (
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
        equipment: PlayerEquipmnent,
    ):
        self.discord_id = discord_id
        self.nick = nick
        self.race: Race = Race.from_id(race)
        self.class_: Class = Class.from_id(class_)
        self.location: Location = Location.from_id(location)
        self.xp = xp
        self.money = money
        self.inventory = PlayerInventory(items=inventory)
        self.equipment = equipment

        # TODO: pass equipment instead
        self.stats = PlayerStats(self.equipment, self.level)

    @classmethod
    async def create(
        cls,
        pool: asyncpg.Pool,
        discord_id: int,
        nick: str,
        race_id: int,
        class_id: int,
        location_id: Optional[int] = None,
    ) -> Player:

        if location_id is None:
            location_id = race_id

        async with pool.acquire() as conn:
            async with conn.transaction():
                try:
                    player_data = await conn.fetchrow(
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
                except asyncpg.UniqueViolationError:
                    # TODO: parse e.detail to get problematic key or check beforehand
                    raise NickOrIDUsed

                equipment_data = await conn.fetchrow(
                    "INSERT INTO equipment (discord_id) VALUES ($1) RETURNING *",
                    discord_id,
                )

        return cls.from_data(player_data, equipment_data)

    async def delete(self, conn: asyncpg.Connection) -> None:
        deleted = await conn.fetchrow(
            "DELETE FROM players WHERE discord_id = $1 RETURNING true",
            self.discord_id,
        )

        if not deleted:
            raise UnknownPlayer

    @classmethod
    async def from_id(
        cls, discord_id: int, conn: asyncpg.Connection
    ) -> Player:
        player_data = await conn.fetchrow(
            "SELECT * FROM players WHERE discord_id = $1", discord_id
        )

        if player_data is None:
            raise UnknownPlayer

        equipment_data = await conn.fetchrow(
            "SELECT * FROM equipment WHERE discord_id = $1", discord_id
        )

        return cls.from_data(player_data, equipment_data)

    @classmethod
    def from_data(
        cls, player_data: Dict[str, Any], equipment_data: Dict[str, Any]
    ) -> Player:
        equipment = PlayerEquipmnent.from_data(equipment_data)

        return cls(
            discord_id=player_data["discord_id"],
            nick=player_data["nick"],
            race=player_data["race"],
            class_=player_data["class"],
            location=player_data["location"],
            xp=player_data["xp"],
            money=player_data["money"],
            inventory=player_data["inventory"],
            equipment=equipment,
        )

    @property
    def level(self) -> int:
        """Get current level."""

        return xp_to_level(self.xp)

    @property
    def xp_to_next_level(self) -> int:
        """Get amount of xp required to get next level."""

        return level_to_xp(self.level + 1) - self.xp

    async def add_item(self, item: Item, pool: asyncpg.Pool) -> Item:
        """
        Add item to player inventory.
        Returns added item on success.
        """

        if isinstance(item, int):
            item = Item.from_id(item)

        return await self.inventory.add(item, self, pool)

    async def remove_item(self, item: Item, pool: asyncpg.Pool) -> Item:
        """
        Remove item from inventory (preferable) or equipment.
        Returns removed item on success.
        """

        if isinstance(item, int):
            item = Item.from_id(item)

        if item not in self.inventory:
            # prefer removing item from inventory
            if isinstance(item, Equippable):
                with suppress(ItemAlreadyUnequipped):
                    await self.equipment.unequip(item, self, pool)

                    # avoid adding item to inventory and removing it again
                    return item

        return await self.inventory.remove(item, self, pool)

    def can_equip(self, item: Union[int, Equippable]) -> bool:
        """Check if item can be equipped."""

        return self.equipment.can_equip(item, self)

    async def equip_item(
        self, item: Union[int, Equippable], pool: asyncpg.Pool
    ) -> Optional[Equippable]:
        """
        Equip item from inventory to equipment.
        Returns replaced item on success.
        """

        if isinstance(item, int):
            item = Equippable.from_id(item)

        if item in self.equipment:
            raise ItemAlreadyEquipped

        if not self.can_equip(item):
            raise UnableToEquip

        await self.inventory.remove(item, self, pool)
        unequipped = await self.equipment.equip(item, self, pool)

        if unequipped is not None:
            await self.inventory.add(unequipped, self, pool)

        return unequipped

    async def unequip_item(
        self, item: Union[int, Equippable], pool: asyncpg.Pool
    ) -> Item:
        """
        Equip item into player equipment. Returns equipped item on success.
        """

        if isinstance(item, int):
            item = Equippable.from_id(item)

        await self.equipment.unequip(item, self, pool)
        return await self.inventory.add(item, self, pool)

    def __contains__(self, obj: object) -> bool:
        """Check if item is in player's inventory or equipment."""

        if isinstance(obj, int):
            item: Item = Item.from_id(obj)
        elif isinstance(obj, Item):
            item = obj
        else:
            return False

        return item in self.inventory or item in self.equipment

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Player):
            raise NotImplementedError

        return self.discord_id == other.discord_id

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, Player):
            raise NotImplementedError

        return self.discord_id != other.discord_id

    def __str__(self) -> str:
        return self.nick

    def __repr__(self) -> str:
        return f"<Player discord_id={self.discord_id} nick={self.nick} stats={self.stats}>"
