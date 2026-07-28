import asyncio
from typing import Any

import pytest

from app.core.exceptions import WeatherDataUnavailableError
from app.services.weather_service import WeatherService


class FakeWeatherClient:
    async def get_current_weather(self, **_: Any) -> dict[str, Any]:
        return {
            "latitude": 39.9531,
            "longitude": -75.1641,
            "generationtime_ms": 0.08,
            "utc_offset_seconds": -14400,
            "timezone": "America/New_York",
            "timezone_abbreviation": "GMT-4",
            "elevation": 13.0,
            "current_units": {
                "time": "iso8601",
                "interval": "seconds",
                "temperature_2m": "°C",
                "relative_humidity_2m": "%",
                "apparent_temperature": "°C",
                "is_day": "",
                "precipitation": "mm",
                "weather_code": "wmo code",
                "wind_speed_10m": "km/h",
                "wind_direction_10m": "°",
                "wind_gusts_10m": "km/h",
            },
            "current": {
                "time": "2026-07-27T17:15",
                "interval": 900,
                "temperature_2m": 29.4,
                "relative_humidity_2m": 57,
                "apparent_temperature": 31.2,
                "is_day": 1,
                "precipitation": 0.0,
                "weather_code": 2,
                "wind_speed_10m": 11.5,
                "wind_direction_10m": 247,
                "wind_gusts_10m": 23.0,
            },
        }


class IncompleteWeatherClient:
    async def get_current_weather(self, **_: Any) -> dict[str, Any]:
        return {"latitude": 39.95, "longitude": -75.16}


def test_weather_service_normalizes_current_conditions() -> None:
    service = WeatherService(FakeWeatherClient())  # type: ignore[arg-type]

    result = asyncio.run(
        service.get_current_weather(
            latitude=39.95233,
            longitude=-75.16379,
            unit_system="metric",
        )
    )

    assert result.provider == "Open-Meteo"
    assert result.timezone == "America/New_York"
    assert result.units.temperature == "°C"
    assert result.current.condition == "Partly cloudy"
    assert result.current.wind_direction_cardinal == "WSW"
    assert result.current.is_day is True


def test_weather_service_rejects_incomplete_provider_data() -> None:
    service = WeatherService(IncompleteWeatherClient())  # type: ignore[arg-type]

    with pytest.raises(WeatherDataUnavailableError):
        asyncio.run(
            service.get_current_weather(
                latitude=39.95233,
                longitude=-75.16379,
                unit_system="metric",
            )
        )
