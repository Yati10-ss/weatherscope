from app.clients.open_meteo_client import OpenMeteoClient
from app.core.exceptions import InvalidLocationQueryError, LocationNotFoundError
from app.schemas.location import LocationResult, LocationSearchResponse


class LocationService:
    def __init__(self, client: OpenMeteoClient) -> None:
        self.client = client

    async def search_locations(self, *, query: str, count: int, language: str, country_code: str | None) -> LocationSearchResponse:
        normalized_query = query.strip()
        if len(normalized_query) < 2:
            raise InvalidLocationQueryError(details={"query": query})
        normalized_country_code = country_code.upper() if country_code else None
        payload = await self.client.search_locations(
            name=normalized_query,
            count=count,
            language=language.lower(),
            country_code=normalized_country_code,
        )
        raw_results = payload.get("results", [])
        if not isinstance(raw_results, list) or not raw_results:
            raise LocationNotFoundError(details={"query": normalized_query})
        results = [self._normalize_location(item) for item in raw_results if isinstance(item, dict)]
        if not results:
            raise LocationNotFoundError(details={"query": normalized_query})
        return LocationSearchResponse(query=normalized_query, result_count=len(results), results=results)

    @staticmethod
    def _normalize_location(item: dict) -> LocationResult:
        name = str(item.get("name", "")).strip()
        admin1 = _optional_text(item.get("admin1"))
        admin2 = _optional_text(item.get("admin2"))
        country = _optional_text(item.get("country"))
        display_parts: list[str] = []
        for value in (name, admin1, country):
            if value and value not in display_parts:
                display_parts.append(value)
        return LocationResult(
            provider_id=item.get("id"),
            name=name,
            display_name=", ".join(display_parts),
            latitude=item["latitude"],
            longitude=item["longitude"],
            country=country,
            country_code=_optional_text(item.get("country_code")),
            administrative_area=admin1,
            secondary_administrative_area=admin2,
            timezone=_optional_text(item.get("timezone")),
            elevation_m=item.get("elevation"),
            population=item.get("population"),
            postcodes=item.get("postcodes") or [],
        )


def _optional_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
