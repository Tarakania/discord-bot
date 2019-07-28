import os
import yaml

from typing import Dict, Any


def get_bot_config(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Config file {path} is missing. Example config file is located at config/bot-config.yaml.example"
        )

    with open(path, "r") as f:
        return yaml.load(f, Loader=yaml.SafeLoader)
