from handler import Context, Arguments, CommandResult
from paginator import PageType, RawPagePaginator
from utils.formatting import TabularData, codeblock

LINES_PER_PAGE = 1


async def run(ctx: Context, args: Arguments) -> CommandResult:
    try:
        result = await ctx.bot.pg.fetch(" ".join(args))
    except Exception as e:
        return f"Произошла ошибка: {codeblock(str(e))}"
    if len(result) > 0:
        table = TabularData()
        table.set_columns(list(result[0].keys()))
        table.add_rows(list(r.values() for r in result))
        result = table.render()
        if len(result) > 2000:
            ii = 0
            lines = []
            for i in range(0, len(result), 1500):
                lines.append(result[ii:i])
                ii = i

            p = RawPagePaginator(len(lines))

            @p.on_page_switch
            async def f(current_page: int, next_page: int) -> PageType:
                nl = ""
                return (
                    f"{codeblock(nl.join(lines[next_page]))}"
                    f"Страница **{next_page + 1}** из **{p.size}**"
                )

            return await p.run(ctx)

    return codeblock(result)
