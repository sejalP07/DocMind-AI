from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.crawler import CrawlRequest
from app.schemas.document import DocumentResponse
from app.services.crawler_service import CrawlerService

router = APIRouter(tags=["Crawler"])


@router.post(
    "/crawl",
    response_model=DocumentResponse,
)
async def crawl(
    request: CrawlRequest,
    db: AsyncSession = Depends(get_db),
):
    return await CrawlerService.crawl(
        db,
        str(request.url),
    )