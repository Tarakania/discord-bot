import traceback

from ..command import BaseCommand, CommandResult
from ..parser.arguments import Arguments
from ..context import Context
from ..utils.formatting import codeblock


class Command(BaseCommand):
    async def run(self, ctx: Context, args: Arguments) -> CommandResult:
        for command in args:
            try:
                reloaded = await self.bot._handler.reload_command(args[0].name)
            except Exception as e:
                await ctx.send(
                    f"Ошибка при перезагрузке **{command.name}**: **{e.__class__.__name__}: {e}**\n"
                    f"{codeblock(traceback.format_exc())}"
                )

            assert reloaded is not None

            await ctx.send(f"Перезагружена команда **{reloaded.name}**")

        return None
