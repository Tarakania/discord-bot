from __future__ import annotations

import yaml

from typing import Any, Dict, List, Type, Optional

from constants import DATA_DIR


_all_items_by_id: Dict[int, Item] = {}
_all_items_by_name: Dict[str, Item] = {}


def _drop_items(item_type: Optional[Type[Item]] = None) -> None:
    global _all_items_by_id, _all_items_by_name

    if item_type is None:
        _all_items_by_id = {}
        _all_items_by_name = {}

        return

    for item in _all_items_by_id.values():
        del _all_items_by_id[item.id]
        del _all_items_by_name[item.name]


def _read_items_from_file(item_type: Type[Item]) -> Dict[int, Any]:
    with open(f"{DATA_DIR}/rpg/items/{item_type.config_filename}") as f:
        item_data = yaml.safe_load(f)

    if item_data is None:  # empty config
        return {}

    for k, v in item_data.items():
        v["id"] = k

    return item_data


def _load_items_from_file(item_type: Type[Item]) -> List[Item]:
    items_data = _read_items_from_file(item_type)

    created: List[Item] = []

    for id, data in items_data.items():
        new_item = item_type.from_data(data)

        global _all_items_by_id, _all_items_by_name
        _all_items_by_id[id] = new_item
        _all_items_by_name[new_item.name.lower()] = new_item

        created.append(new_item)

    return created


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
                f"Unknown kwarg(s) passed from {self.__class__.__name__}: {tuple(kwargs.keys())}"
            )

    @classmethod
    def from_data(cls, data: Dict[str, Any]) -> Item:
        return cls(**data)

    @classmethod
    def from_id(cls, id: int) -> Item:
        try:
            return _all_items_by_id[id]
        except KeyError:
            raise UnknownItem(f"Item with id {id} not found")

    @classmethod
    def from_name(cls, name: str) -> Item:
        try:
            return _all_items_by_name[name]
        except KeyError:
            raise UnknownItem(f"Item with name {name} not found")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Item):
            raise NotImplementedError

        return self.id == other.id

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, Item):
            raise NotImplementedError

        return self.id != other.id

    def __str__(self) -> str:
        return f"{self.name}[{self.id}]"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id} name={self.name}>"
