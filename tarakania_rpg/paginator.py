from __future__ import annotations

import asyncio

from time import time
from typing import Any, Dict, List, Union, Callable, Optional, Awaitable, AsyncIterator
from logging import getLogger
from contextlib import suppress
from concurrent.futures import FIRST_COMPLETED

import discord

from handler.command import StopCommandExecution
from handler.context import Context

__all__ = ("RawPagePaginator", "EmbedPagePaginator", "PaginatorWithHelp")

log = getLogger(__name__)

PageType = Union[str, discord.Embed, Dict[str, Any]]
ControlFnType = Callable[[Any], Awaitable[PageType]]


class _control_fn:
    def __init__(self, fn: ControlFnType, name: str, position: int):
        self.fn = fn
        self.name = name

        setattr(fn, "__position", position)

    def __set_name__(self, owner: _PaginatorBase, name: str) -> None:
        owner._default_events[self.name] = self.fn

        setattr(owner, name, self.fn)


def control_fn(name: str, position: int = 1) -> Callable[[ControlFnType], _control_fn]:
    """Decorator for emote event handlers."""

    def wrapper(fn: ControlFnType) -> _control_fn:
        return _control_fn(fn, name, position)

    return wrapper


class NoPageUpdate(Exception):
    """Raise if you need to stop page update operation"""


class _PaginatorBase:
    """Provides base for other paginators. Not useful on its own."""

    __slots__ = (
        "size",
        "_timeout",
        "_timeout_modifier",
        "_cache_pages",
        "_pages",
        "_index",
        "_stopped",
        "_reaction_add_task",
        "_reaction_remove_task",
        "_stop_task",
        "_page_switch_callback",
        "_user",
        "_message",
        "_ctx",
        "_events",
    )

    _default_events: Dict[str, ControlFnType] = {}

    def __init__(
        self,
        size: int,
        *,
        timeout: float = 50,
        timeout_modifier: float = 20,
        cache_pages: bool = True,
    ) -> None:
        if size < 0:
            raise ValueError("Paginator size should not be lower than 0")

        self.size = size
        self._timeout = timeout
        self._timeout_modifier = timeout_modifier
        self._cache_pages = cache_pages

        self._pages: List[Optional[PageType]]
        if cache_pages:
            self._pages = [None] * size

        self._index = 0
        self._stopped = False

        # awful nasty types
        self._reaction_add_task: Any
        self._reaction_remove_task: Any
        self._stop_task: Any = None

        self._user: discord.User
        self._message: discord.Message
        self._ctx: Context

        # to allow dynamic modification of _events
        self._events = self._default_events

        self._sort_reactions()

    def _sort_reactions(self) -> None:
        # negative indexes
        for fn in self._events.values():
            position = getattr(fn, "__position")
            if position < 0:
                # TODO: what if (-position) > len(self._events) ?
                setattr(fn, "__position", len(self._events) + position)

        self._events = dict(
            sorted(self._events.items(), key=lambda x: getattr(x[1], "__position"))
        )

    async def _init_reactions(self) -> None:
        try:
            for emoji in self._events.keys():
                await self._message.add_reaction(emoji)
        except discord.HTTPException:
            self.stop()

    async def _clear_reactions(self) -> None:
        try:
            for emoji in self._events.keys():
                await self._message.remove_reaction(emoji, self._ctx.me)
        except discord.HTTPException:
            return

    async def _listen_events(
        self, time_remaining: float
    ) -> AsyncIterator[discord.RawReactionActionEvent]:
        def check(event: discord.RawReactionActionEvent) -> bool:
            return (
                event.user_id == self._user.id
                and event.message_id == self._message.id
                and str(event.emoji) in self._events
            )

        log.debug(f"{self}: listening events")

        while not self._stopped:
            # TODO: listen for websocket instead of 2 events?
            # https://github.com/Gelbpunkt/IdleRPG/blob/d85f2e373b076e48ea26cde370ab54ecc651582b/cogs/shard_communication.py#L278
            self._reaction_add_task = asyncio.create_task(
                self._ctx.bot.wait_for("raw_reaction_add", check=check)
            )
            self._reaction_remove_task = asyncio.create_task(
                self._ctx.bot.wait_for("raw_reaction_remove", check=check)
            )

            try:
                done, pending = await asyncio.wait(
                    (self._reaction_add_task, self._reaction_remove_task),
                    loop=self._ctx.bot.loop,
                    timeout=time_remaining,
                    return_when=FIRST_COMPLETED,
                )

                for task in pending:
                    task.cancel()

                if not done:
                    # timeout
                    break

                yield done.pop().result()
            except asyncio.CancelledError:
                if not self._stopped:
                    raise  # caused by something else

                # caused by cancelling wait_for tasks
                break

    @staticmethod
    def _check_permissions(channel: discord.TextChannel) -> None:
        me = channel.me if isinstance(channel, discord.DMChannel) else channel.guild.me
        perms = me.permissions_in(channel)

        for permission_name in ("add_reactions", "read_message_history"):
            if not getattr(perms, permission_name):
                raise StopCommandExecution(f"У меня нет разрешения {permission_name}")

    def _schedule_stop(self, delay: Optional[float] = None) -> None:
        delay = self._timeout if delay is None else delay

        if self._stop_task is not None:
            self._stop_task.cancel()

        log.debug(f"{self}: scheduled stop in {round(delay, 1)} seconds")

        self._stop_task = self._ctx.bot.loop.call_later(delay, self.stop)

    def _make_edit_kwargs(self, page: PageType) -> Dict[str, Any]:
        if isinstance(page, str):
            return {"content": page, "embed": None}
        elif isinstance(page, discord.Embed):
            return {"content": "", "embed": page}
        else:
            return page

    @property
    def paginatable(self) -> bool:
        """Check if pagination should be done."""

        return self.size > 1

    async def run(
        self,
        ctx: Context,
        message: Optional[discord.Message] = None,
        user: Optional[discord.User] = None,
        page_switch: Optional[Callable[[int, int], Awaitable[PageType]]] = None,
    ) -> discord.Message:
        """Run paginator."""

        if page_switch is not None:
            self._page_switch_callback = page_switch
        elif not hasattr(self, "_page_switch_callback"):
            raise AttributeError("Page generation function not set")

        if message is None:
            kwargs = self._make_edit_kwargs(await self._switch_page(0, 0))
            message = await ctx.send(**kwargs)

        if user is None:
            user = ctx.author

        self._ctx = ctx
        self._user = user
        self._message = message

        if not self.paginatable:
            log.debug(f"{self}: not paginatable, exiting")

            return message

        self._check_permissions(message.channel)

        await self._init_reactions()

        start_time = time()
        time_remaining = self._timeout
        self._schedule_stop()

        async for event in self._listen_events(time_remaining):
            log.debug(f"{self}: {event.emoji} <- {event.user_id}")

            try:
                page = await self._events[str(event.emoji)](self)
            except NoPageUpdate:
                continue

            kwargs = self._make_edit_kwargs(page)
            # TODO: ctx.edit
            await message.edit(**kwargs)

            time_remaining = (
                start_time + self._timeout + self._timeout_modifier - time()
            )
            self._schedule_stop(time_remaining)

        await self._clear_reactions()

        return message

    def stop(self) -> None:
        """Stop paginator."""

        log.debug(f"{self}: stopping")

        self._stopped = True

        self._reaction_add_task.cancel()
        self._reaction_remove_task.cancel()

    async def _switch_page(self, old_index: int, new_index: int) -> PageType:
        """Get page from cache or use callback to generate it."""

        log.debug(f"{self}: {old_index} -> {new_index}")

        page = None
        if self._cache_pages:
            page = self._pages[new_index]

        if page is None:
            log.debug(f"{self}: generating page {new_index}")

            page = await self._page_switch_callback(old_index, new_index)

        if self._cache_pages:
            self._pages[self._index] = page

        return page

    def on_page_switch(
        self, callback: Callable[[int, int], Awaitable[PageType]]
    ) -> None:
        """Decorator to set page switch callback."""

        self._page_switch_callback = callback

    @property
    def index(self) -> int:
        return self._index

    def __str__(self) -> str:
        if not hasattr(self, "_message"):
            return "?-?"

        return f"{self._message.channel.id}-{self._message.id}"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} size=self.size >"


class PaginatorWithHelp(_PaginatorBase):
    """Contains help button."""

    __slots__ = ("_on_help_page",)

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

        self._on_help_page = False

    @control_fn("\N{WHITE QUESTION MARK ORNAMENT}", position=-1)
    async def _help(self) -> PageType:
        """Справка по использованию пагинатора."""

        if self._on_help_page:
            self._on_help_page = False
            return await self._switch_page(self._index, self._index)
        else:
            self._on_help_page = True

        e = discord.Embed(
            description=(
                "Для использования пагинатора, нажимайте на реакции под \n"
                "этим сообщением. \n"
                "Каждое нажатие на реакцию добавляет время работы пагинатора.\n"
                "По истечению этого времени бот уберёт свои реакции и не \n"
                "будет реагировать на нажатия.\n\n"
                "**Список реакций и их действий приведён ниже:**\n"
            )
            + "\n".join(f"{emote}: {fn.__doc__}" for emote, fn in self._events.items()),
            color=discord.Color.purple(),
        )
        e.set_author(name="Справка по использованию пагинатора")

        return e


class RawPagePaginator(PaginatorWithHelp):
    """
    Most basic paginator. Sends page switch callback result directly to
    message.edit.
    """

    __slots__ = ("_index_request_timeout", "_looped")

    def __init__(
        self,
        *args: Any,
        index_request_timeout: float = 15,
        looped: bool = True,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)

        self._index_request_timeout = index_request_timeout
        self._looped = looped

    def _index_down(self) -> None:
        if self._index == 0:
            if self._looped:
                self._index = self.size - 1
        else:
            self._index -= 1

    def _index_up(self) -> None:
        if self._index == self.size - 1:
            if self._looped:
                self._index = 0
        else:
            self._index += 1

    @control_fn("\N{BLACK LEFT-POINTING TRIANGLE}")
    async def _prev_page(self) -> PageType:
        """Перейти на предыдущую страницу."""

        old_index = self._index

        if self._on_help_page:
            self._on_help_page = False
        else:
            self._index_down()

            # not looped, avoid redundant http request
            if old_index == self._index:
                raise NoPageUpdate

        return await self._switch_page(old_index, self._index)

    @control_fn("\N{INPUT SYMBOL FOR NUMBERS}")
    async def _page_by_index(self) -> PageType:
        """Перейти по номеру страницы (бот попросит отправить номер)."""

        request_message = None
        response_message = None

        try:
            request_message = await self._ctx.send("Отправьте номер страницы")
        except discord.HTTPException:
            self.stop()

        def check(message: discord.Message) -> bool:
            return (
                message.author == self._user
                and message.channel == self._message.channel
                and message.content.isdigit()
            )

        async def cleanup() -> None:
            with suppress(discord.HTTPException):
                if request_message is not None:
                    await request_message.delete()

        try:
            while True:
                response_message = await self._ctx.bot.wait_for(
                    "message", timeout=self._index_request_timeout, check=check
                )

                new_index = int(response_message.content) - 1

                with suppress(discord.HTTPException):
                    await response_message.delete()

                if not (0 <= new_index < self.size):
                    await self._ctx.send(
                        f"Номер страницы должен быть между 1 и {self.size}",
                        delete_after=5,
                    )

                    continue

                break

            old_index = self._index
            self._index = new_index

            # same page, avoid redundant http request
            if old_index == new_index:
                raise NoPageUpdate

            return await self._switch_page(old_index, new_index)
        except asyncio.TimeoutError:
            await cleanup()

            raise NoPageUpdate

        # finally statement should not be used for cleanup because it will be triggered
        # by bot shutdown/cancellation of command
        await cleanup()

    @control_fn("\N{BLACK RIGHT-POINTING TRIANGLE}")
    async def _next_page(self) -> PageType:
        """Перейти на страницу вперёд."""

        old_index = self._index

        if self._on_help_page:
            self._on_help_page = False
        else:
            self._index_up()

            # not looped, avoid redundant http request
            if old_index == self._index:
                raise NoPageUpdate

        return await self._switch_page(old_index, self._index)


class EmbedPagePaginator(RawPagePaginator):
    """
    Formats embed for you (page number in footer). Page switch callbacks should
    return embed object.
    """

    async def _switch_page(self, old_index: int, new_index: int) -> PageType:
        page = await super()._switch_page(old_index, new_index)

        if not isinstance(page, discord.Embed):
            raise ValueError("Page should be Embed")

        if self.paginatable:
            page.set_footer(text=f"Страница {self._index + 1} из {self.size}")

        return page
