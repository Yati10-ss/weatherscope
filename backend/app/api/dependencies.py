from typing import Annotated

from fastapi import Depends

from app.clients.open_meteo_client import OpenMeteoClient
from app.database.session import get_db_session
from app.repositories.weather_search_repository import WeatherSearchRepository
from app.services.export_service import ExportService
from app.services.location_service import LocationService
from app.services.weather_search_service import WeatherSearchService
from app.services.weather_service import WeatherService


def get_location_service() -> LocationService:
    return LocationService(OpenMeteoClient())


def get_weather_service() -> WeatherService:
    return WeatherService(OpenMeteoClient())


def get_weather_search_service(
    weather_service: Annotated[WeatherService, Depends(get_weather_service)],
) -> WeatherSearchService:
    return WeatherSearchService(
        weather_service=weather_service,
        repository=WeatherSearchRepository(),
    )


def get_export_service() -> ExportService:
    return ExportService(repository=WeatherSearchRepository())


__all__ = [
    "get_db_session",
    "get_export_service",
    "get_location_service",
    "get_weather_service",
    "get_weather_search_service",
]
