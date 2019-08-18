from __future__ import annotations

from typing import Any, Dict, Tuple, TYPE_CHECKING

import discord

from . import log
from .context import Context
from .exceptions import ConvertError
from rpg.rpg_object import UnknownObject
from rpg.items import Item as Item_
from rpg.race import Race as Race_
from rpg.class_ import Class as Class_
from rpg.location import Location as Location_
from rpg.player import Player as Player_, UnknownPlayer
from regexes import USER_MENTION_OR_ID_REGEX


if TYPE_CHECKING:
    from .command import BaseCommand


class _ConverterMeta(type):
    _converter_name_map: Dict[str, type] = {}

    def __new__(
        mcls, name: str, bases: Tuple[type, ...], dct: Dict[str, Any]
    ) -> type:
        cls = super().__new__(mcls, name, bases, dct)

        type_name = dct.get("type_name")
        if type_name is not None:
            existing = mcls._converter_name_map.get(type_name)
            if existing is not None:
                raise TypeError(
                    f"Duplicate name in {type_name}, defined in {existing.__name__}"
                )
            mcls._converter_name_map[type_name] = cls

        return cls

    @classmethod
    def _get_converter_by_name(mcls, name: str) -> type:
        argument = mcls._converter_name_map.get(name)
        if argument is not None:
            return argument

        log.warning(
            f"Warning: no mathing argument for type {name}. Falling back to String"
        )

        return String


# TODO: a way to subclass conventer with actual class defining convert function
class Converter(metaclass=_ConverterMeta):
    type_name = ""

    @classmethod
    def new(cls, data: Dict[str, Any]) -> Converter:
        type_name = data["type"]

        return type(cls)._get_converter_by_name(type_name)(data)

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

    def get_usage(self) -> str:
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

    def __str__(self) -> str:
        return self.type_name

    def __repr__(self) -> str:
        return f"<Converter name={self.type_name} display_name={self.display_name} default_value={self.default_value}>"


class String(Converter):
    type_name = "string"

    async def convert(self, ctx: Context, value: str) -> str:
        return value


class Number(Converter):
    type_name = "number"

    async def convert(self, ctx: Context, value: str) -> float:
        return float(value)


class Integer(Converter):
    type_name = "integer"

    async def convert(self, ctx: Context, value: str) -> int:
        return int(value)


class Command(Converter):
    type_name = "command"

    async def convert(self, ctx: Context, value: str) -> "BaseCommand":
        command = ctx.bot._handler.get_command(value.lower())
        if command is None:
            raise ConvertError(value, self, "Такой команды не существует")

        return command


class Player(Converter):
    type_name = "player"

    async def convert(self, ctx: Context, value: str) -> Player_:
        try:
            return await Player_.from_nick(value, ctx.bot.pg)
        except UnknownPlayer:
            raise ConvertError(value, self, "Игрок с таким ником не найден")


class Item(Converter):
    type_name = "item"

    async def convert(self, ctx: Context, value: str) -> Item_:
        try:
            if value.isdigit():
                return Item_.from_id(int(value))

            return Item_.from_name(value.lower().replace("-", " "))
        except UnknownObject:
            raise ConvertError(
                value, self, "Такой предмет не существует найден"
            )


class Race(Converter):
    type_name = "race"

    async def convert(self, ctx: Context, value: str) -> Race_:
        try:
            if value.isdigit():
                return Race_.from_id(int(value))

            return Race_.from_name(value.lower().replace("-", " "))
        except UnknownObject:
            raise ConvertError(value, self, "Такой расы не существует")


class Class(Converter):
    type_name = "class"

    async def convert(self, ctx: Context, value: str) -> Class_:
        try:
            if value.isdigit():
                return Class_.from_id(int(value))

            return Class_.from_name(value.lower().replace("-", " "))
        except UnknownObject:
            raise ConvertError(value, self, "Такой класс не существует")


class Location(Converter):
    type_name = "location"

    async def convert(self, ctx: Context, value: str) -> Location_:
        try:
            if value.isdigit():
                return Location_.from_id(int(value))

            return Location_.from_name(value.lower().replace("-", " "))
        except UnknownObject:
            raise ConvertError(value, self, "Такой локация не существует")


class User(Converter):
    type_name = "user"

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
