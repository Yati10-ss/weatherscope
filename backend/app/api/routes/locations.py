from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_location_service
from app.schemas.location import LocationSearchResponse
from app.services.location_service import LocationService

router = APIRouter(prefix="/locations", tags=["Locations"])


@router.get(
    "/search",
    response_model=LocationSearchResponse,
    summary="Search and validate a location",
    description="Search by city, town, place name, or postal code.",
    responses={
        400: {"description": "The search contains only whitespace."},
        404: {"description": "No matching location was found."},
        502: {"description": "The geocoding provider failed."},
        504: {"description": "The geocoding provider timed out."},
    },
)
async def search_locations(
    q: Annotated[str, Query(min_length=2, max_length=100, description="City, town, place name, or postal code.")],
    service: Annotated[LocationService, Depends(get_location_service)],
    count: Annotated[int, Query(ge=1, le=10)] = 5,
    language: Annotated[str, Query(min_length=2, max_length=2, pattern=r"^[a-z]{2}$")] = "en",
    country_code: Annotated[str | None, Query(min_length=2, max_length=2, pattern=r"^[A-Za-z]{2}$")] = None,
) -> LocationSearchResponse:
    return await service.search_locations(
        query=q,
        count=count,
        language=language,
        country_code=country_code,
    )
