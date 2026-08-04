from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.document_repository import DocumentRepository
from app.search.inverted_index import InvertedIndex
from app.search.preprocess import preprocess
from app.search.tfidf import TFIDF


class SearchService:

    def __init__(self):
        self.index = InvertedIndex()
        self.index_built = False

    async def build_index(
        self,
        db: AsyncSession,
    ):
        """
        Build the in-memory inverted index once.
        """

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
        """
        Search documents using TF-IDF ranking.
        """

        query_tokens = preprocess(query)

        ranked = TFIDF.rank_documents(
            query_tokens=query_tokens,
            index=self.index.index,
            total_documents=self.index.total_documents,
            document_frequency=self.index.document_frequency,
        )

        document_ids = [
            document_id
            for document_id, _ in ranked
        ]

        return await DocumentRepository.get_documents_by_ids(
            db,
            document_ids,
        )