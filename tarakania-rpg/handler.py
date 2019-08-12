import os
import traceback
import importlib

from types import ModuleType
from typing import TYPE_CHECKING, Dict, Optional, Tuple, Set

import discord

from command import BaseCommand, CommandResult
from context import Context
from parser.arguments import Arguments
from parser.exceptions import ParserError


if TYPE_CHECKING:
    from bot import TarakaniaRPG


class CommandCheckError(Exception):
    pass


class Handler:
    def __init__(self, bot: "TarakaniaRPG"):
        self.bot = bot

        self._default_prefixes: Tuple[str, ...] = ()
        self._default_dm_prefixes: Tuple[str, ...] = ()
        self._custom_prefixes: Dict[int, str] = {}
        self._commands: Dict[str, BaseCommand] = {}
        self._imported: Dict[str, ModuleType] = {}

    async def load_command(
        self, command_path: str, raise_on_error: bool = False
    ) -> Optional[BaseCommand]:
        command_name = command_path.rsplit(os.sep, 1)[1][8:-3]

        try:
            print(f"{command_name + ': ':<20}importing....", end="")
            imported = importlib.import_module(
                command_path.replace(os.sep, ".")[:-3]
            )
            print("creating....", end="")
            command = getattr(imported, "Command")(self.bot)
            print("done")
        except Exception as e:
            print(f"error -> {e.__class__.__name__}: {e}")

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

        try:
            print(f"{name + ': ':<20}reloading....", end="")
            reloaded = importlib.reload(imported)
            print("creating....", end="")
            command = getattr(reloaded, "Command")(self.bot)
            print("done")
        except Exception as e:
            print(f"error -> {e.__class__.__name__}: {e}")

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

        for path, dirs, files in os.walk("tarakania-rpg/commands"):
            for f in files:
                if f.startswith("command_") and f.endswith(".py"):
                    full_path = os.sep.join((path, f))
                    commands_found.append(full_path.split(os.sep, 1)[1])

        print(">>>>> Started loading commands")
        for command_path in commands_found:
            await self.load_command(command_path)

        print("<<<<< Finished loading commands")

    async def prepare_prefixes(self) -> None:
        bot_id = self.bot.user.id
        self._default_prefixes = (
            self.bot.config["default-prefix"],
            f"<@{bot_id}>",
            f"<@!{bot_id}>",
        )
        self._default_dm_prefixes = self._default_prefixes + ("",)

        print("Prepareded prefixes")

    def separate_prefix(
        self, content: str, guild_id: Optional[int]
    ) -> Tuple[Optional[str], str]:
        lower_content = content.lower()

        if guild_id is None:
            prefixes = self._default_dm_prefixes
        else:
            custom_prefix = self._custom_prefixes.get(guild_id)
            if custom_prefix is None:
                prefixes = self._default_prefixes
            else:
                prefixes = (custom_prefix,)

        matched_prefix = None
        for p in prefixes:
            if lower_content.startswith(p):
                matched_prefix = p
                break

        if matched_prefix is None:
            return (None, content)

        return (matched_prefix, content[len(matched_prefix) :])

    async def process_message(self, msg: discord.Message) -> None:
        if msg.author.bot:
            return

        used_prefix, trimmed_content = self.separate_prefix(
            msg.content, msg.guild.id if msg.guild else None
        )

        if used_prefix is None:
            return

        args = Arguments(trimmed_content)

        used_alias = args.command
        if used_alias is None:
            return

        command = self._commands.get(used_alias)
        if command is None:
            return

        ctx = Context(self.bot, msg, used_prefix, used_alias)

        try:
            await self.run_command_checks(command, ctx)
            await args.convert(ctx, command.arguments)
        except (CommandCheckError, ParserError) as e:
            return await self.process_response(
                f"Ошибка при обработке команды **{command.name}**: {e}\n"
                f"Правила вызова команды: `{await command.get_usage(ctx)}`",
                ctx,
            )

        print(
            f"Invoking command {command.name} from {ctx.author.id} in channel {ctx.channel.id}"
        )

        try:
            await self.process_response(await command.run(ctx, args), ctx)
        except Exception:
            await self.process_response(
                (
                    f"Ошибка при выполнении команды **{command.name}**:\n"
                    f"```{traceback.format_exc(3)}```"
                ),
                ctx,
            )

    async def run_command_checks(
        self, command: BaseCommand, ctx: Context
    ) -> None:
        if command.guild_only and ctx.guild is None:
            raise CommandCheckError(
                "Данную команду можно использовать только на сервере"
            )

        if (
            command.owner_only
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
                f"Invalid type returned by command: {type(response)}"
            )

    def get_command(self, name: str) -> Optional[BaseCommand]:
        return self._commands.get(name)

    def get_all_commands(self, with_hidden: bool = False) -> Set[BaseCommand]:
        return set(
            c for c in self._commands.values() if not c.hidden or with_hidden
        )
