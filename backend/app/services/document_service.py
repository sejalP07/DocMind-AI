from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.document_repository import DocumentRepository
from app.schemas.document import DocumentCreate


class DocumentService:

    @staticmethod
    async def create_document(
        db: AsyncSession,
        document: DocumentCreate,
    ):
        return await DocumentRepository.create(db, document)

    @staticmethod
    async def get_documents(
        db: AsyncSession,
    ):
        return await DocumentRepository.get_all(db)

    @staticmethod
    async def get_document(
        db: AsyncSession,
        document_id: int,
    ):

        document = await DocumentRepository.get_by_id(
            db,
            document_id,
        )

        if document is None:
            raise HTTPException(
                status_code=404,
                detail="Document not found",
            )

        return document

    @staticmethod
    async def delete_document(
        db: AsyncSession,
        document_id: int,
    ):

        document = await DocumentRepository.get_by_id(
            db,
            document_id,
        )

        if document is None:
            raise HTTPException(
                status_code=404,
                detail="Document not found",
            )

        await DocumentRepository.delete(
            db,
            document,
        )

        return {
            "message": "Document deleted successfully"
        }
    @staticmethod
    async def search_documents(
        db: AsyncSession,
        query: str,
        page: int = 1,
        size: int = 10,
    ):
        return await DocumentRepository.search(
            db,
            query,
            page,
            size,
        )