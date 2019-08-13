import asyncpg

from typing import Dict


async def create_pg_connection(
    pg_config: Dict[str, str]
) -> asyncpg.Connection:
    return await asyncpg.create_pool(**pg_config)
