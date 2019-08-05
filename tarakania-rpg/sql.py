import asyncpg

from typing import Dict


async def create_pg_connection(
    pg_config: Dict[str, str]
) -> asyncpg.Connection:
    return await asyncpg.create_pool(**pg_config)


async def get_info_by_nickname(
    nickname: str, conn: asyncpg.connection
) -> asyncpg.Record:
    sql = f"SELECT * FROM statyPlayers WHERE nickname = '{nickname}'"

    return await conn.fetchrow(sql)
