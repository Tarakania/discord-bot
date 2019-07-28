import json

from bot import TarakaniaRPG


if __name__ == "__main__":
    with open("config.json") as f:
        token = json.load(f)["token"]

    bot = TarakaniaRPG("t!")
    bot.run(token)
