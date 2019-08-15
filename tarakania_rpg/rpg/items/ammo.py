from typing import Any, List

from rpg.items import Item


class Ammo(Item):
    config_filename = "ammo.yaml"

    __slots__ = ("used_with",)

    def __init__(self, **kwargs: Any):
        self.used_with: List[int] = kwargs.pop("used_with")

        super().__init__(**kwargs)
