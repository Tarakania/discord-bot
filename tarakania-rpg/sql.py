import asyncpg

from typing import Dict, Optional


async def create_pg_connection(
    pg_config: Dict[str, str]
) -> asyncpg.Connection:
    return await asyncpg.create_pool(**pg_config)


async def get_player_info_by_discord_id(
    conn: asyncpg.connection, discord_id: int
) -> Optional[asyncpg.Record]:
    return await conn.fetchrow(
        "SELECT * FROM players WHERE discord_id = $1", discord_id
    )


async def get_player_info_by_nick(
    conn: asyncpg.connection, nick: str
) -> Optional[asyncpg.Record]:
    return await conn.fetchrow("SELECT * FROM players WHERE nick = $1", nick)


async def create_character(
    conn: asyncpg.connection,
    discord_id: int,
    nick: str,
    race_id: int,
    class_id: int,
    location_id: Optional[int] = None,
) -> None:

    if location_id is None:
        location_id = race_id

    await conn.fetch(
        "INSERT INTO players (discord_id, nick, race, class, location) VALUES ($1, $2, $3, $4, $5)",
        discord_id,
        nick,
        race_id,
        class_id,
        location_id,
    )


async def delete_character(conn: asyncpg.connection, discord_id: int) -> None:
    await conn.fetch("DELETE FROM players WHERE discord_id = $1", discord_id)
