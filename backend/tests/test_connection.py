import asyncio
import asyncpg


async def main():
    conn = await asyncpg.connect(
        host="127.0.0.1",
        port=5434,
        user="postgres",
        password="postgres",
        database="search_engine",
    )

    print("Connected!")

    rows = await conn.fetch(
        "SELECT current_database();"
    )

    print(rows)

    await conn.close()


asyncio.run(main())