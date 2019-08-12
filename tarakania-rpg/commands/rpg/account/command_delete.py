from command import BaseCommand, CommandResult
from parser.arguments import Arguments
from context import Context

from sql import delete_character


class Command(BaseCommand):
    async def run(self, ctx: Context, args: Arguments) -> CommandResult:
        await delete_character(self.bot.pg, ctx.author.id)
        return "Ваш персонаж удалён"
