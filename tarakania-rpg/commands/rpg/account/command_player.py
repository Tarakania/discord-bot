import discord


from player import Player
from command import BaseCommand, CommandResult
from parser.arguments import Arguments
from context import Context
from sql import get_player_info_by_discord_id


class Command(BaseCommand):
    async def run(self, ctx: Context, args: Arguments) -> CommandResult:
        if len(args) == 0:
            data = await get_player_info_by_discord_id(
                self.bot.pg, ctx.author.id
            )
            if data is None:
                return "У вас нет персонажа"

            player = Player.from_data(data)
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
