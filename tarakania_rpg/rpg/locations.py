import os
import yaml

from typing import Any, Dict

from constants import DATA_DIR


locations: Dict[int, Any] = {}


def load_locations(
    path: str = os.sep.join((DATA_DIR, "rpg", "locations.yaml"))
) -> None:
    with open(path) as f:
        global locations
        locations = yaml.load(f, Loader=yaml.SafeLoader)


load_locations()
