from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.document import (
    DocumentCreate,
    DocumentResponse,
)
from app.schemas.search import SearchResult
from app.services.document_service import DocumentService


router = APIRouter(tags=["Documents"])


@router.post(
    "/documents",
    response_model=DocumentResponse,
)
async def create_document(
    document: DocumentCreate,
    db: AsyncSession = Depends(get_db),
):
    return await DocumentService.create_document(
        db,
        document,
    )


@router.get(
    "/documents",
    response_model=list[DocumentResponse],
)
async def get_documents(
    db: AsyncSession = Depends(get_db),
):
    return await DocumentService.get_documents(db)


@router.get(
    "/documents/{document_id}",
    response_model=DocumentResponse,
)
async def get_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await DocumentService.get_document(
        db,
        document_id,
    )


@router.delete(
    "/documents/{document_id}",
)
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await DocumentService.delete_document(
        db,
        document_id,
    )


@router.get(
    "/search",
    response_model=list[SearchResult],
)
async def search_documents(
    q: str = Query(..., min_length=1, max_length=200),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await DocumentService.search_documents(
        db,
        q,
        page,
        size,
    )
@router.get("/autocomplete")
async def autocomplete(
    q: str = Query(..., min_length=1, max_length=100),
    db: AsyncSession = Depends(get_db),
):
    return await DocumentService.autocomplete(
        db,
        q,
    )

@router.get("/distributed-search")
async def distributed_search(
    q: str = Query(..., min_length=1, max_length=200),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await DocumentService.distributed_search(
    db,
    q,
    page,
    page_size,
)