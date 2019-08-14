from rpg.player import Player, UnknownPlayer

from command import BaseCommand, CommandResult
from argparser.arguments import Arguments
from context import Context


class Command(BaseCommand):
    async def run(self, ctx: Context, args: Arguments) -> CommandResult:
        try:
            player = await Player.from_id(ctx.author.id, self.bot.pg)
            await player.delete(self.bot.pg)
        except UnknownPlayer:
            return "У вас нет персонажа"

        return "Ваш персонаж удалён"
