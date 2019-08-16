from typing import Any, List

from rpg.items import Item


class CraftIngredient(Item):
    config_filename = "craft_ingredients.yaml"

    __slots__ = ("_used_for",)

    def __init__(self, **kwargs: Any):
        self._used_for: List[int] = kwargs.pop("used_for")

        super().__init__(**kwargs)

    @property
    def used_for(self) -> List[Item]:
        return [Item.from_id(i) for i in self._used_for]

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id} name={self.name} used_for={self.used_for}>"
