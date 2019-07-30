import argparse

from pathlib import Path


argparser = argparse.ArgumentParser(description="Tarakania RPG discord bot")
argparser.add_argument(
    "--wh-host",
    default="0.0.0.0",
    help="Host to run webhook on. Defaults to 0.0.0.0",
)
argparser.add_argument(
    "--wh-port",
    default="60000",
    help="Port to run update webhook on. Defaults to 60000",
)
argparser.add_argument(
    "--config-file",
    type=Path,
    default=Path("config/bot-config.yaml"),
    help="Path to the config file. Defaults to config/bot-config.yaml",
)
argparser.add_argument(
    "--production",
    action="store_true",
    help="Run bot in production mode if added. Disables debug functions",
)

args = argparser.parse_args()
