from .item import Item, all_items, all_items_by_name, _drop_items  # noqa: F401

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
    Item.read_items_from_file(AlchemyIngredient)
    Item.read_items_from_file(Ammo)
    Item.read_items_from_file(Armor)
    Item.read_items_from_file(Book)
    Item.read_items_from_file(CraftIngredient)
    Item.read_items_from_file(Scroll)
    Item.read_items_from_file(Tool)
    Item.read_items_from_file(Weapon)

    Item.read_items_from_file(Food)
    Item.read_items_from_file(Potion)


def reload_item_configs() -> None:
    _drop_items()
    read_item_configs()


read_item_configs()
