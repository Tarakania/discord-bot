import sentry_sdk

from sentry_sdk.integrations.aiohttp import AioHttpIntegration

from bot import TarakaniaRPG
from cli import args
from rpg import load_objects
from config import get_bot_config
from logger import setup_logger

if __name__ == "__main__":
    config = get_bot_config(args.config_file)

    if args.enable_sentry:
        sentry_sdk.init(
            dsn=config["sentry"]["dsn"],
            integrations=[AioHttpIntegration()],
            debug=not args.production,
        )

    setup_logger(config["logging"])
    load_objects()

    bot = TarakaniaRPG(args, config)
    bot.run()
