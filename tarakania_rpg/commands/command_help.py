from ..command import BaseCommand, CommandResult
from ..parser.arguments import Arguments
from ..context import Context


class Command(BaseCommand):
    async def run(self, ctx: Context, args: Arguments) -> CommandResult:
        if len(args) == 0:
            commands = list(
                self.bot._handler.get_all_commands(
                    with_hidden=ctx.author.id in self.bot.config["owners"]
                )
            )
            commands.sort(key=lambda c: c.name)

            lines = [f"{c.name:<12}: {c.short_help}" for c in commands]
            ln = "\n"
            return f"```{ln}{ln.join(lines)}```"

        return await args[0].get_help(ctx)
