import traceback

from command import BaseCommand, CommandResult
from parser.arguments import Arguments
from context import Context


class Command(BaseCommand):
    async def run(self, ctx: Context, args: Arguments) -> CommandResult:
        try:
            command = await self.bot._handler.reload_command(args[0].name)
        except Exception as e:
            return (
                f"Ошибка при перезагрузке: **{e.__class__.__name__}: {e}**\n"
                f"```{traceback.format_exc()}```"
            )

        assert command is not None

        return f"Перезагружена команда **{command.name}**"
