from .item import Item  # isort:skip
from .equippable import Equippable  # isort:skip

from .ammo import Ammo
from .book import Book
from .tool import Tool
from .armor import Armor
from .scroll import Scroll
from .weapon import Weapon
from .consumables.food import Food
from .craft_ingredient import CraftIngredient
from .alchemy_ingredient import AlchemyIngredient
from .consumables.potion import Potion

__all__ = ("Item", "UnknownItem", "Equippable", "load_all_items", "reload_all_items")

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
