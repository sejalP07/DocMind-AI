from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.schemas.document import DocumentCreate


class DocumentRepository:

    @staticmethod
    async def create(
        db: AsyncSession,
        document: DocumentCreate,
    ) -> Document:

        db_document = Document(
            title=document.title,
            content=document.content,
            url=document.url,
        )

        db.add(db_document)
        await db.commit()
        await db.refresh(db_document)

        return db_document

    @staticmethod
    async def get_all(db: AsyncSession):

        result = await db.execute(
            select(Document)
        )

        return result.scalars().all()

    @staticmethod
    async def search(
        db: AsyncSession,
        query: str,
    ):

        statement = (
            select(Document)
            .where(
                or_(
                    Document.title.ilike(f"%{query}%"),
                    Document.content.ilike(f"%{query}%"),
                )
            )
        )

        result = await db.execute(statement)

        return result.scalars().all()