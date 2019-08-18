from handler import BaseCommand, Context, Arguments, CommandResult


class Command(BaseCommand):
    async def run(self, ctx: Context, args: Arguments) -> CommandResult:
        return repr(args[0])
