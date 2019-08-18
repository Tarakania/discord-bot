from copy import copy

from handler import BaseCommand, Context, Arguments, CommandResult


class Command(BaseCommand):
    async def run(self, ctx: Context, args: Arguments) -> CommandResult:
        message = copy(ctx.message)
        message.author = args[0]
        message.content = f"{ctx.prefix}{args[1].name} {' '.join(args[2:])}"

        await self.bot._handler.process_message(message)

        return f"Команда **{args[1].name}** обработана от имени **{args[0]}**"
