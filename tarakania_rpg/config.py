import os
import sys
import logging

from typing import Any, Dict

import yaml

from constants import DATA_DIR


def get_bot_config(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        log = logging.getLogger(__name__)
        log.fatal(
            f"Config file {os.path.relpath(path)} is missing. "
            f"Example config file is located at {os.path.relpath(DATA_DIR)}"
        )

        sys.exit(1)

    with open(path, "r") as f:
        return yaml.load(f, Loader=yaml.SafeLoader)
