from app.search.shard import SearchShard


class SearchCoordinator:

    def __init__(self, shard_count=3):

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
        content,
    ):

        shard = self.get_shard(document_id)

        shard.add_document(
            document_id,
            content,
        )

    def search(
        self,
        query,
    ):

        results = set()

        for shard in self.shards:

            results |= shard.search(query)

        return results