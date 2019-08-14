import discord


from rpg.player import Player, UnknownPlayer
from command import BaseCommand, CommandResult
from parser.arguments import Arguments
from context import Context


class Command(BaseCommand):
    async def run(self, ctx: Context, args: Arguments) -> CommandResult:
        if len(args) == 0:
            try:
                player = await Player.from_id(ctx.author.id, ctx.bot.pg)
            except UnknownPlayer:
                return "У вас нет персонажа"
        else:
            player = args[0]

        e = discord.Embed(
            title="Информация о персонаже",
            description=f"""Раса: **{player.race["name"]}**
Класс: **{player.class_["name"]}**
Локация: **{player.location["name"]}**
Уровень: **{player.level}**
Опыта до следующего уровня: **{player.xp_to_next_level}**
Деньги: **{player.money}**
Размер инвентаря: **{len(player.inventory)}**""",
        )
        e.set_author(name=player.nick)

        return await ctx.send(embed=e)
