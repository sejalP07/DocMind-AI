import httpx


BASE_URL = "http://127.0.0.1:8000"


def test_distributed_search_with_failed_shard():
    # Use an unavailable shard URL temporarily
    # through the coordinator's configured shard list.

    response = httpx.get(
        f"{BASE_URL}/distributed-search",
        params={"q": "Python"},
        timeout=10.0,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] >= 1
    assert isinstance(data["results"], list)

    for result in data["results"]:
        assert "id" in result
        assert "shard" in result