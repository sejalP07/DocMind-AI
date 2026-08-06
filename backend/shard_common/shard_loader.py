from app.search.inverted_index import InvertedIndex


class ShardLoader:

    def __init__(self, shard_id, total_shards):

        self.shard_id = shard_id
        self.total_shards = total_shards

        self.documents = []

        self.index = InvertedIndex()

    async def load(
        self,
        db,
        repository,
    ):

        documents = await repository.get_all(db)

        self.documents.clear()

        self.index = InvertedIndex()

        for document in documents:

            if document.id % self.total_shards != self.shard_id:
                continue

            self.documents.append(document)

            self.index.add_document(
                document.id,
                document.content,
            )

    def search(
        self,
        query,
    ):

        ids = self.index.search(query)

        return [
            document
            for document in self.documents
            if document.id in ids
        ]