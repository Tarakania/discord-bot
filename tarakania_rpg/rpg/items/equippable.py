from typing import Any, Dict

from . import Item


class Equippable(Item):

    __slots__ = ("modifiers",)

    def __init__(self, **kwargs: Any):
        self.modifiers: Dict[str, int] = kwargs.pop("modifiers", {})

        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id} name={self.name} modifiers={self.modifiers}>"
