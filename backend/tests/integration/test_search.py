import httpx


def test_distributed_search():
    response = httpx.get(
        "http://127.0.0.1:8000/distributed-search",
        params={"q": "Python"},
        timeout=10.0,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["query"] == "python"
    assert data["total"] >= 1
    assert isinstance(data["results"], list)

    for result in data["results"]:
        assert "id" in result
        assert "title" in result
        assert "score" in result
        assert "shard" in result