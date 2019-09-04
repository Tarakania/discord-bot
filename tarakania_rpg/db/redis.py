from typing import Any, Dict
from asyncio import sleep
from logging import getLogger

import aioredis

log = getLogger(__name__)


class _ConnectionsPool(aioredis.ConnectionsPool):
    def __init__(
        self, *args: Any, retry_count: int = 5, retry_interval: int = 2, **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)

        self._retry_count = retry_count
        self._retry_interval = retry_interval

    async def execute(self, command: str, *args: Any, **kwargs: Any) -> Any:
        exc: Exception

        for i in range(self._retry_count):
            try:
                return await super().execute(command, *args, **kwargs)
            except (
                aioredis.ConnectionClosedError,
                aioredis.PoolClosedError,
                ConnectionRefusedError,
            ) as e:
                log.debug(
                    f"Command {command} failed, remaining attempts: {self._retry_count - i}"
                )
                exc = e
                await sleep(self._retry_interval)

        log.error(f"Command {command} has failed after {self._retry_count} retries")

        raise exc


async def create_redis_pool(config: Dict[str, Any]) -> _ConnectionsPool:
    config = config.copy()
    address = (config.pop("host"), config.pop("port"))

    return await aioredis.create_pool(address, pool_cls=_ConnectionsPool, **config)
