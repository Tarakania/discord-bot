from __future__ import annotations

import yaml

from typing import Any, Dict, List, Type

from constants import DATA_DIR


_all_items_by_id: Dict[int, Item] = {}
_all_items_by_name: Dict[str, Item] = {}


def _drop_items() -> None:
    global _all_items_by_id, _all_items_by_name

    _all_items_by_id = {}
    _all_items_by_name = {}


class UnknownItem(Exception):
    pass


class Item:
    config_filename = ""

    __slots__ = ("id", "name", "craft_amount", "ingredients")

    def __init__(self, **kwargs: Any):
        self.id: int = kwargs.pop("id")
        self.name: str = kwargs.pop("name")

        # for craftable items
        self.craft_amount: int = kwargs.pop("craft_amount", 1)
        self.ingredients: List[int] = kwargs.pop("ingredients", [])

        if kwargs:
            raise ValueError(
                f"Unknown kwarg(s) passed from {self.__class__.__name__}: {kwargs.keys()}"
            )

    @staticmethod
    def read_items_from_file(cls: Type[Item]) -> List[Item]:
        with open(f"{DATA_DIR}/rpg/items/{cls.config_filename}") as f:
            items = yaml.safe_load(f)

        created: List[Item] = []

        if items is None:  # empty config
            return created

        for k, v in items.items():
            v["id"] = k
            new_item = cls.from_data(v)

            global _all_items_by_id, _all_items_by_name
            _all_items_by_id[k] = new_item
            _all_items_by_name[new_item.name.lower()] = new_item

            created.append(new_item)

        return created

    @classmethod
    def from_data(cls, data: Dict[str, Any]) -> Item:
        return cls(**data)

    @classmethod
    def from_id(cls, id: int) -> Item:
        try:
            return _all_items_by_id[id]
        except IndexError:
            raise UnknownItem(f"Item with id {id} not found")

    @classmethod
    def from_name(cls, name: str) -> Item:
        try:
            return _all_items_by_name[name]
        except IndexError:
            raise UnknownItem(f"Item with name {name} not found")

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id} name={self.name}>"
