from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.document_repository import DocumentRepository
from app.search.inverted_index import InvertedIndex


class SearchService:
    def __init__(self):
        self.index = InvertedIndex()
        self.index_built = False
    async def build_index(self, db: AsyncSession):

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
        Search using the inverted index.
        """
        ids = self.index.search(query)

        return await DocumentRepository.get_documents_by_ids(
            db,
            ids,
        )