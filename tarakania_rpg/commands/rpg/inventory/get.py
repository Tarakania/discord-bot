from handler import Context, Arguments, CommandResult
from utils.command_helpers import get_author_player


async def run(ctx: Context, args: Arguments) -> CommandResult:
    player = await get_author_player(ctx)

    await player.add_item(args[0], ctx.bot.pg)

    return f"Предмет **{args[0]}** добавлен"
