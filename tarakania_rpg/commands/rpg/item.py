from handler import Context, Arguments, CommandResult


async def run(ctx: Context, args: Arguments) -> CommandResult:
    return repr(args[0])
