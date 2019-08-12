import time

from command import BaseCommand, CommandResult
from parser.arguments import Arguments
from context import Context


class Command(BaseCommand):
    async def run(self, ctx: Context, args: Arguments) -> CommandResult:
        receive_time = time.time()
        msg = await ctx.send("Pinging...")
        request_complete_time = time.time()

        receive_diff = (
            receive_time
            - (ctx.message.edited_at or ctx.message.created_at).timestamp()
        )

        send_diff = request_complete_time - receive_time

        total_diff = (
            ctx.message.edited_at or ctx.message.created_at
        ) - msg.created_at

        return await msg.edit(
            content=(
                f"```\n"
                f"Receive diff: {round(receive_diff / 1000)}ms\n"
                f"Message send: {round(send_diff * 1000)}ms\n"
                f"Total diff:   {round(total_diff.microseconds / 1000)}ms\n"
                f"WS latency:   {round(self.bot.latency * 1000)}ms\n"
                f"```"
            )
        )
