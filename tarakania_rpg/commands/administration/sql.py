from handler import Context, Arguments, CommandResult
from utils.formatting import TabularData, codeblock


async def run(ctx: Context, args: Arguments) -> CommandResult:
    try:
        result = await ctx.bot.pg.fetch(" ".join(args))
    except Exception as e:
        return codeblock(f"Произошла ошибка: {e}")
    if len(result) > 0:
        table = TabularData()
        re = list(result[0].keys())
        table.set_columns(re)
        table.add_rows(list(r.values() for r in result))
        result = table.render()
    return codeblock(result)
