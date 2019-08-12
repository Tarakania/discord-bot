import asyncpg

from rpg.races import races
from rpg.classes import classes

from command import BaseCommand, CommandResult
from parser.arguments import Arguments
from context import Context
from sql import create_character


class Command(BaseCommand):
    async def run(self, ctx: Context, args: Arguments) -> CommandResult:
        nick = args[0]
        race = args[1].lower()
        class_ = args[2].lower()

        if not (1 <= len(nick) <= 128):
            return f"Имя персонажа должно быть в пределах от **1** до **128** символов.\nВы ввели **{len(nick)}**"

        is_race_valid = False
        for race_id, r in races.items():
            if r["name"].lower() == race:
                is_race_valid = True
                break

        if not is_race_valid:
            return f"Выберите название расы из: **{', '.join(i['name'] for i in races.values())}**"

        is_class_valid = False
        for class_id, c in classes.items():
            if c["name"].lower() == class_:
                is_class_valid = True
                break

        if not is_class_valid:
            return f"Выберите название класса из: **{', '.join(i['name'] for i in classes.values())}**"

        try:
            await create_character(
                self.bot.pg, ctx.author.id, nick, race_id, class_id
            )
        except asyncpg.UniqueViolationError:  # TODO: parse e.detail to get problematic key or check beforehand
            return "Персонаж с таким именем уже существует или у вас уже есть персонаж"

        return "Персонаж создан"
