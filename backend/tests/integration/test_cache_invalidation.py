import time
import httpx


BASE_URL = "http://127.0.0.1:8000"


def test_document_creation_invalidates_cache():
    query = f"cachetest{int(time.time())}"

    # 1. First search creates a cached result
    first = httpx.get(
        f"{BASE_URL}/distributed-search",
        params={"q": query},
        timeout=10.0,
    )

    assert first.status_code == 200

    first_data = first.json()

    # 2. Search again - should come from cache
    second = httpx.get(
        f"{BASE_URL}/distributed-search",
        params={"q": query},
        timeout=10.0,
    )

    assert second.status_code == 200
    assert second.json() == first_data

    # 3. Create a document containing the query
    document = {
        "title": "Cache Invalidation Test",
        "content": f"This document contains {query}",
        "url": f"https://example.com/{query}",
    }

    create_response = httpx.post(
        f"{BASE_URL}/documents",
        json=document,
        timeout=10.0,
    )

    assert create_response.status_code == 200

    created = create_response.json()

    assert created["title"] == "Cache Invalidation Test"

    # 4. Search again after document creation
    third = httpx.get(
        f"{BASE_URL}/distributed-search",
        params={"q": query},
        timeout=10.0,
    )

    assert third.status_code == 200

    third_data = third.json()

    # 5. New document must now appear
    assert third_data["total"] >= 1

    ids = [
        result["id"]
        for result in third_data["results"]
    ]

    assert created["id"] in ids