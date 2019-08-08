import asyncpg

from typing import Dict, Optional


async def create_pg_connection(
    pg_config: Dict[str, str]
) -> asyncpg.Connection:
    return await asyncpg.create_pool(**pg_config)


async def get_info_by_nick(
    nick: str, conn: asyncpg.connection
) -> Optional[asyncpg.Record]:
    return await conn.fetchrow("SELECT * FROM players WHERE nick = $1", nick)
