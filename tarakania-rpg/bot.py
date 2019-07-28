import time

from datetime import timedelta
from typing import Any, Dict

import git
import discord
import humanize

from updater import start_updater


class TarakaniaRPG(discord.AutoShardedClient):
    def __init__(self, config: Dict[str, Any], **kwargs: Any):
        self.config = config

        self.prefixes = {config["default-prefix"]}
        self.owners = set(config["owners"])

        self.repo = git.Repo()

        super().__init__(**kwargs)

    def run(self, *args: Any, **kwargs: Any) -> None:
        super().run(self.config["discord-token"], *args, **kwargs)

    async def prepare_prefixes(self) -> None:
        bot_id = self.user.id
        self.prefixes |= {f"<@{bot_id}>", f"<@!{bot_id}>"}

        print("Prepareded prefixes")

    async def on_ready(self) -> None:
        await start_updater(self)
        await self.prepare_prefixes()

        print("Bot is ready")

    async def on_message(self, msg: discord.Message) -> None:
        used_prefix = None

        for prefix in self.prefixes:
            if msg.content.lower().startswith(prefix):
                used_prefix = prefix
                break

        if used_prefix is None:
            return

        content = msg.content[len(prefix) :]
        args = content.split()
        command = args[0].lower()

        print(
            f"Received command from {msg.author.id} in channel {msg.channel.id}: {command}"
        )

        if command == "ping":
            await msg.channel.send(f"{msg.author.mention}, pong!")
        elif command == "version":
            repo_url = self.repo.remote().url
            commit_date = self.repo.head.object.committed_date
            committer_name = self.repo.head.object.committer.name
            commit_summary = self.repo.head.object.summary
            commit_hash = self.repo.head.object.hexsha

            message = (
                f"Latest commit made {humanize.naturaltime(timedelta(seconds=time.time() - commit_date))} by **{committer_name}**: ```"
                f"{commit_summary}```"
                f"URL: <{repo_url}/commit/{commit_hash}>"
            )

            await msg.channel.send(message)
