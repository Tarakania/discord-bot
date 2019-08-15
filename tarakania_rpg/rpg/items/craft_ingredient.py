from typing import Any, List

from rpg.items import Item


class CraftIngredient(Item):
    config_filename = "craft_ingredients.yaml"

    __slots__ = ("used_for",)

    def __init__(self, **kwargs: Any):
        self.used_for: List[int] = kwargs.pop("used_for")

        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id} name={self.name} used_for={self.used_for}>"
