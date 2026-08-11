import pytest
import asyncpg


@pytest.mark.asyncio
async def test_database_connects():
    conn = await asyncpg.connect(
        user="postgres",
        password="postgres",
        database="search_engine",
        host="postgres",
        port=5432,
    )
    await conn.close()