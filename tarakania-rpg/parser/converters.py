from __future__ import annotations

from typing import Any, Dict, Tuple, TYPE_CHECKING

import discord

from player import Player as Player_
from context import Context
from parser.exceptions import ConvertError
from sql import get_player_info_by_nick
from regexes import USER_MENTION_OR_ID_REGEX


if TYPE_CHECKING:
    from command import BaseCommand


class _ConverterMeta(type):
    _name_map: Dict[str, type] = {}

    def __new__(
        mcls, name: str, bases: Tuple[type, ...], dct: Dict[str, Any]
    ) -> type:
        cls = super().__new__(mcls, name, bases, dct)
        if cls.__module__ == mcls.__module__ and name == "ArgumentType":
            pass

        type_name = dct.get("name")
        if type_name is not None:
            existing = mcls._name_map.get(type_name)
            if existing is not None:
                raise TypeError(
                    f"Duplicate name in {type_name}, defined in {existing.__name__}"
                )
            mcls._name_map[type_name] = cls

        return cls

    @classmethod
    def get_argument_by_name(mcls, name: str) -> type:
        argument = mcls._name_map.get(name)
        if argument is not None:
            return argument

        print(
            f"Warning: no mathing argument for type {name}. Falling back to String"
        )

        return String


class Converter(metaclass=_ConverterMeta):
    name = ""

    @classmethod
    def new(cls, data: Dict[str, Any]) -> Converter:
        type_name = data["type"]

        return type(cls).get_argument_by_name(type_name)(data)

    def __init__(self, data: Dict[str, Any]):
        self.display_name = data.get("name", data["type"])
        self.optional = data.get("optional", False)
        self.default_value = data.get("default", None)
        self.greedy = data.get("greedy", False)

        if not self.optional and self.default_value is not None:
            raise SyntaxError(
                "Command can not have default value and be not optional at the same time"
            )

    async def convert(self, ctx: Context, value: str) -> Any:
        raise NotImplementedError

    def __str__(self) -> str:
        extra_markers = ""
        if self.greedy:
            extra_markers += "..."

        if self.default_value is not None:
            extra_markers += f"={self.default_value}"

        return (
            f"[{self.display_name}{extra_markers}]"
            if self.optional
            else f"<{self.display_name}{extra_markers}>"
        )

    def __repr__(self) -> str:
        return f"<Converter name={self.name} display_name={self.display_name} default_value={self.default_value}>"


class String(Converter):
    name = "string"

    async def convert(self, ctx: Context, value: str) -> str:
        return value


class Number(Converter):
    name = "number"

    async def convert(self, ctx: Context, value: str) -> float:
        return float(value)


class Integer(Converter):
    name = "integer"

    async def convert(self, ctx: Context, value: str) -> int:
        return int(value)


class Command(Converter):
    name = "command"

    async def convert(self, ctx: Context, value: str) -> "BaseCommand":
        command = ctx.bot._handler.get_command(value.lower())
        if command is None:
            raise ConvertError(value, self, "Такой команды не существует")

        return command


class Player(Converter):
    name = "player"

    async def convert(self, ctx: Context, value: str) -> Player_:
        data = await get_player_info_by_nick(ctx.bot.pg, value)
        if data is None:
            raise ConvertError(value, self, "Игрок с таким ником не найден")

        return Player_.from_data(data)


class User(Converter):
    name = "user"

    async def convert(self, ctx: Context, value: str) -> discord.User:
        user = None
        id_match = USER_MENTION_OR_ID_REGEX.fullmatch(value)

        if id_match is not None:
            user_id = int(id_match.group(1) or id_match.group(0))
            if ctx.guild is not None:
                user = ctx.guild.get_member(user_id)
            if user is None:
                # double check of ctx.guild, but we need to ensure we won't
                # get member object from other guild by accident
                for guild in ctx.bot.guilds or []:
                    user = guild.get_member(user_id)
                    if user is not None:
                        break

            if user is None:
                try:
                    user = await ctx.bot.fetch_user(user_id)
                except discord.NotFound:
                    pass

        if user is not None:
            return user

        if ctx.guild is None:
            return None

        found = []
        pattern = value.lower()

        for member in ctx.guild.members:
            match_pos = -1
            if member.nick is not None:
                match_pos = member.nick.lower().find(pattern)
            if match_pos == -1:
                match_pos = f"{member.name.lower()}#{member.discriminator}".find(
                    pattern
                )
            if match_pos == -1:
                continue
            found.append((member, match_pos))

        found = list(set(found))
        found.sort(
            key=lambda x: (
                # last member message timestamp, lower delta is better
                # TODO?
                # index of match in string, smaller value is better
                -x[1],
                # member status, not 'offline' is better
                str(x[0].status) != "offline",
                # guild join timestamp, lower delta is better
                x[0].joined_at,
            ),
            reverse=True,
        )

        if found:
            return found[0][0]

        raise ConvertError(value, self, "Пользователь не найден")
