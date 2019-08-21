from handler import BaseCommand, Context, Arguments, CommandResult
from rpg.player import Player, UnknownPlayer, ItemNotFound,PlayerInventory

class Command(BaseCommand):
    async def run(self, ctx: Context, args: Arguments) -> CommandResult:

        try:
            player = await Player.from_id(ctx.author.id, ctx.bot.pg)
        except UnknownPlayer:
            return "У вас нет персонажа"

        try:
            player_nick = await Player.from_nick(args[1], ctx.bot.pg)
        except UnknownPlayer:
            return "У вас нет персонажа"

        await player_nick.add_item_gift(args[0], ctx.bot.pg)

        try:
            await player.remove_item(args[0], ctx.bot.pg)
        except ItemNotFound:
            return f"В вашем инвентаре нет **{args[0]}**"

        return f"**{ctx.author}** передал **{args[0].name}**  **{args[1]}**"