from handler import Context, Arguments, CommandResult
from rpg.player import ItemAlreadyUnequipped
from utils.command_helpers import get_author_player


async def run(ctx: Context, args: Arguments) -> CommandResult:
    player = await get_author_player(ctx)

    try:
        await player.unequip_item(args[0], ctx.bot.pg)
    except ItemAlreadyUnequipped:
        return f"Предмет **{args[0]}** не экипирован"

    return f"Предмет **{args[0]}** снят"
