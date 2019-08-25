from handler import Context, Arguments, CommandResult

from rpg.player import ItemNotFound
from utils.command_helpers import get_author_player


async def run(ctx: Context, args: Arguments) -> CommandResult:
    player = await get_author_player(ctx)

    try:
        await player.remove_item(args[0], ctx.bot.pg)
    except ItemNotFound:
        return f"В вашем инвентаре нет **{args[0]}**"

    return f"Предмет **{args[0]}** удалён"
