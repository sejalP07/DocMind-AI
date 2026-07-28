from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.document_repository import DocumentRepository
from app.schemas.document import DocumentCreate


class DocumentService:

    @staticmethod
    async def create_document(
        db: AsyncSession,
        document: DocumentCreate,
    ):
        return await DocumentRepository.create(
            db,
            document,
        )

    @staticmethod
    async def get_documents(
        db: AsyncSession,
    ):
        return await DocumentRepository.get_all(db)

    @staticmethod
    async def search_documents(
        db: AsyncSession,
        query: str,
    ):
        return await DocumentRepository.search(
            db,
            query,
        )