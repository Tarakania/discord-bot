from .item import Item
from .equippable import Equippable

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

__all__ = (
    "Item",
    "UnknownItem",
    "Equippable",
    "load_all_items",
    "reload_all_items",
)

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
        item_type._load_objects_from_file(item_type)


def reload_all_items() -> None:
    Item._drop_objects(Item)

    for item_type in _ALL_ITEM_TYPES:
        item_type._load_objects_from_file(item_type)
