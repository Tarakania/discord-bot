from typing import Any, Dict

from rpg.items import Item


class Armor(Item):
    config_filename = "armor.yaml"

    def __init__(self, **kwargs: Any):
        self.type: str = kwargs.pop("type")
        self.modifiers: Dict[str, int] = kwargs.pop("modifiers", {})

        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id} name={self.name} type={self.type} modifiers={self.modifiers}>"
