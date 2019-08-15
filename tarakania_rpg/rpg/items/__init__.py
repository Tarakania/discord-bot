from .item import (  # noqa: F401
    Item,
    UnknownItem,
    _load_items_from_file,
    _drop_items,
)

from .alchemy_ingredient import AlchemyIngredient
from .ammo import Ammo
from .armor import Armor
from .book import Book
from .craft_ingredient import CraftIngredient
from .scroll import Scroll
from .tool import Tool
from .weapon import Weapon

from .consumables.food import Food
from .consumables.potion import Potion


_ALL_ITEM_TYPES = (
    AlchemyIngredient,
    Ammo,
    Armor,
    Book,
    CraftIngredient,
    Scroll,
    Tool,
    Weapon,
    Food,
    Potion,
)


def load_all_items() -> None:
    for item_type in _ALL_ITEM_TYPES:
        _load_items_from_file(item_type)


def reload_all_items() -> None:
    for item_type in _ALL_ITEM_TYPES:
        _drop_items(item_type)
        _load_items_from_file(item_type)


load_all_items()
