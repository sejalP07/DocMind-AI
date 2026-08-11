import httpx
BASE_URL = "http://127.0.0.1:8000"
def test_metrics():
    response = httpx.get(
        f"{BASE_URL}/metrics",
        timeout=10.0,
    )
    assert response.status_code == 200
    data = response.json()
    assert "cache_hits" in data
    assert "cache_misses" in data
    assert "total_requests" in data
    assert "cache_hit_rate" in data
    assert data["cache_hits"] >= 0
    assert data["cache_misses"] >= 0
    assert data["total_requests"] >= 0
    assert 0 <= data["cache_hit_rate"] <= 1
