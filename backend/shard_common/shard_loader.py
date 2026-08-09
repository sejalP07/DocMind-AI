from app.search.inverted_index import InvertedIndex
from app.search.bm25 import BM25
from app.search.preprocess import preprocess

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

    def search(
        self,
        query: str,
        total_documents: int = 0,
        average_document_length: float = 0,
        document_frequency: dict = None,
    ):

        query_tokens = preprocess(query)

        if not query_tokens:
            return []

        total_documents = average_document_length

        if total_documents == 0:
            return []

        # Calculate average document length
        total_length = sum(
            len(preprocess(doc["content"]))
            for doc in self.documents
        )

        average_document_length = (
            total_length / total_documents
        )

        scores = {}

        for document in self.documents:

            document_tokens = preprocess(
                document["content"]
            )

            document_length = len(document_tokens)

            for term in query_tokens:

                term_frequency = document_tokens.count(term)

                if term_frequency == 0:
                    continue

            # Document frequency inside this shard
                document_frequency = sum(
                    1
                    for doc in self.documents
                    if term in preprocess(doc["content"])
                )

                score = BM25.score(
                    term_frequency=term_frequency,
                    document_frequency=document_frequency,
                    total_documents=total_documents,
                    document_length=document_length,
                    average_document_length=average_document_length,
                        )

                scores[document["id"]] = (
                    scores.get(document["id"], 0)
                    + score
                )

        results = []

        for document in self.documents:

            if document["id"] not in scores:
                continue

            result = document.copy()

            result["score"] = round(
                scores[document["id"]],
                4,
            )

            result["snippet"] = document["content"][:200]

            results.append(result)

        results.sort(
            key=lambda x: x["score"],
            reverse=True,
        )

        return results

    def get_stats(self):
        total_documents = len(self.documents)

        total_length = 0
        document_frequency = {}

        for document in self.documents:
            tokens = preprocess(document["content"])
            total_length += len(tokens)

            unique_terms = set(tokens)
            for term in unique_terms:
                document_frequency[term] = (
                    document_frequency.get(term, 0) + 1
                )

        return {
            "shard": self.shard_id,
            "total_documents": total_documents,
            "total_length": total_length,
            "document_frequency": document_frequency,
        }