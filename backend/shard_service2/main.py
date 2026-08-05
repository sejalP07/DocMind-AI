from fastapi import FastAPI

app = FastAPI(title="Shard 2")

DOCUMENTS = [
    {
        "id": 3,
        "title": "Docker Guide",
        "content": "Docker containers Kubernetes deployment",
        "url": "https://doc3.com",
    },
    {
        "id": 4,
        "title": "Kubernetes Basics",
        "content": "Pods Services Deployment",
        "url": "https://doc4.com",
    },
]


@app.get("/health")
def health():
    return {"status": "Shard 2 Running"}


@app.get("/search")
def search(q: str):
    q = q.lower()

    return [
        doc
        for doc in DOCUMENTS
        if q in doc["title"].lower()
        or q in doc["content"].lower()
    ]