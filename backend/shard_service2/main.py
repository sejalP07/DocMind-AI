from contextlib import asynccontextmanager

from fastapi import FastAPI

from shard_common.database import get_db
from shard_common.repository import DocumentRepository
from shard_common.shard_loader import ShardLoader

# Shard 2 owns documents where id % 3 == 2
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

    print(f"Shard 2 loaded {len(loader.documents)} documents")

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
async def search(q: str):
    return loader.search(q)


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
        "documents": len(loader.documents),
    }