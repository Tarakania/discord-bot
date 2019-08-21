from handler import BaseCommand, Context, Arguments, CommandResult

from rpg.player import Player, UnknownPlayer
from utils.formatting import codeblock


class Command(BaseCommand):
    async def run(self, ctx: Context, args: Arguments) -> CommandResult:
        try:
            player = await Player.from_id(ctx.author.id, ctx.bot.pg)
        except UnknownPlayer:
            return "У вас нет персонажа"

        if player.inventory.size:
            inventory = "\n".join(str(i) for i in player.inventory)
        else:
            inventory = "Ваш инвентарь пуст"

        equipment_item_map = [
            (slot, getattr(player.equipment, slot))
            for slot in player.equipment._slots
        ]

        equipment = "\n".join(
            f"{slot:>10}: {item}" for (slot, item) in equipment_item_map
        )

        return codeblock(
            f"Экипировка:\n\n{equipment}\n\nИнвентарь:\n\n{inventory}"
        )
