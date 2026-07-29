from sqlalchemy.ext.asyncio import AsyncSession

from app.crawler.fetcher import WebFetcher
from app.crawler.parser import HTMLParser
from app.schemas.document import DocumentCreate
from app.services.document_service import DocumentService


class CrawlerService:

    @staticmethod
    async def crawl(
        db: AsyncSession,
        url: str,
    ):
        html = await WebFetcher.fetch(url)

        parsed = HTMLParser.parse(html)

        document = DocumentCreate(
            title=parsed["title"],
            content=parsed["content"],
            url=url,
        )

        return await DocumentService.create_document(
            db,
            document,
        )