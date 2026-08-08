from sqlalchemy import select

from app.models.document import Document


class DocumentRepository:

    @staticmethod
    async def get_all(db):
        result = await db.execute(
            select(Document).order_by(Document.id)
        )

        return result.scalars().all()