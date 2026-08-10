import httpx


def test_main_api_health():
    response = httpx.get(
        "http://127.0.0.1:8000/health"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"