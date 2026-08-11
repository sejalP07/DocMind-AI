import httpx

BASE_URL = "http://127.0.0.1:8000"
SHARD_2_URL = "http://shard2:8002"


def test_shard_recovery():
    # 1. Verify Shard 2 is healthy again
    health_response = httpx.get(
        f"{SHARD_2_URL}/health",
        timeout=5.0,
    )

    assert health_response.status_code == 200

    health_data = health_response.json()

    assert health_data["status"] == "healthy"
    assert health_data["shard"] == 2

    # 2. Perform distributed search through API container
    response = httpx.get(
        f"{BASE_URL}/distributed-search",
        params={
            "q": "Python",
            "page": 1,
            "page_size": 10,
        },
        timeout=15.0,
    )

    assert response.status_code == 200

    data = response.json()

    # 3. Search should no longer be partial
    assert data["partial"] is False
    assert data["failed_shards"] == []

    # 4. Results should exist
    assert data["total"] >= 1
    assert isinstance(data["results"], list)

    # 5. Verify recovered Shard 2 participates
    shard_ids = {
        result["shard"]
        for result in data["results"]
    }

    assert 2 in shard_ids
