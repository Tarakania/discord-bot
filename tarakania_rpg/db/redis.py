from time import sleep
from typing import Any, Dict
from logging import getLogger

import aioredis

log = getLogger(__name__)


class RedisClient(aioredis.ConnectionsPool):
    def __init__(
        self, *args: Any, retry_count: int = 5, retry_interval: int = 2, **kwargs: Any
    ):
        super().__init__(*args, **kwargs)

        self._retry_count = retry_count
        self._retry_interval = retry_interval

    def execute(self, command: Any, *args: Any, **kwargs: Any) -> Any:
        exc: aioredis.ConnectionError

        for _ in range(self._retry_count):
            try:
                return super().execute(command, *args, **kwargs)
            except aioredis.ConnectionError as e:
                exc = e
                sleep(self._retry_interval)

        log.error(f"Command {command} has failed after {self._retry_count} retries")

        raise exc


async def create_redis_client(config: Dict[str, Any]) -> RedisClient:
    address = (config.pop("host"), config.pop("port"))

    return aioredis.create_pool(address, pool_cls=RedisClient, **config)
