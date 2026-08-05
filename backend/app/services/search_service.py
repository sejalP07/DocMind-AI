
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.document_repository import DocumentRepository
from app.search.bm25 import BM25
from app.search.inverted_index import InvertedIndex
from app.search.preprocess import preprocess
from app.search.phrase_search import PhraseSearch
from app.search.boolean_search import BooleanSearch
from app.search.fuzzy_search import FuzzySearch
from app.search.autocomplete import Autocomplete
from app.core.redis import redis_client
from app.search.coordinator import SearchCoordinator



class SearchService:

    def __init__(self):
        self.index = InvertedIndex()
        self.coordinator = SearchCoordinator()
        self.index_built = False

    async def build_index(
        self,
        db: AsyncSession,
    ):

        if self.index_built:
            return

        documents = await DocumentRepository.get_all_documents(db)

        for document in documents:
            self.index.add_document(
                document.id,
                document.content,
            )
            

        self.index_built = True

    async def search(
        self,
        db: AsyncSession,
        query: str,
    ):

        if not self.index_built:
            await self.build_index(db)


        # -----------------------------
        # Fuzzy Search
        # -----------------------------
        query = FuzzySearch.correct_query(
            self.index,
            query,
        )

        # -----------------------------
        # Redis Cache
        # -----------------------------
        import json
        cache_key = f"search:{query}"

        cached = redis_client.get(cache_key)

        if cached:
            print("Cache Hit")

            ids = json.loads(cached)

            return await DocumentRepository.get_documents_by_ids(
                db,
                ids,
            )
        # -----------------------------
        # Phrase Search
        # -----------------------------
        if query.startswith('"') and query.endswith('"'):

            documents = await DocumentRepository.get_all_documents(db)

            return PhraseSearch.search(
                documents,
                query[1:-1],
            )

        # -----------------------------
        # Boolean Search
        # -----------------------------
        if (
            " AND " in query
            or " OR " in query
            or " NOT " in query
        ):

            document_ids = list(
                BooleanSearch.search(
                    self.index,
                    query,
                )
            )

            return await DocumentRepository.get_documents_by_ids(
                db,
                document_ids,
            )

        # -----------------------------
        # BM25 Search
        # -----------------------------
        query_tokens = preprocess(query)

        if self.index.total_documents == 0:
            return []

        average_document_length = (
            sum(self.index.document_lengths.values())
            / self.index.total_documents
        )

        scores = {}

        for term in query_tokens:

            if term not in self.index.index:
                continue

            for document_id, term_frequency in self.index.index[term].items():

                score = BM25.score(
                    term_frequency=term_frequency,
                    document_frequency=self.index.document_frequency[term],
                    total_documents=self.index.total_documents,
                    document_length=self.index.document_lengths[document_id],
                    average_document_length=average_document_length,
                )

                scores[document_id] = (
                    scores.get(document_id, 0)
                    + score
                )

        ranked_ids = sorted(
            scores.keys(),
            key=lambda doc_id: scores[doc_id],
            reverse=True,
        )

        documents = await DocumentRepository.get_documents_by_ids(
            db,
            ranked_ids,
        )

        redis_client.set(
            cache_key,
            json.dumps(ranked_ids),
            ex=300,  # Cache for 5 minutes
        )

        print("Cache Saved")

        return documents

    async def autocomplete(
        self,
        db: AsyncSession,
        prefix: str,
    ):

        if not self.index_built:
            await self.build_index(db)

        return Autocomplete.suggest(
            self.index,
            prefix,
        )

    async def distributed_search(
        self,
        db: AsyncSession,
        query: str,
    ):
        return await self.coordinator.search(query)