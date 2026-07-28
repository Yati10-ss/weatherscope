from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_weather_service
from app.core.config import settings
from app.schemas.weather import (
    CurrentWeatherResponse,
    UnitSystem,
    WeatherPreviewRequest,
    WeatherRangeResponse,
)
from app.services.weather_service import WeatherService


router = APIRouter(prefix="/weather", tags=["Weather"])


@router.get(
    "/current",
    response_model=CurrentWeatherResponse,
    summary="Get current weather by coordinates",
    description=(
        "Returns current conditions for validated latitude and longitude. "
        "Use the location-search endpoint first when the user enters a place name."
    ),
    responses={
        502: {"description": "The weather provider failed or returned incomplete data."},
        504: {"description": "The weather provider timed out."},
    },
)
async def get_current_weather(
    latitude: Annotated[float, Query(ge=-90, le=90, examples=[39.95233])],
    longitude: Annotated[float, Query(ge=-180, le=180, examples=[-75.16379])],
    service: Annotated[WeatherService, Depends(get_weather_service)],
    unit_system: Annotated[UnitSystem, Query(description="Use metric or imperial display units.")] = "metric",
) -> CurrentWeatherResponse:
    return await service.get_current_weather(
        latitude=latitude,
        longitude=longitude,
        unit_system=unit_system,
    )


@router.get(
    "/forecast",
    response_model=WeatherRangeResponse,
    summary="Get a daily weather forecast",
    description="Returns one to sixteen forecast days. Five days are returned by default.",
    responses={
        502: {"description": "The weather provider failed or returned incomplete data."},
        504: {"description": "The weather provider timed out."},
    },
)
async def get_daily_forecast(
    latitude: Annotated[float, Query(ge=-90, le=90, examples=[39.95233])],
    longitude: Annotated[float, Query(ge=-180, le=180, examples=[-75.16379])],
    service: Annotated[WeatherService, Depends(get_weather_service)],
    days: Annotated[int, Query(ge=1, le=settings.max_forecast_days)] = 5,
    unit_system: Annotated[UnitSystem, Query(description="Use metric or imperial display units.")] = "metric",
) -> WeatherRangeResponse:
    return await service.get_daily_forecast(
        latitude=latitude,
        longitude=longitude,
        days=days,
        unit_system=unit_system,
    )


@router.post(
    "/preview",
    response_model=WeatherRangeResponse,
    summary="Preview weather for an inclusive date range",
    description=(
        "Validates the requested dates, routes past dates to historical weather, "
        "routes current/future dates to forecast weather, and merges mixed ranges. "
        "The preview is not saved to the database."
    ),
    responses={
        400: {"description": "The date range or timezone is invalid or unsupported."},
        502: {"description": "The weather provider failed or returned incomplete data."},
        504: {"description": "The weather provider timed out."},
    },
)
async def preview_weather(
    request: WeatherPreviewRequest,
    service: Annotated[WeatherService, Depends(get_weather_service)],
) -> WeatherRangeResponse:
    return await service.preview_date_range(
        latitude=request.latitude,
        longitude=request.longitude,
        start_date=request.start_date,
        end_date=request.end_date,
        unit_system=request.unit_system,
        timezone_name=request.timezone,
    )
