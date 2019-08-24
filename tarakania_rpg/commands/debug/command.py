from time import time

from handler import Context, Arguments, CommandResult

from utils.formatting import codeblock


async def run(ctx: Context, args: Arguments) -> CommandResult:
    info = {
        "time": time(),
        "prefix": ctx.prefix,
        "alias": ctx.alias,
        "arguments": len(args),
        "author": ctx.author,
        "guild": ctx.guild,
    }

    return codeblock("\n".join(f"{k}: {v}" for k, v in info.items()))
