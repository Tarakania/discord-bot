from typing import Any

from rpg.items import Equippable


class Armor(Equippable):
    config_filename = "armor.yaml"

    __slots__ = ("type",)

    def __init__(self, **kwargs: Any):
        self.type: str = kwargs.pop("type")

        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id} name={self.name} type={self.type} modifiers={self.modifiers}>"
