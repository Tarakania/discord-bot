from handler import BaseCommand, Context, Arguments, CommandResult
from rpg.player import Player, UnknownPlayer


class Command(BaseCommand):
    async def run(self, ctx: Context, args: Arguments) -> CommandResult:
        try:
            player = await Player.from_id(ctx.author.id, ctx.bot.pg)
        except UnknownPlayer:
            return "У вас нет персонажа"

        if player == args[1]:
            return "Нельзя дарить вещи себе"

        from_equipment = False
        if args[0] in player.inventory:
            pass
        elif args[0] in player.equipment:
            from_equipment = True
        else:
            return f"В вашем инвентаре и экипировке нет **{args[0]}**"

        # TODO: confirmation

        item = await player.remove_item(args[0], ctx.bot.pg)
        await args[1].add_item(item, ctx.bot.pg)

        return f"**{ctx.author}** передал **{args[0]}** **{args[1]}**{' из экипировки' if from_equipment else ''}"
