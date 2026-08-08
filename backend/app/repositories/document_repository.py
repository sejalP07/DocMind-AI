from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.models.document import Document


class DocumentRepository:

    @staticmethod
    async def create(db, document):
        db_document = Document(
            title=document.title,
            content=document.content,
            url=document.url,
        )

        try:
            db.add(db_document)

            await db.commit()
            await db.refresh(db_document)

            return db_document

        except IntegrityError:
            await db.rollback()
            raise

    @staticmethod
    async def get_all(
        db: AsyncSession,
    ):
        result = await db.execute(
            select(Document).order_by(Document.id)
        )

        return result.scalars().all()

    @staticmethod
    async def get_documents_by_ids(
        db: AsyncSession,
        ids: list[int],
    ):
        """
        Returns documents in the same order as the given ids.
        """

        if not ids:
            return []

        result = await db.execute(
            select(Document).where(
                Document.id.in_(ids)
            )
        )

        documents = result.scalars().all()

        document_map = {
            document.id: document
            for document in documents
        }

        ordered_documents = []

        for document_id in ids:
            if document_id in document_map:
                ordered_documents.append(
                    document_map[document_id]
                )

        return ordered_documents

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        document_id: int,
    ):
        result = await db.execute(
            select(Document).where(
                Document.id == document_id
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def delete(
        db: AsyncSession,
        document: Document,
    ):
        await db.delete(document)
        await db.commit()

    @staticmethod
    async def search(
        db: AsyncSession,
        query: str,
        page: int = 1,
        size: int = 10,
    ):
        result = await db.execute(
            select(Document).where(
                or_(
                    Document.title.ilike(f"%{query}%"),
                    Document.content.ilike(f"%{query}%"),
                )
            )
        )

        documents = result.scalars().all()

        results = []

        for doc in documents:

            title_matches = doc.title.lower().count(
                query.lower()
            )

            content_matches = doc.content.lower().count(
                query.lower()
            )

            score = title_matches * 3 + content_matches

            results.append(
                {
                    "id": doc.id,
                    "title": doc.title,
                    "url": doc.url,
                    "score": score,
                    "snippet": doc.content[:200],
                }
            )

        results.sort(
            key=lambda x: x["score"],
            reverse=True,
        )

        start = (page - 1) * size
        end = start + size

        return results[start:end]
    