from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check_returns_expected_payload() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert payload["application"] == "WeatherScope API"
    assert payload["version"] == "1.0.0"
