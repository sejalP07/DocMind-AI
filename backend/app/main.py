from fastapi import FastAPI
from app.api.crawler import router as crawler_router
from app.api.metrics import router as metrics_router
from app.api.document import router as document_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Distributed Search Engine")

app.include_router(document_router)
app.include_router(crawler_router)
app.include_router(metrics_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "Distributed Search Engine API"
    }
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "distributed-search-engine"
    }