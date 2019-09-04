from handler import Context, Arguments, CommandResult
from paginator import PageType, RawPagePaginator
from utils.formatting import codeblock

LINES_PER_PAGE = 15


async def run(ctx: Context, args: Arguments) -> CommandResult:
    if len(args) == 1:
        # TODO: syntax hints
        help_text = codeblock(await args[0].get_help(ctx))

        return help_text

    commands = list(
        ctx.bot._handler.get_all_commands(
            with_hidden=ctx.author.id in ctx.bot.config["owners"]
        )
    )
    commands.sort(key=lambda c: c.name)

    lines = [f"{c.name:<12}: {c.short_help}" for c in commands]

    pages = [
        lines[i : i + LINES_PER_PAGE] for i in range(0, len(lines), LINES_PER_PAGE)
    ]

    p = RawPagePaginator(len(pages))

    @p.on_page_switch
    async def f(current_page: int, next_page: int) -> PageType:
        nl = "\n"

        return (
            f"Список **{len(lines)}** доступных команд:"
            f"{codeblock(nl.join(pages[next_page]))}"
            f"Страница **{next_page + 1}** из **{p.size}**"
        )

    return await p.run(ctx)
