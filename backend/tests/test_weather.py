from typing import Any

from fastapi.testclient import TestClient

from app.api.dependencies import get_weather_service
from app.main import app
from app.schemas.weather import (
    CurrentWeatherObservation,
    CurrentWeatherResponse,
    CurrentWeatherUnits,
)


client = TestClient(app)


class SuccessfulWeatherService:
    async def get_current_weather(self, **_: Any) -> CurrentWeatherResponse:
        return CurrentWeatherResponse(
            unit_system="metric",
            requested_latitude=39.95233,
            requested_longitude=-75.16379,
            provider_latitude=39.9531,
            provider_longitude=-75.1641,
            elevation_m=13.0,
            timezone="America/New_York",
            timezone_abbreviation="GMT-4",
            utc_offset_seconds=-14400,
            units=CurrentWeatherUnits(
                temperature="°C",
                apparent_temperature="°C",
                relative_humidity="%",
                precipitation="mm",
                wind_speed="km/h",
                wind_direction="°",
                wind_gusts="km/h",
            ),
            current=CurrentWeatherObservation(
                observed_at_local="2026-07-27T17:15",
                interval_seconds=900,
                temperature=29.4,
                apparent_temperature=31.2,
                relative_humidity_percent=57,
                is_day=True,
                precipitation=0.0,
                weather_code=2,
                condition="Partly cloudy",
                wind_speed=11.5,
                wind_direction_degrees=247,
                wind_direction_cardinal="WSW",
                wind_gusts=23.0,
            ),
        )


def test_current_weather_endpoint_returns_normalized_payload() -> None:
    app.dependency_overrides[get_weather_service] = (
        lambda: SuccessfulWeatherService()
    )
    try:
        response = client.get(
            "/api/v1/weather/current",
            params={
                "latitude": 39.95233,
                "longitude": -75.16379,
                "unit_system": "metric",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["current"]["condition"] == "Partly cloudy"
    assert payload["current"]["relative_humidity_percent"] == 57
    assert payload["units"]["temperature"] == "°C"


def test_current_weather_endpoint_rejects_invalid_latitude() -> None:
    response = client.get(
        "/api/v1/weather/current",
        params={"latitude": 91, "longitude": -75.16},
    )

    assert response.status_code == 422


def test_current_weather_endpoint_rejects_invalid_unit_system() -> None:
    response = client.get(
        "/api/v1/weather/current",
        params={
            "latitude": 39.95,
            "longitude": -75.16,
            "unit_system": "kelvin",
        },
    )

    assert response.status_code == 422
