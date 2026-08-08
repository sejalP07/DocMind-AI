from contextlib import asynccontextmanager

from fastapi import FastAPI

from shard_common.database import get_db
from shard_common.repository import DocumentRepository
from shard_common.shard_loader import ShardLoader
from shard_common.index_request import IndexRequest


loader = ShardLoader(
    shard_id=1,
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
        f"Shard 1 loaded "
        f"{len(loader.documents)} documents"
    )

    yield


app = FastAPI(
    title="Shard 1",
    lifespan=lifespan,
)


@app.get("/health")
def health():

    return {
        "status": "healthy",
        "shard": 1,
        "documents": len(loader.documents),
    }


@app.get("/search")
async def search(q: str):

    return loader.search(q)


@app.post("/index")
async def index_document(
    document: IndexRequest,
):

    loader.add_document(
        document.model_dump()
    )

    return {
        "message": "Document indexed",
        "shard": 1,
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
        "shard": 1,
        "documents": len(loader.documents),
    }