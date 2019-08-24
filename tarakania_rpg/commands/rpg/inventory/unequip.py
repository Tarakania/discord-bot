from handler import Context, Arguments, CommandResult

from rpg.player import Player, UnknownPlayer, ItemAlreadyUnequipped


async def run(ctx: Context, args: Arguments) -> CommandResult:
    try:
        player = await Player.from_id(ctx.author.id, ctx.bot.pg)
    except UnknownPlayer:
        return "У вас нет персонажа"

    try:
        await player.unequip_item(args[0], ctx.bot.pg)
    except ItemAlreadyUnequipped:
        return f"Предмет **{args[0]}** не экипирован"

    return f"Предмет **{args[0]}** снят"
