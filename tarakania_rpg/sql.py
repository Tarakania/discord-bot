from typing import Dict

import asyncpg


async def create_pg_connection(
    pg_config: Dict[str, str]
) -> asyncpg.Connection:
    return await asyncpg.create_pool(**pg_config)
