from handler import Context, Arguments, CommandResult

from rpg.player import Player, UnknownPlayer


async def run(ctx: Context, args: Arguments) -> CommandResult:
    try:
        player = await Player.from_id(ctx.author.id, ctx.bot.pg)
    except UnknownPlayer:
        return "У вас нет персонажа"

    await player.add_item(args[0], ctx.bot.pg)

    return f"Предмет **{args[0]}** добавлен"
