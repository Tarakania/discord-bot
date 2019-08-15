from .item import Item, UnknownItem, _drop_items  # noqa: F401

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


def read_item_configs() -> None:
    for cls in (
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
    ):
        Item.read_items_from_file(cls)


def reload_item_configs() -> None:
    _drop_items()
    read_item_configs()


read_item_configs()
