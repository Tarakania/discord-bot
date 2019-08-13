import os
import yaml

from typing import Dict, Any

from . import DATA_DIR


def get_bot_config(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Config file {os.path.relpath(path)} is missing. "
            f"Example config file is located at {os.path.relpath(DATA_DIR)}"
        )

    with open(path, "r") as f:
        return yaml.load(f, Loader=yaml.SafeLoader)
