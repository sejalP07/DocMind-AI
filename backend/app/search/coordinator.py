import asyncio

from app.search.shard import SearchShard


class SearchCoordinator:

    def __init__(self, shard_count: int = 3):
        self.shards = [
            SearchShard(i)
            for i in range(shard_count)
        ]

    def get_shard(
        self,
        document_id: int,
    ):
        return self.shards[
            document_id % len(self.shards)
        ]

    def add_document(
        self,
        document_id: int,
        content: str,
    ):
        shard = self.get_shard(document_id)

        shard.add_document(
            document_id,
            content,
        )

    async def search(
        self,
        query: str,
    ):

        tasks = [
            asyncio.to_thread(
                shard.search,
                query,
            )
            for shard in self.shards
        ]

        shard_results = await asyncio.gather(*tasks)

        results = set()

        for docs in shard_results:
            results |= docs

        return results