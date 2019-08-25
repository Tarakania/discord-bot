from handler import Context, Arguments, CommandResult
from rpg.player import (
    ItemNotFound,
    UnableToEquip,
    ItemUnequippable,
    ItemAlreadyEquipped,
)
from utils.command_helpers import get_author_player


async def run(ctx: Context, args: Arguments) -> CommandResult:
    player = await get_author_player(ctx)

    try:
        unequipped = await player.equip_item(args[0], ctx.bot.pg)
    except ItemNotFound:
        return f"В вашем инвентаре нет **{args[0]}**"
    except ItemUnequippable:
        return f"Невозможно экипировать **{args[0]}**"
    except ItemAlreadyEquipped:
        return f"Предмет **{args[0]}** уже экипирован"
    except UnableToEquip:
        return f"Вы не можете экипировать **{args[0]}** в данный момент"

    if unequipped is None:
        return f"Предмет **{args[0]}** экипирован"

    return f"Предмет **{unequipped}** заменён на **{args[0]}**"
