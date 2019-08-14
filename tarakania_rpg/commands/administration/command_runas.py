import copy

from command import BaseCommand, CommandResult
from argparser.arguments import Arguments
from context import Context


class Command(BaseCommand):
    async def run(self, ctx: Context, args: Arguments) -> CommandResult:
        message = copy.copy(ctx.message)
        message.author = args[0]
        message.content = f"{ctx.prefix}{args[1].name} {' '.join(args[2:])}"

        await self.bot._handler.process_message(message)

        return f"Команда **{args[1].name}** обработана от имени **{args[0]}**"
