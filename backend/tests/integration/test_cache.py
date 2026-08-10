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

    assert first.json() == second.json()