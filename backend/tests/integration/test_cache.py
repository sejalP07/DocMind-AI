import time
import httpx


BASE_URL = "http://127.0.0.1:8000"


def test_search_cache():
    query = f"python-{time.time()}"

    first = httpx.get(
        f"{BASE_URL}/distributed-search",
        params={"q": query},
        timeout=10.0,
    )

    assert first.status_code == 200

    second = httpx.get(
        f"{BASE_URL}/distributed-search",
        params={"q": query},
        timeout=10.0,
    )

    assert second.status_code == 200

    first_data = first.json()
    second_data = second.json()

    assert first_data["query"] == second_data["query"]
    assert first_data["total"] == second_data["total"]
    assert first_data["partial"] == second_data["partial"]
    assert first_data["failed_shards"] == second_data["failed_shards"]
    assert first_data["results"] == second_data["results"]

    assert first_data["cache_hit"] is False
    assert second_data["cache_hit"] is True