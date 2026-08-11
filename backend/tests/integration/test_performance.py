import time
import httpx

BASE_URL = "http://127.0.0.1:8000"


def test_search_performance():
    query = f"performance-{time.time()}"

    start = time.perf_counter()

    response = httpx.get(
        f"{BASE_URL}/distributed-search",
        params={"q": query},
        timeout=10.0,
    )

    elapsed = (time.perf_counter() - start) * 1000

    assert response.status_code == 200

    data = response.json()

    assert "total_latency_ms" in data
    assert "shard_latency_ms" in data

    print(f"\nTotal request latency: {elapsed:.2f} ms")
    print(f"Coordinator latency: {data['total_latency_ms']} ms")
    print(f"Shard latency: {data['shard_latency_ms']}")

    assert elapsed < 3000