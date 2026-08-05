from fastapi import FastAPI

app = FastAPI(title="Shard 3")

DOCUMENTS = [
    {
        "id": 5,
        "title": "Artificial Intelligence",
        "content": "Machine Learning Deep Learning LLM",
        "url": "https://doc5.com",
    },
    {
        "id": 6,
        "title": "Data Science",
        "content": "Pandas NumPy Scikit-Learn",
        "url": "https://doc6.com",
    },
]


@app.get("/health")
def health():
    return {"status": "Shard 3 Running"}


@app.get("/search")
def search(q: str):
    q = q.lower()

    return [
        doc
        for doc in DOCUMENTS
        if q in doc["title"].lower()
        or q in doc["content"].lower()
    ]