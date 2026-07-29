from fastapi import FastAPI
from app.api.crawler import router as crawler_router

from app.api.document import router as document_router

app = FastAPI(title="Distributed Search Engine")

app.include_router(document_router)
app.include_router(crawler_router)

@app.get("/")
def root():
    return {
        "message": "Distributed Search Engine API"
    }