from fastapi.testclient import TestClient

from tests.test_weather_searches import (
    client,  # imported pytest fixture
    create_record,
    test_context,  # imported dependency fixture
)


def test_query_validation_uses_consistent_error_envelope(client: TestClient) -> None:
    response = client.get("/api/v1/locations/search", params={"q": "P"})

    assert response.status_code == 422
    payload = response.json()
    assert payload["error"]["code"] == "VALIDATION_ERROR"
    assert payload["error"]["message"] == "The request contains invalid values."
    assert payload["error"]["details"]["errors"][0]["loc"] == ["query", "q"]


def test_body_validation_uses_consistent_error_envelope(client: TestClient) -> None:
    created = create_record(client)

    response = client.patch(
        f"/api/v1/weather-searches/{created['id']}",
        json={},
    )

    assert response.status_code == 422
    payload = response.json()
    assert payload["error"]["code"] == "VALIDATION_ERROR"
    assert payload["error"]["details"]["errors"]


def test_cors_preflight_allows_local_react_frontend(client: TestClient) -> None:
    response = client.options(
        "/api/v1/weather/current",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == (
        "http://localhost:5173"
    )
