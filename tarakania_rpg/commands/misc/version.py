from time import time
from datetime import timedelta

from humanize import naturaltime

from handler import Context, Arguments, CommandResult

from utils.formatting import codeblock


async def run(ctx: Context, args: Arguments) -> CommandResult:
    repo_url = ctx.bot.repo.remote().url
    commit_date = ctx.bot.repo.head.object.committed_date
    committer_name = ctx.bot.repo.head.object.committer.name
    commit_summary = ctx.bot.repo.head.object.summary
    commit_hash = ctx.bot.repo.head.object.hexsha

    return (
        f"Latest commit made {naturaltime(timedelta(seconds=time() - commit_date))} by **{committer_name}**:"
        f"{codeblock(commit_summary)}"
        f"URL: <{repo_url}/commit/{commit_hash}>"
    )
