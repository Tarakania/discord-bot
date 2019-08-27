from collections import Counter

from handler import Context, Arguments, CommandResult
from utils.confirmations import request_confirmation
from utils.command_helpers import get_author_player


async def run(ctx: Context, args: Arguments) -> CommandResult:
    player = await get_author_player(ctx)

    item = args[0]
    player2 = args[1]

    if len(args) == 2:
        number_items = 1
    else:
        if isinstance(args[2], str):
            if args[2] == "all":
                number_items = int(Counter(player.inventory)[item])
        else:
            number_items = args[2]

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
        f"Вы действительно хотите передать **{item}** в количестве **{str(number_items)}** персонажу **{player2}**?"
    )
    confirmation = await request_confirmation(ctx, confirmation_request)

    if not confirmation:
        return await confirmation_request.edit(
            content="Вы не подтвердили передачу предемета"
        )

    for i in range(int(number_items)):
        await player.remove_item(item, ctx.bot.pg)
        await player2.add_item(item, ctx.bot.pg)

    return await confirmation_request.edit(
        content=(
            f"**{player}** передал **{item}** x **{str(number_items)}** **{player2}**"
            f"{' из экипировки' if from_equipment else ''}"
        )
    )
