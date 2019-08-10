import yaml

from typing import Any, Dict


races: Dict[int, Any] = {}


def load_races(path: str = "tarakania-rpg/configs/races.yaml") -> None:
    with open(path) as f:
        global races
        races = yaml.load(f, Loader=yaml.SafeLoader)


load_races()
