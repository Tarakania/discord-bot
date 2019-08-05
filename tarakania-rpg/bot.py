import time

from datetime import timedelta
from typing import Any

from sql import connection_db

import git
import discord
import humanize
import asyncpg
import asyncio


from cli import args
from updater import start_updater
from config import get_bot_config

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

    async def prepare_prefixes(self) -> None:
        bot_id = self.user.id
        self.prefixes |= {f"<@{bot_id}>", f"<@!{bot_id}>"}

        print("Prepareded prefixes")

    async def on_ready(self) -> None:
        await start_updater(self)
        await self.prepare_prefixes()

        print(
            f"Running in {'production' if self.args.production else 'debug'} mode"
        )
        print(TARAKANIA_RPG_ASCII_ART)
        print(f"Bot is ready to operate as {self.user}")

    async def on_message(self, msg: discord.Message) -> None:
        used_prefix = None

        for prefix in self.prefixes:
            if msg.content.lower().startswith(prefix):
                used_prefix = prefix
                break

        if used_prefix is None:
            return

        content = msg.content[len(prefix) :]
        args = content.split()
        command = args[0].lower()

        print(
            f"Received command from {msg.author.id} in channel {msg.channel.id}: {command}"
        )

        if command == "ping":
            await msg.channel.send(f"{msg.author.mention}, pong!")
        elif command == "version":
            repo_url = self.repo.remote().url
            commit_date = self.repo.head.object.committed_date
            committer_name = self.repo.head.object.committer.name
            commit_summary = self.repo.head.object.summary
            commit_hash = self.repo.head.object.hexsha

            message = (
                f"Latest commit made {humanize.naturaltime(timedelta(seconds=time.time() - commit_date))} by **{committer_name}**: ```"
                f"{commit_summary}```"
                f"URL: <{repo_url}/commit/{commit_hash}>"
            )

            await msg.channel.send(message)
        elif command == 'info':
            nickname = args[1].lower()
            con = await connection_db(self.config)
            sql = "SELECT*FROM statyPlayers WHERE nickname = '{0}';".format(nickname)
            values = await con.fetchrow(sql)

            message = str(
                "Раса: " + values['race'] +
                "\nКласс: " + values['class'] +
                "\nУровень: " + str(values['level']) +
                "\nОпыт: " + str(values['experience']) +
                "\nОчки действия: " + str(values['actionpoints']) +
                "\nСила: " + str(values['force']) +
                "\nСила магии: " + str(values['forcemagic'])+
                "\nЛовкость: " + str(values['agility']) +
                "\nБроня: " + str(values['armor']) +
                "\nМана: " + str(values['mana']) +
                "\nЗдоровье: " + str(values['health']) +
                "\nДеньги: " + str(values['money'])
            )

            await msg.channel.send(message)


