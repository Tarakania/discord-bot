import yaml

from typing import Any, Dict


classes: Dict[int, Any] = {}


def load_classes(path: str = "tarakania-rpg/rpg/configs/classes.yaml") -> None:
    with open(path) as f:
        global classes
        classes = yaml.load(f, Loader=yaml.SafeLoader)


load_classes()
