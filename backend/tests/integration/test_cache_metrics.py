import httpx


BASE_URL = "http://127.0.0.1:8000"


def test_cache_metrics():
    first_response = httpx.get(
        f"{BASE_URL}/distributed-search",
        params={"q": "CacheMetricsTest"},
        timeout=10.0,
    )

    assert first_response.status_code == 200

    first_data = first_response.json()

    assert first_data["cache_hit"] is False
    assert first_data["cache_misses"] >= 1

    second_response = httpx.get(
        f"{BASE_URL}/distributed-search",
        params={"q": "CacheMetricsTest"},
        timeout=10.0,
    )

    assert second_response.status_code == 200

    second_data = second_response.json()

    assert second_data["cache_hit"] is True
    assert second_data["cache_hits"] >= 1