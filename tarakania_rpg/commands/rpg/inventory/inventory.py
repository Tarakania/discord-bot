from handler import Context, Arguments, CommandResult

from utils.formatting import codeblock
from utils.command_helpers import get_author_player


async def run(ctx: Context, args: Arguments) -> CommandResult:
    player = await get_author_player(ctx)

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
