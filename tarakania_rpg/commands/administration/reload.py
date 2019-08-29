import traceback

from handler import Context, Arguments, CommandResult
from utils.formatting import codeblock


async def run(ctx: Context, args: Arguments) -> CommandResult:
    for command in args:
        try:
            reloaded = await ctx.bot._handler.reload_command(
                args[0].name, raise_on_error=True
            )
        except Exception as e:
            await ctx.send(
                f"Ошибка при перезагрузке **{command.name}**: **{e.__class__.__name__}: {e}**\n"
                f"{codeblock(traceback.format_exc())}"
            )

        assert reloaded is not None

        await ctx.send(f"Перезагружена команда **{reloaded.name}**")

    return None
