from typing import Any

import git
import discord

from cli import args
from updater import start_updater
from config import get_bot_config
from handler import Handler
from sql import create_pg_connection


TARAKANIA_RPG_ASCII_ART = r""" _____                _               _           __    ___  ___
/__   \__ _ _ __ __ _| | ____ _ _ __ (_) __ _    /__\  / _ \/ _ \
  / /\/ _` | '__/ _` | |/ / _` | '_ \| |/ _` |  / \// / /_)/ /_\/
 / / | (_| | | | (_| |   < (_| | | | | | (_| | / _  \/ ___/ /_\\
 \/   \__,_|_|  \__,_|_|\_\__,_|_| |_|_|\__,_| \/ \_/\/   \____/
"""


class TarakaniaRPG(discord.AutoShardedClient):
    def __init__(self, **kwargs: Any):
        self.args = args

        self.config = get_bot_config(args.config_file)
        self.prefixes = {self.config["default-prefix"]}
        self.owners = set(self.config["owners"])

        self.repo = git.Repo()

        self._handler = Handler(self)

        super().__init__(**kwargs)

    def run(self, *args: Any, **kwargs: Any) -> None:
        if self.args.production:
            token = self.config["discord-token"]
        else:
            token = self.config["discord-beta-token"]

        if not token:
            raise RuntimeError(
                f"Discord {'' if self.args.production else 'beta'}token is missing from config"
            )

        super().run(token, *args, **kwargs)

    async def on_ready(self) -> None:
        await start_updater(self)

        self.pg = await create_pg_connection(self.config["postgresql"])

        await self._handler.load_all_commands()
        await self._handler.prepare_prefixes()

        print(
            f"Running in {'production' if self.args.production else 'debug'} mode"
        )
        print(TARAKANIA_RPG_ASCII_ART)
        print(f"Bot is ready to operate as {self.user}")

    async def on_message(self, msg: discord.Message) -> None:
        await self._handler.process_message(msg)
