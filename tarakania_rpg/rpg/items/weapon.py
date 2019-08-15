from typing import Any, Optional

from rpg.items import Item


class Weapon(Item):
    config_filename = "weapons.yaml"

    __slots__ = ("damage", "ammo")

    def __init__(self, **kwargs: Any):
        self.damage: str = kwargs.pop("damage")
        self.ammo: Optional[int] = kwargs.pop("ammo", None)

        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id} name={self.name} damage={self.damage} ammo={self.ammo}>"
