from command import BaseCommand, CommandResult
from parser.arguments import Arguments
from context import Context


class Command(BaseCommand):
    async def run(self, ctx: Context, args: Arguments) -> CommandResult:
        return f"{ctx.author.mention}, pong!"
