from time import time
from datetime import timedelta

from humanize import naturaltime

from handler import BaseCommand, Context, Arguments, CommandResult

from utils.formatting import codeblock


class Command(BaseCommand):
    async def run(self, ctx: Context, args: Arguments) -> CommandResult:
        repo_url = self.bot.repo.remote().url
        commit_date = self.bot.repo.head.object.committed_date
        committer_name = self.bot.repo.head.object.committer.name
        commit_summary = self.bot.repo.head.object.summary
        commit_hash = self.bot.repo.head.object.hexsha

        return (
            f"Latest commit made {naturaltime(timedelta(seconds=time() - commit_date))} by **{committer_name}**:"
            f"{codeblock(commit_summary)}"
            f"URL: <{repo_url}/commit/{commit_hash}>"
        )
