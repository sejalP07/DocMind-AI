import pytest
import asyncpg


@pytest.mark.asyncio
async def test_postgres_connection():
    conn = await asyncpg.connect(
        host="postgres",
        port=5432,
        user="postgres",
        password="postgres",
        database="search_engine",
    )

    rows = await conn.fetch("SELECT current_database();")
    assert rows[0]["current_database"] == "search_engine"

    await conn.close()