from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session, get_weather_search_service
from app.schemas.weather_search import (
    WeatherSearchCreate,
    WeatherSearchDetail,
    WeatherSearchListResponse,
    WeatherSearchUpdate,
)
from app.services.weather_search_service import WeatherSearchService


router = APIRouter(prefix="/weather-searches", tags=["Weather Searches"])


@router.post(
    "",
    response_model=WeatherSearchDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Create and save a weather search",
    description=(
        "Retrieves validated weather data for a resolved location and inclusive "
        "date range, then stores the search and one related row per weather day."
    ),
    responses={
        400: {"description": "The date range or timezone is invalid."},
        502: {"description": "The weather provider failed."},
        504: {"description": "The weather provider timed out."},
    },
)
async def create_weather_search(
    request: WeatherSearchCreate,
    session: Annotated[Session, Depends(get_db_session)],
    service: Annotated[WeatherSearchService, Depends(get_weather_search_service)],
) -> WeatherSearchDetail:
    return await service.create(session=session, request=request)


@router.get(
    "",
    response_model=WeatherSearchListResponse,
    summary="List saved weather searches",
    description=(
        "Returns paginated saved-search summaries, ordered from newest to oldest. "
        "An optional location filter searches the original and resolved location fields."
    ),
)
def list_weather_searches(
    session: Annotated[Session, Depends(get_db_session)],
    service: Annotated[WeatherSearchService, Depends(get_weather_search_service)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 10,
    location: Annotated[str | None, Query(min_length=1, max_length=120)] = None,
) -> WeatherSearchListResponse:
    return service.list(
        session=session,
        page=page,
        page_size=page_size,
        location=location,
    )


@router.get(
    "/{search_id}",
    response_model=WeatherSearchDetail,
    summary="Read one saved weather search",
    responses={404: {"description": "The saved weather search does not exist."}},
)
def get_weather_search(
    search_id: Annotated[int, Path(ge=1)],
    session: Annotated[Session, Depends(get_db_session)],
    service: Annotated[WeatherSearchService, Depends(get_weather_search_service)],
) -> WeatherSearchDetail:
    return service.get(session=session, search_id=search_id)


@router.patch(
    "/{search_id}",
    response_model=WeatherSearchDetail,
    summary="Update a saved weather search",
    description=(
        "Updates the note directly. Changing the resolved location, date range, or "
        "unit system retrieves fresh weather and atomically replaces the stored days."
    ),
    responses={
        404: {"description": "The saved weather search does not exist."},
        400: {"description": "The revised date range or timezone is invalid."},
        502: {"description": "The weather provider failed."},
        504: {"description": "The weather provider timed out."},
    },
)
async def update_weather_search(
    search_id: int,
    request: WeatherSearchUpdate,
    session: Annotated[Session, Depends(get_db_session)],
    service: Annotated[WeatherSearchService, Depends(get_weather_search_service)],
) -> WeatherSearchDetail:
    return await service.update(
        session=session,
        search_id=search_id,
        request=request,
    )


@router.delete(
    "/{search_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a saved weather search",
    description=(
        "Permanently deletes the selected search and all related daily weather rows."
    ),
    responses={404: {"description": "The saved weather search does not exist."}},
)
def delete_weather_search(
    search_id: int,
    session: Annotated[Session, Depends(get_db_session)],
    service: Annotated[WeatherSearchService, Depends(get_weather_search_service)],
) -> Response:
    service.delete(session=session, search_id=search_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
