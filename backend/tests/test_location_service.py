import asyncio
from typing import Any

from app.services.location_service import LocationService


class FakeOpenMeteoClient:
    async def search_locations(self, **_: Any) -> dict[str, Any]:
        return {"results": [{
            "id": 2950159,
            "name": "Berlin",
            "latitude": 52.52437,
            "longitude": 13.41053,
            "elevation": 74.0,
            "country_code": "DE",
            "timezone": "Europe/Berlin",
            "population": 3426354,
            "postcodes": ["10967", "13347"],
            "country": "Germany",
            "admin1": "Berlin",
        }]}


def test_location_service_normalizes_provider_response() -> None:
    service = LocationService(FakeOpenMeteoClient())  # type: ignore[arg-type]
    result = asyncio.run(service.search_locations(query=" Berlin ", count=5, language="en", country_code="de"))
    assert result.query == "Berlin"
    assert result.results[0].display_name == "Berlin, Germany"
    assert result.results[0].country_code == "DE"
