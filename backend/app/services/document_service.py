from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.document_repository import DocumentRepository
from app.schemas.document import DocumentCreate
from app.services.search_service import SearchService
from app.search.shard_client import ShardClient




search_service = SearchService()


class DocumentService:
    @staticmethod
    async def create_document(
        db: AsyncSession,
        document: DocumentCreate,
    ):
        document = await DocumentRepository.create(
            db,
            document,
        )

        await ShardClient.reload_all()

        return document

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
    async def autocomplete(
        db: AsyncSession,
        prefix: str,
    ):
        await search_service.build_index(db)

        return await search_service.autocomplete(
            db,
            prefix,
        )

    @staticmethod
    async def distributed_search(
        db: AsyncSession,
        query: str,
    ):
        await search_service.build_index(db)

        return await search_service.distributed_search(
            db,
            query,
        )

    @staticmethod
    async def search_documents(
        db: AsyncSession,
        query: str,
        page: int = 1,
        size: int = 10,
    ):
        # Build the index if needed
        await search_service.build_index(db)

        documents = await search_service.search(
            db,
            query,
        )

        results = []

        for doc in documents:
            results.append(
                {
                    "id": doc.id,
                    "title": doc.title,
                    "url": doc.url,
                    "score": 1.0,
                    "snippet": doc.content[:200],
                }
            )

        start = (page - 1) * size
        end = start + size

        return results[start:end]