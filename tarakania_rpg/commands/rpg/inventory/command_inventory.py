from handler import BaseCommand, Context, Arguments, CommandResult

from rpg.player import Player, UnknownPlayer
from utils.formatting import codeblock


class Command(BaseCommand):
    async def run(self, ctx: Context, args: Arguments) -> CommandResult:
        try:
            player = await Player.from_id(ctx.author.id, ctx.bot.pg)
        except UnknownPlayer:
            return "У вас нет персонажа"

        if not player.inventory.size:
            return "Ваш инвентарь пуст"

        return codeblock("\n".join(str(i) for i in player.inventory))
