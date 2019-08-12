import time

from command import BaseCommand, CommandResult
from parser.arguments import Arguments
from context import Context
from utils.formatting import codeblock


class Command(BaseCommand):
    async def run(self, ctx: Context, args: Arguments) -> CommandResult:
        info = {
            "time": time.time(),
            "prefix": ctx.prefix,
            "alias": ctx.alias,
            "arguments": len(args),
            "author": ctx.author,
            "guild": ctx.guild,
        }

        return codeblock("\n".join(f"{k}: {v}" for k, v in info.items()))
