import asyncio
import asyncpg

async def connection_db(config):
    user = config["user"]
    password = config["password"]
    database = config["database"]
    host = config["host"]
    con = await asyncpg.connect(user=user, password=password, database=database, host=host)
    async with con.transaction():
        return con


async def read(nickname):
    con = await connection_db()
    sql = "SELECT*FROM statyPlayers WHERE nickname = '{0}';".format(nickname)
    read_sql = await con.fetchrow(sql)
    return read_sql


async def main():
    tsk1 = asyncio.create_task(connection_db())
    tsk2 = asyncio.create_task(read())

    await asyncio.gather(tsk1, tsk2)