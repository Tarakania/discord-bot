import time

from datetime import timedelta
from typing import Any

import git
import discord
import asyncpg
import humanize

from sql import (
    create_pg_connection,
    get_player_info_by_nick,
    get_player_info_by_discord_id,
    create_character,
    delete_character,
)
from cli import args
from updater import start_updater
from config import get_bot_config
from utils.xp import xp_to_level, level_to_xp

from races import races
from classes import classes
from locations import locations


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

        self.pg = await create_pg_connection(self.config["postgresql"])

        await self.prepare_prefixes()

        print(
            f"Running in {'production' if self.args.production else 'debug'} mode"
        )
        print(TARAKANIA_RPG_ASCII_ART)
        print(f"Bot is ready to operate as {self.user}")

    async def on_message(self, msg: discord.Message) -> None:  # noqa: C901
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
        elif command == "info":
            if len(args) == 1:
                info = await get_player_info_by_discord_id(
                    self.pg, msg.author.id
                )
                if info is None:
                    await msg.channel.send("У вас нет персонажа")
                    return
            else:
                info = await get_player_info_by_nick(self.pg, args[1])

                if info is None:
                    await msg.channel.send("Персонаж с таким именем не найден")
                    return

            e = discord.Embed(
                title="Информация о персонаже",
                description=f"""Раса: **{races[info["race"]]["name"]}**
Класс: **{classes[info["class"]]["name"]}**
Локация: **{locations[info["location"]]["name"]}**
Уровень: **{xp_to_level(info["xp"])}**
Опыта до следующего уровня: **{level_to_xp(xp_to_level(info["xp"]) + 1) - info["xp"]}**
Деньги: **{info["money"]}**
Размер инвентаря: **{len(info["inventory"])}**""",
            )
            e.set_author(name=info["nick"])

            await msg.channel.send(embed=e)

        elif command == "delete":
            await delete_character(self.pg, msg.author.id)
            await msg.channel.send("Ваш персонаж удалён")
        elif command == "register":
            try:
                nick, race, class_ = args[1:]
            except ValueError:
                await msg.channel.send(
                    "Недостаточно аргументов.\nВведите имя, расу и класс персонажа"
                )
                return

            if not (1 <= len(nick) <= 128):
                await msg.channel.send(
                    f"Имя персонажа должно быть в пределах от **1** до **128** символов.\nВы ввели **{len(nick)}**"
                )

            is_race_valid = False
            for race_id, r in races.items():
                if r["name"] == race:
                    is_race_valid = True
                    break

            if not is_race_valid:
                await msg.channel.send(
                    f"Выберите название расы из: **{', '.join(i['name'] for i in races.values())}**"
                )
                return

            is_class_valid = False
            for class_id, c in classes.items():
                if c["name"] == class_:
                    is_class_valid = True
                    break

            if not is_class_valid:
                await msg.channel.send(
                    f"Выберите название класса из: **{', '.join(i['name'] for i in classes.values())}**"
                )
                return

            try:
                await create_character(
                    self.pg, msg.author.id, nick, race_id, class_id
                )
            except asyncpg.UniqueViolationError:  # TODO: parse e.detail to get problematic key or check beforehand
                await msg.channel.send(
                    "Персонаж с таким именем уже существует или у вас уже есть персонаж"
                )
                return

            await msg.channel.send("Персонаж создан")
