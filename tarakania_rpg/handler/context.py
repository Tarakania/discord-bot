from typing import TYPE_CHECKING, Any, Union, Optional

import discord

if TYPE_CHECKING:
    from bot import TarakaniaRPG
    from .command import Command


_ReactionsType = Union[int, str, discord.Emoji]

CACHE_TTL = 86400  # 24 hours


class Context:
    __slots__ = (
        "bot",
        "message",
        "author",
        "channel",
        "guild",
        "command",
        "prefix",
        "alias",
    )

    def __init__(
        self,
        bot: "TarakaniaRPG",
        message: discord.Message,
        command: "Command",
        prefix: str,
        alias: str,
    ):
        self.bot = bot
        self.message = message
        self.command = command
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
        response_to: Optional[discord.Message] = None,
        register: bool = True,
        **kwargs: Any,
    ) -> discord.Message:
        target = channel if channel is not None else self.channel

        # TODO: cleanup!!! (@everyone/@here, etc)
        new_message = await target.send(content=content, **kwargs)

        if register:
            if response_to is None:
                response_to = self.message

            await self._register_message_response(response_to, new_message)

        return new_message

    async def react(
        self,
        reaction: _ReactionsType,
        target: Optional[discord.Message] = None,
        response_to: Optional[discord.Message] = None,
        register: bool = True,
        **kwargs: Any,
    ) -> discord.Reaction:
        if isinstance(reaction, int):
            emote = self.bot.get_emoji(reaction)
            if emote is None:
                raise ValueError(f"Emoji with id {reaction} not found in cache")
        elif isinstance(reaction, str):
            emote = reaction
        elif isinstance(reaction, discord.Emoji):
            emote = reaction
        else:
            raise TypeError(
                f"Unknown emoji type is passed: {type(reaction)}. Expected one of {discord.Emoji}, {str}, {int}"
            )

        target = self.message if target is None else target

        if register:
            if response_to is None:
                response_to = self.message

            await self._register_reaction_response(response_to, target, emote)

        return await target.add_reaction(emote, **kwargs)

    async def _register_message_response(
        self, response_to: discord.Message, response: discord.Message
    ) -> None:
        address = f"message_responses:{response_to.id}"

        await self.bot.redis.execute(
            "RPUSH", address, f"message:{response.channel.id}:{response.id}"
        )
        await self.bot.redis.execute("EXPIRE", address, CACHE_TTL)

    async def _register_reaction_response(
        self,
        response_to: discord.Message,
        response: discord.Message,
        reaction: _ReactionsType,
    ) -> None:
        key = f"message_responses:{response_to.id}"

        await self.bot.redis.execute(
            "RPUSH", key, f"reaction:{response.channel.id}:{response.id}:{reaction}"
        )
        await self.bot.redis.execute("EXPIRE", key, CACHE_TTL)

    @property
    def me(self) -> Union[discord.ClientUser, discord.Member]:
        return self.channel.me if self.guild is None else self.guild.me

    @property
    def local_prefix(self) -> str:
        if self.guild is not None:
            guild_prefix = self.bot._handler._custom_prefixes.get(self.guild.id)
            if guild_prefix is not None:
                return guild_prefix

        return self.bot.config["default-prefix"]

    def __repr__(self) -> str:
        return (
            f"<Context prefix={self.prefix} alias={self.alias} message={self.message}>"
        )
