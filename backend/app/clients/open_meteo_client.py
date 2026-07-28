from datetime import date
from typing import Any

import httpx

from app.core.config import settings
from app.core.exceptions import (
    GeocodingProviderError,
    GeocodingProviderTimeoutError,
    WeatherProviderError,
    WeatherProviderTimeoutError,
)


_FORECAST_DAILY_VARIABLES = (
    "weather_code,temperature_2m_max,temperature_2m_min,temperature_2m_mean,"
    "apparent_temperature_max,apparent_temperature_min,precipitation_sum,"
    "precipitation_probability_max,wind_speed_10m_max,wind_gusts_10m_max,"
    "sunrise,sunset,daylight_duration,sunshine_duration"
)

_HISTORICAL_DAILY_VARIABLES = (
    "weather_code,temperature_2m_max,temperature_2m_min,temperature_2m_mean,"
    "apparent_temperature_max,apparent_temperature_min,precipitation_sum,"
    "wind_speed_10m_max,wind_gusts_10m_max,sunrise,sunset,"
    "daylight_duration,sunshine_duration"
)


class OpenMeteoClient:
    """HTTP adapter for Open-Meteo geocoding and weather services."""

    async def search_locations(
        self,
        *,
        name: str,
        count: int,
        language: str,
        country_code: str | None,
    ) -> dict[str, Any]:
        params: dict[str, str | int] = {
            "name": name,
            "count": count,
            "language": language,
            "format": "json",
        }
        if country_code:
            params["countryCode"] = country_code

        return await self._get_json(
            url=str(settings.open_meteo_geocoding_url),
            params=params,
            timeout_error=GeocodingProviderTimeoutError,
            provider_error=GeocodingProviderError,
        )

    async def get_current_weather(
        self,
        *,
        latitude: float,
        longitude: float,
        temperature_unit: str,
        wind_speed_unit: str,
        precipitation_unit: str,
    ) -> dict[str, Any]:
        params: dict[str, str | float] = {
            "latitude": latitude,
            "longitude": longitude,
            "current": (
                "temperature_2m,relative_humidity_2m,apparent_temperature,"
                "is_day,precipitation,weather_code,wind_speed_10m,"
                "wind_direction_10m,wind_gusts_10m"
            ),
            "temperature_unit": temperature_unit,
            "wind_speed_unit": wind_speed_unit,
            "precipitation_unit": precipitation_unit,
            "timezone": "auto",
        }
        return await self._weather_get(
            url=str(settings.open_meteo_forecast_url), params=params
        )

    async def get_daily_forecast(
        self,
        *,
        latitude: float,
        longitude: float,
        forecast_days: int,
        temperature_unit: str,
        wind_speed_unit: str,
        precipitation_unit: str,
    ) -> dict[str, Any]:
        params: dict[str, str | int | float] = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": _FORECAST_DAILY_VARIABLES,
            "forecast_days": forecast_days,
            "temperature_unit": temperature_unit,
            "wind_speed_unit": wind_speed_unit,
            "precipitation_unit": precipitation_unit,
            "timezone": "auto",
        }
        return await self._weather_get(
            url=str(settings.open_meteo_forecast_url), params=params
        )

    async def get_forecast_range(
        self,
        *,
        latitude: float,
        longitude: float,
        start_date: date,
        end_date: date,
        temperature_unit: str,
        wind_speed_unit: str,
        precipitation_unit: str,
    ) -> dict[str, Any]:
        params: dict[str, str | float] = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": _FORECAST_DAILY_VARIABLES,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "temperature_unit": temperature_unit,
            "wind_speed_unit": wind_speed_unit,
            "precipitation_unit": precipitation_unit,
            "timezone": "auto",
        }
        return await self._weather_get(
            url=str(settings.open_meteo_forecast_url), params=params
        )

    async def get_historical_range(
        self,
        *,
        latitude: float,
        longitude: float,
        start_date: date,
        end_date: date,
        temperature_unit: str,
        wind_speed_unit: str,
        precipitation_unit: str,
    ) -> dict[str, Any]:
        params: dict[str, str | float] = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": _HISTORICAL_DAILY_VARIABLES,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "temperature_unit": temperature_unit,
            "wind_speed_unit": wind_speed_unit,
            "precipitation_unit": precipitation_unit,
            "timezone": "auto",
        }
        return await self._weather_get(
            url=str(settings.open_meteo_archive_url), params=params
        )

    async def _weather_get(
        self,
        *,
        url: str,
        params: dict[str, str | int | float],
    ) -> dict[str, Any]:
        return await self._get_json(
            url=url,
            params=params,
            timeout_error=WeatherProviderTimeoutError,
            provider_error=WeatherProviderError,
        )

    @staticmethod
    async def _get_json(
        *,
        url: str,
        params: dict[str, str | int | float],
        timeout_error: type[Exception],
        provider_error: type[Exception],
    ) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(
                timeout=settings.request_timeout_seconds
            ) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise timeout_error() from exc
        except (httpx.HTTPStatusError, httpx.RequestError) as exc:
            raise provider_error() from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise provider_error(
                "The external service returned an invalid JSON response."
            ) from exc

        if not isinstance(payload, dict):
            raise provider_error(
                "The external service returned an unexpected response."
            )

        return payload
