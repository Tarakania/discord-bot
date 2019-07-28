from config import get_bot_config
from bot import TarakaniaRPG


if __name__ == "__main__":
    bot = TarakaniaRPG(get_bot_config("config/bot-config.yaml"))
    bot.run()
