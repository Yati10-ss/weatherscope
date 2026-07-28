from typing import Any

from fastapi.testclient import TestClient

from app.api.dependencies import get_location_service
from app.core.exceptions import LocationNotFoundError
from app.main import app
from app.schemas.location import LocationResult, LocationSearchResponse

client = TestClient(app)


class SuccessfulLocationService:
    async def search_locations(self, *, query: str, count: int, language: str, country_code: str | None) -> LocationSearchResponse:
        return LocationSearchResponse(
            query=query.strip(),
            result_count=1,
            results=[LocationResult(
                provider_id=4560349,
                name="Philadelphia",
                display_name="Philadelphia, Pennsylvania, United States",
                latitude=39.95233,
                longitude=-75.16379,
                country="United States",
                country_code="US",
                administrative_area="Pennsylvania",
                timezone="America/New_York",
                elevation_m=12.0,
                population=1603797,
                postcodes=["19104"],
            )],
        )


class MissingLocationService:
    async def search_locations(self, **_: Any) -> LocationSearchResponse:
        raise LocationNotFoundError(details={"query": "NoSuchPlace"})


def test_location_search_returns_normalized_result() -> None:
    app.dependency_overrides[get_location_service] = lambda: SuccessfulLocationService()
    try:
        response = client.get("/api/v1/locations/search", params={"q": "Philadelphia", "country_code": "US"})
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    payload = response.json()
    assert payload["result_count"] == 1
    assert payload["results"][0]["country_code"] == "US"
    assert payload["results"][0]["timezone"] == "America/New_York"


def test_location_search_rejects_one_character_query() -> None:
    response = client.get("/api/v1/locations/search", params={"q": "P"})
    assert response.status_code == 422


def test_location_search_returns_structured_not_found_error() -> None:
    app.dependency_overrides[get_location_service] = lambda: MissingLocationService()
    try:
        response = client.get("/api/v1/locations/search", params={"q": "NoSuchPlace"})
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 404
    payload = response.json()
    assert payload["error"]["code"] == "LOCATION_NOT_FOUND"


def test_location_search_rejects_invalid_country_code() -> None:
    response = client.get("/api/v1/locations/search", params={"q": "Paris", "country_code": "USA"})
    assert response.status_code == 422
