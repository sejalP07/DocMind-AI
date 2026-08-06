import asyncio
import httpx


class ShardClient:

    SHARDS = [
        "http://127.0.0.1:8001",
        "http://127.0.0.1:8002",
        "http://127.0.0.1:8003",
    ]

    @staticmethod
    async def reload_all():
        async with httpx.AsyncClient(timeout=10.0) as client:

            tasks = [
                client.post(f"{shard}/reload")
                for shard in ShardClient.SHARDS
            ]

            results = await asyncio.gather(
                *tasks,
                return_exceptions=True,
            )

            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    print(f"Shard {i + 1} reload failed: {result}")
                else:
                    print(f"Shard {i + 1} reloaded successfully")