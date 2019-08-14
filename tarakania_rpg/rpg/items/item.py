from __future__ import annotations

import yaml

from typing import Any, Dict, List, Type

from constants import DATA_DIR


all_items: Dict[int, Item] = {}
all_items_by_name: Dict[str, Item] = {}


def _drop_items() -> None:
    global all_items, all_items_by_name

    all_items = {}
    all_items_by_name = {}


class Item:
    config_filename = ""

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

            global all_items, all_items_by_name
            all_items[k] = new_item
            all_items_by_name[new_item.name.lower()] = new_item

            created.append(new_item)

        return created

    @classmethod
    def from_data(cls, data: Dict[str, Any]) -> Item:
        return cls(**data)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id} name={self.name}>"
