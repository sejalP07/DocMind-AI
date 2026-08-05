from fastapi import FastAPI

app = FastAPI(title="Shard 1")

DOCUMENTS = [
    {
        "id": 1,
        "title": "Python FastAPI Guide",
        "content": "Python Python FastAPI REST API tutorial",
        "url": "https://doc1.com",
    },
    {
        "id": 2,
        "title": "Advanced Python",
        "content": "Python programming language advanced concepts",
        "url": "https://doc2.com",
    },
]


@app.get("/health")
def health():
    return {"status": "Shard 1 Running"}


@app.get("/search")
def search(q: str):
    q = q.lower()

    return [
        doc
        for doc in DOCUMENTS
        if q in doc["title"].lower()
        or q in doc["content"].lower()
    ]