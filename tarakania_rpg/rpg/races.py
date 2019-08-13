import os
import yaml

from typing import Any, Dict

from .. import DATA_DIR


races: Dict[int, Any] = {}


def load_races(
    path: str = os.sep.join((DATA_DIR, "rpg", "races.yaml"))
) -> None:
    with open(path) as f:
        global races
        races = yaml.load(f, Loader=yaml.SafeLoader)


load_races()
