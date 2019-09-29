from handler import Context, Arguments, CommandResult
from utils.formatting import TabularData, codeblock


async def run(ctx: Context, args: Arguments) -> CommandResult:
    try:
        a = await ctx.bot.pg.fetch(" ".join(args))
    except Exception as e:
        return codeblock(str(e))
    if len(a) > 0:
        table = TabularData()
        re = list(a[0].keys())
        table.set_columns(re)
        table.add_rows(list(r.values() for r in a))
        a = table.render()
    return codeblock(a)
