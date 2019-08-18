from cli import args
from config import get_bot_config
from logger import setup_logger
from bot import TarakaniaRPG
from rpg import load_objects


if __name__ == "__main__":
    config = get_bot_config(args.config_file)
    setup_logger(config["logging"])
    load_objects()

    bot = TarakaniaRPG(args, config)
    bot.run()
