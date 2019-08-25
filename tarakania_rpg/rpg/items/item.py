from __future__ import annotations

from typing import Any, List

from ..rpg_object import RPGObject


class Item(RPGObject):
    config_folder = "items/"

    __slots__ = ("craft_amount", "ingredients")

    def __init__(self, **kwargs: Any):
        # for craftable items
        self.craft_amount: int = kwargs.pop("craft_amount", 1)
        self.ingredients: List[int] = kwargs.pop("ingredients", [])

        super().__init__(**kwargs)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Item):
            raise NotImplementedError

        return self.id == other.id

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, Item):
            raise NotImplementedError

        return self.id != other.id

    def __hash__(self) -> int:
        return super().__hash__()
