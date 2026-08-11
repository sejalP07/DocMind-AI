from contextlib import asynccontextmanager
import json

from fastapi import FastAPI

from shard_common.database import get_db
from shard_common.repository import DocumentRepository
from shard_common.shard_loader import ShardLoader
from shard_common.index_request import IndexRequest


loader = ShardLoader(
    shard_id=2,
    total_shards=3,
)


@asynccontextmanager
async def lifespan(app: FastAPI):

    async for db in get_db():

        await loader.load(
            db,
            DocumentRepository,
        )

        break

    print(
        f"Shard 2 loaded "
        f"{len(loader.documents)} documents"
    )

    yield


app = FastAPI(
    title="Shard 2",
    lifespan=lifespan,
)


@app.get("/health")
def health():

    return {
        "status": "healthy",
        "shard": 2,
        "documents": len(loader.documents),
    }
@app.get("/search")
async def search(
    q: str,
    total_documents: int = 0,
    average_document_length: float = 0,
    document_frequency: str = "",
):
    document_frequency = json.loads(document_frequency)
    return loader.search(
        q,
        total_documents=total_documents,
        average_document_length=average_document_length,
        document_frequency=document_frequency,
    )

@app.get("/stats")
async def stats():
    return loader.get_stats()

@app.post("/index")
async def index_document(
    document: IndexRequest,
):

    loader.add_document(
        document.model_dump()
    )

    return {
        "message": "Document indexed",
        "shard": 2,
        "document_id": document.id,
    }


@app.post("/reload")
async def reload():

    async for db in get_db():

        await loader.load(
            db,
            DocumentRepository,
        )

        break

    return {
        "message": "Shard reloaded",
        "shard": 2,
        "documents": len(loader.documents),
    }