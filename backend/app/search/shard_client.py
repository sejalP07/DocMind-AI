import httpx

from app.search.shard_router import ShardRouter


class ShardClient:

    @staticmethod
    async def index_document(document):

        shard_url = ShardRouter.get_shard(
            document.id
        )

        payload = {
            "id": document.id,
            "title": document.title,
            "content": document.content,
            "url": document.url,
        }

        async with httpx.AsyncClient(
            timeout=10.0
        ) as client:

            response = await client.post(
                f"{shard_url}/index",
                json=payload,
            )

            response.raise_for_status()

            return response.json()