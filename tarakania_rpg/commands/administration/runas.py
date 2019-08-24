from copy import copy

from handler import Context, Arguments, CommandResult


async def run(ctx: Context, args: Arguments) -> CommandResult:
    message = copy(ctx.message)
    message.author = args[0]
    message.content = f"{ctx.prefix}{args[1].name}{' ' if args[2:] else ''}{' '.join(args[2:])}"

    await ctx.bot._handler.process_message(message)

    return f"Команда **{args[1].name}** обработана от имени **{args[0]}**"
