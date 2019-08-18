import os
import re
import traceback
import importlib

from shlex import split
from types import ModuleType
from typing import TYPE_CHECKING, Dict, Optional, Tuple, Set, Pattern

import discord

from . import log
from .command import BaseCommand, CommandResult
from .context import Context
from .arguments import Arguments
from .exceptions import ParserError
from constants import BASE_DIR

if TYPE_CHECKING:
    from bot import TarakaniaRPG

COMMANDS_DIR = os.sep.join((BASE_DIR, "commands"))

PREFIX_REGEX = (
    r"^(?P<prefix>({prefixes}))\s*(?P<command>\w+)(?:\s+(?P<arguments>.+))?$"
)


class CommandCheckError(Exception):
    pass


class Handler:
    def __init__(self, bot: "TarakaniaRPG"):
        self.bot = bot

        self._custom_prefixes: Dict[int, str] = {}
        self._commands: Dict[str, BaseCommand] = {}
        self._imported: Dict[str, ModuleType] = {}

    async def load_command(
        self, command_path: str, raise_on_error: bool = False
    ) -> Optional[BaseCommand]:
        name = command_path.rsplit(os.sep, 1)[1][8:-3]
        module_path = command_path.replace(os.sep, ".")[:-3]

        log.info(f"Loading {name}")
        try:
            imported = importlib.import_module(module_path)
            command = getattr(imported, "Command")(self.bot)
        except Exception:
            log.exception(f"Error loading {name}")

            if raise_on_error:
                raise

            return None

        for alias in command.aliases:
            self._commands[alias] = command

        self._imported[command.name] = imported

        return command

    async def reload_command(
        self, name: str, raise_on_error: bool = False
    ) -> Optional[BaseCommand]:
        imported = self._imported.get(name)
        if imported is None:
            return None

        old_aliases = self._commands[name].aliases

        log.info(f"Reloading {name}")
        try:
            reloaded = importlib.reload(imported)
            command = getattr(reloaded, "Command")(self.bot)
        except Exception:
            log.exception(f"Error reloading {name}")

            if raise_on_error:
                raise

            return None
        finally:
            for alias in old_aliases:
                del self._commands[alias]

        for alias in command.aliases:
            self._commands[alias] = command

        self._imported[name] = reloaded

        return command

    async def load_all_commands(self) -> None:
        commands_found = []

        for path, dirs, files in os.walk(COMMANDS_DIR):
            for f in files:
                if f.startswith("command_") and f.endswith(".py"):
                    full_path = os.sep.join((path, f))
                    relative_path = os.path.relpath(full_path)
                    commands_found.append(
                        os.sep.join(relative_path.split(os.sep)[1:])
                    )

        log.info("Started loading commands")
        for command_path in commands_found:
            await self.load_command(command_path)
        log.info(f"Loaded commands with {len(self._commands)} aliases")

    async def prepare_prefixes(self) -> None:
        bot_id = self.bot.user.id

        prefixes = (
            re.escape(self.bot.config["default-prefix"]),
            f"<@{bot_id}>",
            f"<@!{bot_id}>",
        )

        self._prefixes_regex = re.compile(
            PREFIX_REGEX.format(prefixes="|".join(prefixes)),
            re.IGNORECASE | re.UNICODE,
        )
        self._dm_prefixes_regex = re.compile(
            PREFIX_REGEX.format(prefixes="|".join(prefixes + ("",))),
            re.IGNORECASE | re.UNICODE,
        )

        await self.prepare_custom_prefixes()

        log.debug("Prepareded prefixes")

    async def prepare_custom_prefixes(self) -> None:
        # TODO

        pass

    def separate_prefix(
        self, content: str, guild_id: Optional[int]
    ) -> Tuple[Optional[str], Optional[str], str]:
        """Split content into prefix, command, arguments."""

        def regex_match(
            expr: Pattern[str], content: str
        ) -> Tuple[Optional[str], Optional[str], str]:
            match = expr.search(content)
            if match is None:
                return None, None, content

            return (
                match.group("prefix"),
                match.group("command"),
                match.group("arguments") or "",
            )

        if guild_id is None:
            return regex_match(self._dm_prefixes_regex, content)

        custom_prefix = self._custom_prefixes.get(guild_id)
        if custom_prefix is None:
            return regex_match(self._prefixes_regex, content)

        lower_content = content.lower()
        if lower_content.startswith(custom_prefix):
            command_and_arguments = content[len(custom_prefix) :].split(
                maxsplit=1
            )
            return (
                custom_prefix,
                command_and_arguments[0],
                command_and_arguments[1]
                if len(command_and_arguments) == 2
                else "",
            )

        return None, None, content

    async def process_message(self, msg: discord.Message) -> None:
        if not self._commands:
            return

        if msg.author.bot:
            return

        used_prefix, used_alias, arguments = self.separate_prefix(
            msg.content, msg.guild.id if msg.guild else None
        )
        if used_prefix is None or used_alias is None:
            return

        command = self._commands.get(used_alias)
        if command is None:
            return

        try:
            splitted_args = split(arguments)
        except ValueError:
            # TODO: better help message
            await msg.channel.send(
                "Ошибка разделения аргументов: открытая ковычка"
            )

            return

        args = Arguments(splitted_args)
        ctx = Context(self.bot, msg, command, used_prefix, used_alias)

        try:
            await self.run_command_checks(ctx)
            await args.convert(ctx, command.arguments)
        except (CommandCheckError, ParserError) as e:
            return await self.process_response(
                f"Ошибка при обработке команды **{command.name}**: {e}\n"
                f"Правила вызова команды: `{await command.get_usage(ctx)}`",
                ctx,
            )

        log.debug(
            f"Invoking command {command.name} from {ctx.author.id} in channel {ctx.channel.id}"
        )

        try:
            await self.process_response(await command.run(ctx, args), ctx)
        except Exception:
            log.exception(f"Error calling command {command.name}")

            await self.process_response(
                (
                    f"Ошибка при выполнении команды **{command.name}**:\n"
                    f"```{traceback.format_exc(3)}```"
                ),
                ctx,
            )

    async def run_command_checks(self, ctx: Context) -> None:
        if ctx.command.guild_only and ctx.guild is None:
            raise CommandCheckError(
                "Данную команду можно использовать только на сервере"
            )

        if (
            ctx.command.owner_only
            and ctx.author.id not in self.bot.config["owners"]
        ):
            raise CommandCheckError(
                "Данную команду могут использовать только владельцы бота"
            )

    async def process_response(
        self, response: CommandResult, ctx: Context
    ) -> None:
        if isinstance(response, str):
            await ctx.send(response)
        elif isinstance(response, discord.Message):
            return
        elif response is None:
            return
        else:
            raise TypeError(
                f"Invalid type returned by command {ctx.command.name}: {type(response)}"
            )

    def get_command(self, name: str) -> Optional[BaseCommand]:
        return self._commands.get(name)

    def get_all_commands(self, with_hidden: bool = False) -> Set[BaseCommand]:
        return set(
            c for c in self._commands.values() if not c.hidden or with_hidden
        )
