from handler import Context, Arguments, CommandResult
from rpg.race import Race
from rpg.class_ import Class
from rpg.player import Player, NickOrIDUsed
from rpg.rpg_object import UnknownObject


async def run(ctx: Context, args: Arguments) -> CommandResult:
    nick = args[0]

    if not (1 <= len(nick) <= 128):
        return f"Имя персонажа должно быть в пределах от **1** до **128** символов.\nВы ввели **{len(nick)}**"

    try:
        race: Race = Race.from_name(args[1])
    except UnknownObject:
        return f"Выберите название расы из: **{', '.join(i.name for i in Race.all_instances())}**"

    try:
        class_: Class = Class.from_name(args[2])
    except UnknownObject:
        return f"Выберите название класса из: **{', '.join(i.name for i in Class.all_instances())}**"

    try:
        await Player.create(
            ctx.bot.pg, ctx.author.id, nick, race.id, class_.id
        )
    except NickOrIDUsed:
        return "Персонаж с таким именем уже существует или у вас уже есть персонаж"

    return "Персонаж создан"
