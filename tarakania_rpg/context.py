from typing import Any, Union, Optional, TYPE_CHECKING

import discord

if TYPE_CHECKING:
    from bot import TarakaniaRPG


class Context:
    __slots__ = (
        "bot",
        "message",
        "author",
        "channel",
        "guild",
        "prefix",
        "alias",
    )

    def __init__(
        self,
        bot: "TarakaniaRPG",
        message: discord.Message,
        prefix: str,
        alias: str,
    ):
        self.bot = bot
        self.message = message
        self.prefix = prefix
        self.alias = alias

        self.author = message.author
        self.channel = message.channel
        self.guild = message.guild

    async def send(
        self,
        content: Optional[str] = None,
        *,
        channel: Optional[discord.TextChannel] = None,
        **kwargs: Any,
    ) -> discord.Message:
        target = channel if channel is not None else self.channel

        return await target.send(content=content, **kwargs)

    @property
    def me(self) -> Union[discord.ClientUser, discord.Member]:
        return self.channel.me if self.guild is None else self.guild.me

    @property
    def local_prefix(self) -> str:
        if self.guild is not None:
            guild_prefix = self.bot._handler._custom_prefixes.get(
                self.guild.id
            )
            if guild_prefix is not None:
                return guild_prefix

        return self.bot.config["default-prefix"]

    def __repr__(self) -> str:
        return f"<Context prefix={self.prefix} alias={self.alias} message={self.message}>"
