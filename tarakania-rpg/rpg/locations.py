import yaml

from typing import Any, Dict


locations: Dict[int, Any] = {}


def load_locations(
    path: str = "tarakania-rpg/rpg/configs/locations.yaml"
) -> None:
    with open(path) as f:
        global locations
        locations = yaml.load(f, Loader=yaml.SafeLoader)


load_locations()
