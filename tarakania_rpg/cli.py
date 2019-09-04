import os
import logging
import argparse

from pathlib import Path

from constants import DATA_DIR

DEFAULT_PORT = "8081"
DEFAULT_HOST = "0.0.0.0"
DEFAULT_CONFIG_PATH = os.sep.join((DATA_DIR, "bot-config.yaml"))

argparser = argparse.ArgumentParser(description="Tarakania RPG discord bot")
argparser.add_argument(
    "--wh-host",
    default=os.environ.get("WH_HOST", DEFAULT_HOST),
    help="Host to run webhook on. Defaults to 0.0.0.0",
)
argparser.add_argument(
    "--wh-port",
    default=os.environ.get("WH_PORT", DEFAULT_PORT),
    help=f"Port to run update webhook on. Defaults to {DEFAULT_PORT}",
)
argparser.add_argument(
    "--config-file",
    type=Path,
    default=Path(DEFAULT_CONFIG_PATH),
    help=f"Path to the config file. Defaults to {DEFAULT_CONFIG_PATH}",
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
argparser.add_argument(
    "--enable-sentry",
    action="store_true",
    help="Enables sentry. Defaults to false in debug mode. Otherwise true",
)


def _verbosity_to_logging_level(string: str) -> int:
    logging_levels = (
        logging.FATAL,
        logging.ERROR,
        logging.WARNING,
        logging.INFO,
        logging.DEBUG,
    )

    value = int(string)

    try:
        return logging_levels[value]
    except IndexError:
        return logging.DEBUG


argparser.add_argument(
    "--verbose",
    "-v",
    action="count",
    default=1,
    help="Verbosity level. Supports stacking (-vvv)",
)

argparser.add_argument(
    "--no-colors", action="store_true", help="Disables console colors"
)

argparser.add_argument("--test-logger", action="store_true", help="Perform logger test")

args = argparser.parse_args()

# конечная обработка аргументов

args.verbose = _verbosity_to_logging_level(args.verbose)


if args.production:
    args.enable_notifications = True
    args.enable_updater = True
    args.enable_sentry = True
