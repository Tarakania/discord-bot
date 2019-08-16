from command import BaseCommand, CommandResult
from argparser.arguments import Arguments
from context import Context

from rpg.player import Player, UnknownPlayer


class Command(BaseCommand):
    async def run(self, ctx: Context, args: Arguments) -> CommandResult:
        try:
            player = await Player.from_id(ctx.author.id, ctx.bot.pg)
        except UnknownPlayer:
            return "У вас нет персонажа"

        await player.add_item(args[0], ctx.bot.pg)

        return f"Предмет **{args[0]}** добавлен"
