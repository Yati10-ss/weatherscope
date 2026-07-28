import asyncio
from datetime import date, timedelta
from typing import Any

import pytest

from app.core.exceptions import WeatherDataUnavailableError
from app.services.date_range_service import DateSegment
from app.services.weather_service import WeatherService


def _daily_payload(start: date, count: int, *, probability: bool = True) -> dict[str, Any]:
    dates = [(start + timedelta(days=index)).isoformat() for index in range(count)]
    daily: dict[str, Any] = {
        "time": dates,
        "weather_code": [2] * count,
        "temperature_2m_max": [28.0 + index for index in range(count)],
        "temperature_2m_min": [19.0 + index for index in range(count)],
        "temperature_2m_mean": [23.5 + index for index in range(count)],
        "apparent_temperature_max": [29.0 + index for index in range(count)],
        "apparent_temperature_min": [19.5 + index for index in range(count)],
        "precipitation_sum": [0.0] * count,
        "wind_speed_10m_max": [17.0] * count,
        "wind_gusts_10m_max": [28.0] * count,
        "sunrise": [f"{day}T05:50" for day in dates],
        "sunset": [f"{day}T20:20" for day in dates],
        "daylight_duration": [52200.0] * count,
        "sunshine_duration": [36000.0] * count,
    }
    if probability:
        daily["precipitation_probability_max"] = [20] * count
    return {
        "latitude": 39.96,
        "longitude": -75.15,
        "utc_offset_seconds": -14400,
        "timezone": "America/New_York",
        "timezone_abbreviation": "GMT-4",
        "elevation": 12,
        "daily_units": {
            "temperature_2m_max": "°C",
            "apparent_temperature_max": "°C",
            "precipitation_sum": "mm",
            "precipitation_probability_max": "%",
            "wind_speed_10m_max": "km/h",
            "wind_gusts_10m_max": "km/h",
            "daylight_duration": "s",
            "sunshine_duration": "s",
        },
        "daily": daily,
    }


class ForecastClient:
    async def get_daily_forecast(self, **_: Any) -> dict[str, Any]:
        return _daily_payload(date(2026, 7, 28), 5)


class MixedClient:
    async def get_historical_range(self, **kwargs: Any) -> dict[str, Any]:
        return _daily_payload(kwargs["start_date"], 1, probability=False)

    async def get_forecast_range(self, **kwargs: Any) -> dict[str, Any]:
        return _daily_payload(kwargs["start_date"], 2)


class FixedMixedDateRangeService:
    def split_range(self, **_: Any) -> list[DateSegment]:
        return [
            DateSegment("historical", date(2026, 7, 26), date(2026, 7, 26)),
            DateSegment("forecast", date(2026, 7, 27), date(2026, 7, 28)),
        ]


class MismatchedClient:
    async def get_daily_forecast(self, **_: Any) -> dict[str, Any]:
        payload = _daily_payload(date(2026, 7, 28), 3)
        payload["daily"]["temperature_2m_max"] = [28.0]
        return payload


def test_weather_service_normalizes_five_day_forecast() -> None:
    service = WeatherService(ForecastClient())  # type: ignore[arg-type]
    result = asyncio.run(
        service.get_daily_forecast(
            latitude=39.95,
            longitude=-75.16,
            days=5,
            unit_system="metric",
        )
    )
    assert result.total_days == 5
    assert result.source_types == ["forecast"]
    assert result.days[0].condition == "Partly cloudy"
    assert result.days[0].precipitation_probability_max == 20


def test_weather_service_merges_historical_and_forecast_days() -> None:
    service = WeatherService(
        MixedClient(),  # type: ignore[arg-type]
        FixedMixedDateRangeService(),  # type: ignore[arg-type]
    )
    result = asyncio.run(
        service.preview_date_range(
            latitude=39.95,
            longitude=-75.16,
            start_date=date(2026, 7, 26),
            end_date=date(2026, 7, 28),
            unit_system="metric",
            timezone_name="America/New_York",
        )
    )
    assert result.total_days == 3
    assert result.source_types == ["historical", "forecast"]
    assert result.days[0].precipitation_probability_max is None
    assert result.days[-1].source_type == "forecast"


def test_weather_service_rejects_mismatched_daily_arrays() -> None:
    service = WeatherService(MismatchedClient())  # type: ignore[arg-type]
    with pytest.raises(WeatherDataUnavailableError):
        asyncio.run(
            service.get_daily_forecast(
                latitude=39.95,
                longitude=-75.16,
                days=3,
                unit_system="metric",
            )
        )
