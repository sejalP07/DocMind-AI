from app.search.inverted_index import InvertedIndex


class SearchShard:

    def __init__(self, shard_id: int):
        self.shard_id = shard_id
        self.index = InvertedIndex()

    def add_document(
        self,
        document_id: int,
        content: str,
    ):
        self.index.add_document(
            document_id,
            content,
        )

    def search(
        self,
        query: str,
    ):
        return self.index.search(query)