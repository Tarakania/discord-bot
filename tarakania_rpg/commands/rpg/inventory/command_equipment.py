from command import BaseCommand, CommandResult
from argparser.arguments import Arguments
from context import Context

from rpg.player import Player, UnknownPlayer
from utils.formatting import codeblock


class Command(BaseCommand):
    async def run(self, ctx: Context, args: Arguments) -> CommandResult:
        try:
            player = await Player.from_id(ctx.author.id, ctx.bot.pg)
        except UnknownPlayer:
            return "У вас нет персонажа"

        item_map = [
            (slot, getattr(player.equipment, slot))
            for slot in player.equipment._slots
        ]

        return codeblock(
            "\n".join(f"{slot}: {item}" for (slot, item) in item_map)
        )
