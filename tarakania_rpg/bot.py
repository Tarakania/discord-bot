import sys
import logging
import argparse

from typing import Any, Dict

import git
import discord

from updater import start_updater
from db.redis import create_redis_client
from db.postgres import create_pg_connection
from handler.handler import Handler

TARAKANIA_RPG_ASCII_ART = r""" _____                _               _           __    ___  ___
/__   \__ _ _ __ __ _| | ____ _ _ __ (_) __ _    /__\  / _ \/ _ \
  / /\/ _` | '__/ _` | |/ / _` | '_ \| |/ _` |  / \// / /_)/ /_\/
 / / | (_| | | | (_| |   < (_| | | | | | (_| | / _  \/ ___/ /_\\
 \/   \__,_|_|  \__,_|_|\_\__,_|_| |_|_|\__,_| \/ \_/\/   \____/
"""

log = logging.getLogger(__name__)


class TarakaniaRPG(discord.AutoShardedClient):
    def __init__(
        self, cli_args: argparse.Namespace, config: Dict[str, Any], **kwargs: Any
    ):
        self.args = cli_args

        self.config = config
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
            log.fatal(
                f"Discord {'' if self.args.production else 'beta '}token is missing from config"
            )

            sys.exit(1)

        super().run(token, *args, **kwargs)

    async def on_ready(self) -> None:
        await start_updater(self)

        self.redis = await create_redis_client(self.config["redis"])
        self.pg = await create_pg_connection(self.config["postgresql"])

        await self._handler.prepare_prefixes()
        await self._handler.load_all_commands()

        log.info(f"Running in {'production' if self.args.production else 'debug'} mode")

        for line in TARAKANIA_RPG_ASCII_ART.split("\n"):
            log.info(line)

        log.info(
            f"Ready to operate as {self.user}. Prefix: {self.config['default-prefix']}"
        )

    async def on_message(self, msg: discord.Message) -> None:
        await self._handler.process_message(msg)
