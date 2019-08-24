import os
import typing
import importlib

from types import ModuleType
from logging import getLogger

import yaml
import discord

from .context import Context
from .converters import Converter
from .arguments import Arguments

if typing.TYPE_CHECKING:
    from bot import TarakaniaRPG


log = getLogger(__name__)

CommandResult = typing.Union[str, discord.Message, None]


class Command:
    def __init__(self, bot: "TarakaniaRPG", command_path: str) -> None:
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

        self._imported: ModuleType

        self._run_fn: typing.Callable[
            [Context, Arguments], typing.Awaitable[CommandResult]
        ]
        self._init_fn: typing.Callable[[], typing.Awaitable[None]]
        self._unload_fn: typing.Callable[[], typing.Awaitable[None]]

        self._subcommands = typing.Dict[str, typing.Any]

        self.name = command_path.rsplit(os.sep, 1)[-1]
        self._path = command_path

        self._load_configuration()
        self._load_functions()

    def _load_configuration(self) -> None:
        configuration_path = f"{self._path}.yaml"

        log.debug(f"Reading configuration from {configuration_path}")

        with open(configuration_path, encoding="utf8") as f:
            data = yaml.load(f, Loader=yaml.SafeLoader)

        aliases = data.get("aliases", ())
        if isinstance(aliases, str):  # 1 alias
            self.aliases = (self.name, aliases)
        else:
            self.aliases = (self.name, *aliases)

        self.short_help = data.get("short_help")

        if self.short_help is None:
            log.warn(f"No short_help for {self.name}")

            self.short_help = "Описание команды отсутствует"

        self.long_help = data.get("long_help", "")
        self.guild_only = data.get("guild_only", False)
        self.owner_only = data.get("owner_only", False)
        # hidden by default if owner_only is set
        self.hidden = data.get("hidden", self.owner_only)

        self.arguments = []
        for i in data.get("arguments", ()):
            self.arguments.append(Converter.new(i))

    def _load_functions(self) -> None:
        log.debug(f"Loading {self.name} functions")

        module_path = ".".join(self._path.split(os.sep)[1:])

        imported = importlib.import_module(module_path)

        self._run_fn = getattr(imported, "run")
        self._init_fn = getattr(imported, "init", None)
        self._unload_fn = getattr(imported, "unload", None)

        self._imported = imported

    async def get_usage(self, ctx: Context) -> str:
        """Get a formatted usage string."""

        prefix = ctx.local_prefix

        if len(self.aliases) > 1:
            aliases = f"[{'|'.join(self.aliases)}]"
        else:
            aliases = self.aliases[0]

        arguments = " ".join(c.get_usage() for c in self.arguments)

        return f"{prefix}{aliases} {arguments}"

    async def get_help(self, ctx: Context) -> str:
        """Get a formatted help page."""

        usage = await self.get_usage(ctx)

        return f"```\n" f"{usage}\n\n" f"{self.short_help}```"

    async def init(self) -> None:
        if self._init_fn is None:
            return

        await self._init_fn()

    async def unload(self) -> None:
        if self._unload_fn is None:
            return

        await self._unload_fn()

    async def reload(self) -> None:
        await self.unload()

        importlib.reload(self._imported)

        self._load_configuration()
        self._load_functions()

        await self.init()

    async def run(self, ctx: Context, args: Arguments) -> CommandResult:
        if self._run_fn is None:
            return

        # TODO: sybcommand logic
        return await self._run_fn(ctx, args)
