import sys
import logging
import argparse

from typing import Any, Dict
from contextlib import suppress

import git
import discord

from sentry_sdk import capture_message

from updater import start_updater
from db.redis import create_redis_pool
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

        self.redis = await create_redis_pool(self.config["redis"])
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

    async def on_message_edit(self, old: discord.Message, new: discord.Message) -> None:
        if old.pinned != new.pinned:
            return

        self._handler.cancel_command(new.id)
        await self._clear_responses(new.id)

        await self._handler.process_message(new)

    async def on_raw_message_edit(self, event: discord.RawMessageUpdateEvent) -> None:
        if "content" not in event.data:  # embed update
            return

        if event.cached_message is not None:  # cached, on_message_edit will be called
            return

        channel = self.get_channel(event.channel_id)
        if channel is None:
            return

        try:
            # might be an issue if bot will get big, global message cache has limited
            # size
            message = await channel.fetch_message(event.message_id)
        except discord.HTTPException:
            return

        # call this ourselves since message was not cached
        #
        # pin/unpin events will trigger this, there is no easy way to fix it
        await self.on_message_edit(message, message)

    async def on_raw_message_delete(self, event: discord.RawMessageDeleteEvent) -> None:
        self._handler.cancel_command(event.message_id)
        await self._clear_responses(event.message_id)

    async def on_error(self, event: str, *args: Any, **kwargs: Any) -> None:
        log.exception(f"Error during event {event} execution")

    async def _clear_responses(self, message_id: int) -> None:
        address = f"message_responses:{message_id}"

        entries = await self.redis.execute("LRANGE", address, 0, -1)
        await self.redis.execute("DEL", address)

        for entry in reversed(entries):
            type_, data = entry.decode().split(":", 1)

            if type_ == "message":
                channel_id, message_id = data.split(":")

                with suppress(discord.HTTPException):
                    await self.http.delete_message(int(channel_id), int(message_id))
            elif type_ == "reaction":
                channel_id, message_id, reaction = data.split(":", 2)

                if reaction.isdigit():
                    e = self.get_emoji(int(reaction))
                    if e is None:
                        continue

                    emote = f"{'a:' if e.animated else ''}{e.name}:{e.id}"
                else:
                    emote = reaction

                with suppress(discord.HTTPException):
                    await self.http.remove_own_reaction(
                        int(channel_id), int(message_id), emote
                    )
            else:
                capture_message(f"Unknown response type: {type_}. Entry: {entry}")
