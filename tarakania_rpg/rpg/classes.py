import os
import yaml

from typing import Any, Dict

from constants import DATA_DIR


classes: Dict[int, Any] = {}


def load_classes(
    path: str = os.sep.join((DATA_DIR, "rpg", "classes.yaml"))
) -> None:
    with open(path) as f:
        global classes
        classes = yaml.load(f, Loader=yaml.SafeLoader)


load_classes()
