import asyncio
import asyncpg

async def main():
    conn = await asyncpg.connect(
        user="postgres",
        password="postgres",
        database="search_engine",
        host="localhost",
        port=5432,
    )
    print("Connected")
    await conn.close()

asyncio.run(main())