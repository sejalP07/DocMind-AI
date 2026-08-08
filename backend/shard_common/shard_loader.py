from app.search.inverted_index import InvertedIndex

class ShardLoader:

    def __init__(
        self,
        shard_id: int,
        total_shards: int,
    ):
        self.shard_id = shard_id
        self.total_shards = total_shards

        self.index = InvertedIndex()
        self.documents = []

    async def load(
        self,
        db,
        repository,
    ):
        """
        Load only the documents owned by this shard.
        """

        all_documents = await repository.get_all(db)

        print(
            f"Shard {self.shard_id}: "
            f"DB returned {len(all_documents)} documents"
        )

        self.index = InvertedIndex()
        self.documents = []

        for document in all_documents:

            if document.id % self.total_shards != self.shard_id:
                continue

            document_data = {
                "id": document.id,
                "title": document.title,
                "content": document.content,
                "url": document.url,
            }

            self.documents.append(document_data)

            self.index.add_document(
                document.id,
                document.content,
            )
            print(
        f"Shard {self.shard_id}: "
        f"loaded IDs = {[doc['id'] for doc in self.documents]}"
    )
        

    def add_document(self, document: dict):
        """
        Incrementally add one document to this shard.
        """

        # Prevent duplicate indexing
        existing_ids = {
            doc["id"]
            for doc in self.documents
        }

        if document["id"] in existing_ids:
            return

        self.documents.append(document)

        self.index.add_document(
            document["id"],
            document["content"],
        )

    def search(self, query: str):

        query = query.lower().strip()

        results = []

        for document in self.documents:

            if (
                query in document["title"].lower()
                or query in document["content"].lower()
            ):
                results.append(document)

        return results