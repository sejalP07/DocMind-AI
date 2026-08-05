import asyncio
import httpx


class SearchCoordinator:

    def __init__(self):
        self.shards = [
            "http://127.0.0.1:8001",
            "http://127.0.0.1:8002",
            "http://127.0.0.1:8003",
        ]

    async def search(
        self,
        query: str,
    ):
        async with httpx.AsyncClient(timeout=10.0) as client:

            tasks = [
                client.get(
                    f"{shard}/search",
                    params={"q": query},
                )
                for shard in self.shards
            ]

            responses = await asyncio.gather(
                *tasks,
                return_exceptions=True,
            )

        results = []

        for response in responses:

            if isinstance(response, Exception):
                print("Shard unavailable:", response)
                continue

            if response.status_code == 200:
                results.extend(response.json())

        return results