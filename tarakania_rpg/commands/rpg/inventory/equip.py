from handler import Context, Arguments, CommandResult

from rpg.player import (
    Player,
    UnknownPlayer,
    ItemNotFound,
    ItemUnequippable,
    ItemAlreadyEquipped,
    UnableToEquip,
)


async def run(ctx: Context, args: Arguments) -> CommandResult:
    try:
        player = await Player.from_id(ctx.author.id, ctx.bot.pg)
    except UnknownPlayer:
        return "У вас нет персонажа"

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
