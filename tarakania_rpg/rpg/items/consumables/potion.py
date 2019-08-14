from typing import Any

from rpg.items.consumables import Consumable


class Potion(Consumable):
    config_filename = "consumables/potions.yaml"

    def __init__(self, **kwargs: Any):
        self.duration: int = kwargs.pop("duration", 0)

        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id} name={self.name} duration={self.duration} modifiers={self.modifiers}>"
