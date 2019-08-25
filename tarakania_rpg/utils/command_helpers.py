from rpg.player import Player, UnknownPlayer
from handler.command import StopCommandExecution
from handler.context import Context


async def get_author_player(
    ctx: Context, error_text: str = "У вас нет персонажа"
) -> Player:
    """Return player object of message author."""

    try:
        return await Player.from_id(ctx.author.id, ctx.bot.pg)
    except UnknownPlayer:
        raise StopCommandExecution(error_text)
