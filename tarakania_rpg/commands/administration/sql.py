from handler import Context, Arguments, CommandResult
from utils.formatting import TabularData, codeblock


async def run(ctx: Context, args: Arguments) -> CommandResult:
    try:
        sql = await ctx.bot.pg.fetch(" ".join(args))
    except Exception as e:
        return codeblock("Произошла ошибка: " + str(e))
    if len(sql) > 0:
        table = TabularData()
        re = list(sql[0].keys())
        table.set_columns(re)
        table.add_rows(list(r.values() for r in sql))
        sql = table.render()
    return codeblock(sql)
