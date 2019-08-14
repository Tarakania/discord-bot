import logging.config

from typing import Any, Dict

from cli import args


LEVEL_TO_COLOR_VALUE = {
    "WARNING": "33",  # yellow
    "ERROR": "31",  # red
    "CRITICAL": "41",  # white on red
}

COLOR_START = "\033["
COLOR_RESET = "\033[0m"

VERBOSE_FORMAT = "%(asctime)s %(levelname)-8s %(name)s %(message)s"
SIMPLE_FORMAT = "%(levelname)-8s %(name)s %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class ColorFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        formatted = super().format(record)

        color_value = LEVEL_TO_COLOR_VALUE.get(record.levelname)
        if color_value is None:
            return formatted

        return f"{COLOR_START}{color_value}m{formatted}{COLOR_RESET}"


def test_logger() -> None:
    print("----- Start logger test -----")

    message = "The quick brown fox jumps over the lazy dog"

    for level in (
        logging.DEBUG,
        logging.INFO,
        logging.WARNING,
        logging.ERROR,
        logging.CRITICAL,
    ):
        logging.log(level, message)

    print("----- End logger test -------")


def setup_logger(logging_config: Dict[str, Any]) -> None:
    LOGGING_CONFIG = {
        "version": 1,
        "formatters": {
            "verbose": {"format": VERBOSE_FORMAT, "datefmt": DATE_FORMAT},
            "simple": {"format": SIMPLE_FORMAT},
            "colorful_verbose": {
                "()": ColorFormatter,
                "format": VERBOSE_FORMAT,
                "datefmt": DATE_FORMAT,
            },
            "colorful_simple": {"()": ColorFormatter, "format": SIMPLE_FORMAT},
        },
        "handlers": {
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "simple",
            },
            "colorful_console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "colorful_simple",
            },
            "file": {
                "level": "ERROR",
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "verbose",
                "filename": logging_config["file"],
                "maxBytes": 10 * 1024 * 1024,
                "backupCount": 1,
            },
        },
        "loggers": {
            "asyncio": {
                "level": "WARNING",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "aiohttp": {
                "level": "WARNING",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "discord": {
                "level": "WARNING",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "websockets": {
                "level": "WARNING",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "git": {
                "level": "WARNING",
                "handlers": ["console", "file"],
                "propagate": False,
            },
        },
        "root": {
            "level": args.verbose,
            "handlers": [
                "console" if args.no_colors else "colorful_console",
                "file",
            ],
        },
        "disable_existing_loggers": False,
    }

    logging.config.dictConfig(LOGGING_CONFIG)

    if args.test_logger:
        test_logger()
