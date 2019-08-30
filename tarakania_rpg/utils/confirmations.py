from typing import Set, Dict, Union, Iterable, Optional
from asyncio import TimeoutError
from contextlib import suppress

import discord

from handler.context import Context
from handler.converters import Bool

DEFAULT_TIMEOUT = 20


# TODO
_channel_lock: Dict[int, Set[int]] = {}  # channel id to user ids mapping


async def _reaction_confirmation(
    *,
    ctx: Context,
    message: discord.Message,
    user: discord.User,
    emoji_accept: str = "\N{WHITE HEAVY CHECK MARK}",
    emoji_reject: str = "\N{CROSS MARK}",
    timeout: int,
) -> Optional[bool]:
    all_emojis = (emoji_accept, emoji_reject)

    try:
        for emoji in all_emojis:
            await message.add_reaction(emoji)
    except discord.HTTPException:
        return None

    confirmed = None

    def check(r: discord.Reaction, u: Union[discord.Member, discord.User]) -> bool:
        if u != user or r.message.id != message.id:
            return False

        nonlocal confirmed
        emoji_str = str(r.emoji)

        if emoji_str == emoji_accept:
            confirmed = True

            return True
        if emoji_str == emoji_reject:
            confirmed = False

            return True

        return False

    async def do_cleanup(user_reaction: Optional[discord.Reaction] = None) -> None:
        try:
            for emoji in all_emojis:
                await message.remove_reaction(emoji, ctx.me)

            if user_reaction is not None:
                await user_reaction.remove(user)
        except discord.HTTPException:
            return

    try:
        reaction, member = await ctx.bot.wait_for(
            "reaction_add", timeout=timeout, check=check
        )
    except TimeoutError:
        await do_cleanup()

        return None
    else:
        await do_cleanup(user_reaction=reaction)

    return confirmed


async def _text_confirmation(
    *,
    ctx: Context,
    message: discord.Message,
    user: discord.User,
    accept_choices: Iterable[str] = Bool.POSITIVE,
    reject_choices: Iterable[str] = Bool.NEGATIVE,
    timeout: int,
) -> Optional[bool]:

    # intentionally not doing try/catch here. if it fails, we're in trouble
    hint_message = await message.channel.send("Отправьте да/нет")

    confirmed = None

    def check(m: discord.Message) -> bool:
        if m.author != user or m.channel != message.channel:
            return False

        nonlocal confirmed
        lower_content = m.content.lower()

        if lower_content in accept_choices:
            confirmed = True

            return True

        if lower_content in reject_choices:
            confirmed = False

            return True

        return False

    try:
        user_message = await ctx.bot.wait_for("message", timeout=timeout, check=check)
    except TimeoutError:
        return None

    else:
        with suppress(discord.HTTPException):
            await user_message.delete()
    finally:
        with suppress(discord.HTTPException):
            await hint_message.delete()

    return confirmed


async def request_confirmation(
    ctx: Context,
    message: discord.Message,
    *,
    user: Optional[discord.User] = None,
    emoji_accept: str = "\N{WHITE HEAVY CHECK MARK}",
    emoji_reject: str = "\N{CROSS MARK}",
    accept_choices: Iterable[str] = Bool.POSITIVE,
    reject_choices: Iterable[str] = Bool.NEGATIVE,
    timeout: int = DEFAULT_TIMEOUT,
) -> Optional[bool]:
    """
    Ask user for action confirmation. Message must be provided.

    There are 3 possible return values:
        True: user confirmed action
        False: user rejected action
        None: timed out/other error

    This function tries to get reaction confirmation first. If it fails, it
    switches to text confirmation.
    """

    if user is None:
        user = ctx.author

    permissions = message.channel.permissions_for(ctx.me)

    if permissions.read_message_history and permissions.add_reactions:
        return await _reaction_confirmation(
            ctx=ctx,
            message=message,
            emoji_accept=emoji_accept,
            emoji_reject=emoji_reject,
            user=user,
            timeout=timeout,
        )
    else:
        return await _text_confirmation(
            ctx=ctx,
            message=message,
            user=user,
            accept_choices=accept_choices,
            reject_choices=reject_choices,
            timeout=timeout,
        )


async def request_phrase_confirmation(
    ctx: Context,
    message: discord.Message,
    text: str,
    user: Optional[discord.User] = None,
    case_sensitive: bool = True,
    timeout: int = DEFAULT_TIMEOUT,
) -> Optional[bool]:
    """
    Ask user for action confirmation. Message must be provided.

    There are 3 possible return values:
        True: user confirmed action
        False: user rejected action
        None: timed out/other error

    This function requires user to enter the exact phrase to confirm.
    """

    if not case_sensitive:
        text = text.lower()

    if user is None:
        user = ctx.author

    def check(m: discord.Message) -> bool:
        return all(
            (
                m.author == user,
                m.channel == message.channel,
                (m.content if case_sensitive else m.content.lower()) == text,
            )
        )

    try:
        user_message = await ctx.bot.wait_for("message", timeout=timeout, check=check)
    except TimeoutError:
        return None

    with suppress(discord.HTTPException):
        await user_message.delete()

    return True
