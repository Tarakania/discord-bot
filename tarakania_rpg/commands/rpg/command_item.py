from command import BaseCommand, CommandResult
from argparser.arguments import Arguments
from context import Context


class Command(BaseCommand):
    async def run(self, ctx: Context, args: Arguments) -> CommandResult:
        return repr(args[0])
