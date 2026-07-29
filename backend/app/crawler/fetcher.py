import aiohttp


class WebFetcher:

    @staticmethod
    async def fetch(url: str) -> str:
        timeout = aiohttp.ClientTimeout(total=30)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(
                url,
                headers={
                    "User-Agent": "DistributedSearchEngine/0.1"
                },
            ) as response:

                response.raise_for_status()

                return await response.text()