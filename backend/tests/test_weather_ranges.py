from datetime import date, timedelta
from typing import Any

from fastapi.testclient import TestClient

from app.api.dependencies import get_weather_service
from app.main import app
from app.schemas.weather import (
    DailyWeatherObservation,
    DailyWeatherUnits,
    WeatherRangeResponse,
)


client = TestClient(app)


def _range_response(start: date, count: int = 5) -> WeatherRangeResponse:
    days = [
        DailyWeatherObservation(
            date=start + timedelta(days=index),
            source_type="forecast",
            weather_code=2,
            condition="Partly cloudy",
            temperature_min=20 + index,
            temperature_max=28 + index,
            temperature_mean=24 + index,
            apparent_temperature_min=20 + index,
            apparent_temperature_max=29 + index,
            precipitation_sum=0.5,
            precipitation_probability_max=20,
            wind_speed_max=18,
            wind_gusts_max=30,
            sunrise_local=f"{start + timedelta(days=index)}T05:50",
            sunset_local=f"{start + timedelta(days=index)}T20:20",
            daylight_duration_seconds=52200,
            sunshine_duration_seconds=36000,
        )
        for index in range(count)
    ]
    return WeatherRangeResponse(
        unit_system="metric",
        requested_latitude=39.95,
        requested_longitude=-75.16,
        provider_latitude=39.96,
        provider_longitude=-75.15,
        elevation_m=12,
        timezone="America/New_York",
        timezone_abbreviation="GMT-4",
        utc_offset_seconds=-14400,
        start_date=days[0].date,
        end_date=days[-1].date,
        total_days=len(days),
        source_types=["forecast"],
        units=DailyWeatherUnits(
            temperature="°C",
            apparent_temperature="°C",
            precipitation="mm",
            precipitation_probability="%",
            wind_speed="km/h",
            wind_gusts="km/h",
            daylight_duration="s",
            sunshine_duration="s",
        ),
        days=days,
    )


class SuccessfulRangeService:
    async def get_daily_forecast(self, **_: Any) -> WeatherRangeResponse:
        return _range_response(date(2026, 7, 28))

    async def preview_date_range(self, **_: Any) -> WeatherRangeResponse:
        return _range_response(date(2026, 7, 28), count=3)


def test_five_day_forecast_endpoint() -> None:
    app.dependency_overrides[get_weather_service] = lambda: SuccessfulRangeService()
    try:
        response = client.get(
            "/api/v1/weather/forecast",
            params={"latitude": 39.95, "longitude": -75.16},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_days"] == 5
    assert len(payload["days"]) == 5
    assert payload["days"][0]["condition"] == "Partly cloudy"


def test_preview_endpoint_accepts_date_range_body() -> None:
    app.dependency_overrides[get_weather_service] = lambda: SuccessfulRangeService()
    try:
        response = client.post(
            "/api/v1/weather/preview",
            json={
                "latitude": 39.95,
                "longitude": -75.16,
                "start_date": "2026-07-28",
                "end_date": "2026-07-30",
                "unit_system": "metric",
                "timezone": "America/New_York",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["total_days"] == 3


def test_forecast_endpoint_rejects_more_than_sixteen_days() -> None:
    response = client.get(
        "/api/v1/weather/forecast",
        params={"latitude": 39.95, "longitude": -75.16, "days": 17},
    )
    assert response.status_code == 422
