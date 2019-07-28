import typing

import discord

from updater import start_updater
from utils.subprocess import create_subprocess_shell


class TarakaniaRPG(discord.AutoShardedClient):
    def __init__(self, prefix: str, **kwargs: typing.Any):
        self.prefixes = {prefix}

        super().__init__(**kwargs)

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
            program = "&&".join(
                (
                    "git config --get remote.origin.url",
                    r'git show -s HEAD --format="latest commit made %cr by **%cn**: \`\`\`%s\`\`\`URL: <{repo_url}/commit/%H>"',
                )
            )

            process = await create_subprocess_shell(program)
            stdout, stderr = await process.communicate()

            git_url, _, commit_info = stdout.decode().strip().partition("\n")

            if git_url.endswith(".git"):
                git_url = git_url[:-4]
            if git_url.startswith("ssh://"):
                git_url = git_url[6:]
            if git_url.startswith("git@"):
                domain, _, resource = git_url[4:].partition(":")
                git_url = f"https://{domain}/{resource}"
            if git_url.endswith("/"):
                git_url = git_url[:-1]

            git_domain = "https://" + git_url[8:].split("/")[0]
            commit_info = commit_info.format(
                repo_url=git_url, domain=git_domain
            )

            await msg.channel.send(commit_info)
