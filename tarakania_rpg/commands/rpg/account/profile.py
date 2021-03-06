from discord import Embed

from handler import Context, Arguments, CommandResult
from utils.command_helpers import get_author_player


async def run(ctx: Context, args: Arguments) -> CommandResult:
    if len(args) == 0:
        player = await get_author_player(ctx)
    else:
        player = args[0]

    info = {
        "Раса": player.race.name,
        "Класс": player.class_.name,
        "Локация": player.location.name,
        "Уровень": player.level,
        "Опыта до следующего уровня": player.xp_to_next_level,
        "Деньги": player.money,
        "Размер инвентаря": player.inventory.size,
        "Воля": player.stats.will,
        "Защита": player.stats.protection,
        "Сила": player.stats.strength,
        "Сила магии": player.stats.magic_strength,
        "Интеллект": player.stats.intelligence,
        "Живучесть": player.stats.vitality,
        "Ловкость": player.stats.agility,
        "Здоровье": player.stats.health,
        "Мана": player.stats.mana,
        "Очки действия": player.stats.action_points,
    }

    e = Embed(
        title="Информация о персонаже",
        description="\n".join(f"{k}: **{v}**" for k, v in info.items()),
    )
    e.set_author(name=player.nick)

    return await ctx.send(embed=e)
