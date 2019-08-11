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
argparser.add_argument(
    "--enable-notifications",
    action="store_true",
    help="Enables update channel notifications. Defaults to false in debug mode. Otherwise true",
)
argparser.add_argument(
    "--enable-updater",
    action="store_true",
    help="Enables updater. Defaults to false in debug mode. Otherwise true",
)

args = argparser.parse_args()

# конечная обработка аргументов

if args.production:
    args.enable_notifications = True
    args.enable_updater = True
