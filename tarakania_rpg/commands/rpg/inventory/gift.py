from handler import Context, Arguments, CommandResult
from utils.confirmations import request_confirmation
from utils.command_helpers import get_author_player


async def run(ctx: Context, args: Arguments) -> CommandResult:
    player = await get_author_player(ctx)

    item = args[0]
    player2 = args[1]

    if len(args) == 2:
        count = 1
    else:
        if args[2] == "all":
            count = player.inventory.get_count(item)
        else:
            count = int(args[2])

    if player == player2:
        return "Нельзя дарить вещи себе"

    from_equipment = False
    if item in player.inventory:
        pass
    elif item in player.equipment:
        from_equipment = True
    else:
        return f"В вашем инвентаре и экипировке нет **{item}**"

    confirmation_request = await ctx.send(
        f"Вы действительно хотите передать **{item}** в количестве **{str(count)}** персонажу **{player2}**?"
    )
    confirmation = await request_confirmation(ctx, confirmation_request)

    if not confirmation:
        return await confirmation_request.edit(
            content="Вы не подтвердили передачу предемета"
        )

    await player.remove_items(item, ctx.bot.pg, count=count)
    await player2.add_items(item, ctx.bot.pg, count=count)

    return await confirmation_request.edit(
        content=(
            f"**{player}** передал **{item}** x **{count}** **{player2}**"
            f"{' из экипировки' if from_equipment else ''}"
        )
    )
