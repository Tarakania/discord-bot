import sys
import typing

import yaml
import discord

from context import Context
from parser.converters import Converter
from parser.arguments import Arguments

if typing.TYPE_CHECKING:
    from bot import TarakaniaRPG


CommandResult = typing.Union[str, discord.Message, None]


class BaseCommand:
    def __init__(self, bot: "TarakaniaRPG") -> None:
        self.bot = bot

        self.name: str
        self.aliases: typing.Tuple[str, ...]
        self.usage: str
        self.short_help: str
        self.long_help: str
        self.hidden: bool
        self.guild_only: bool
        self.owner_only: bool

        self.arguments: typing.List[Converter]

        self._apply_configuration()

    def _apply_configuration(self) -> None:
        # replace extension from .py to .yaml
        configuration_path = (
            f"{sys.modules[self.__module__].__file__[:-2]}yaml"
        )

        with open(configuration_path) as f:
            data = yaml.load(f, Loader=yaml.SafeLoader)

        self.name = data["name"]

        aliases = data.get("aliases", ())
        if isinstance(aliases, str):  # 1 alias
            self.aliases = (self.name, aliases)
        else:
            self.aliases = (self.name, *aliases)

        self.short_help = data.get("short_help", "Нет информации")
        self.long_help = data.get("long_help", "")
        self.hidden = data.get("hidden", False)
        self.guild_only = data.get("guild_only", False)
        self.owner_only = data.get("owner_only", False)

        self.arguments = []
        for i in data.get("arguments", ()):
            self.arguments.append(Converter.new(i))

    async def get_usage(self, ctx: Context) -> str:
        prefix = ctx.local_prefix

        if len(self.aliases) > 1:
            aliases = f"[{'|'.join(self.aliases)}]"
        else:
            aliases = self.aliases[0]

        arguments = " ".join(str(c) for c in self.arguments)

        return f"{prefix}{aliases} {arguments}"

    async def get_help(self, ctx: Context) -> str:
        usage = await self.get_usage(ctx)

        return f"```\n" f"{usage}\n\n" f"{self.short_help}```"

    async def run(self, ctx: Context, args: Arguments) -> CommandResult:
        raise NotImplementedError
