from typing import Any, List, Union

from aioredis import ReplyError

from handler import Context, Arguments, CommandResult


async def run(ctx: Context, args: Arguments) -> CommandResult:
    try:
        return str(decode(await ctx.bot.redis.execute(*args)))
    except ReplyError as e:
        return f"Ошибка: **{e}**"


def decode(value: Any) -> Union[str, List[Any]]:
    if isinstance(value, list):
        return [decode(v) for v in value]
    elif isinstance(value, bytes):
        return value.decode()

    return value
