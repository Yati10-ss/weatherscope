from collections.abc import Generator
from datetime import date
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_db_session, get_weather_service
from app.core.exceptions import WeatherProviderError
from app.database.base import Base
from app.main import app
from app.models.weather_day import WeatherDay
from app.schemas.weather import (
    DailyWeatherObservation,
    DailyWeatherUnits,
    WeatherRangeResponse,
)


class FakeWeatherService:
    def __init__(self) -> None:
        self.calls = 0
        self.fail_next = False

    async def preview_date_range(self, **kwargs: Any) -> WeatherRangeResponse:
        self.calls += 1
        if self.fail_next:
            self.fail_next = False
            raise WeatherProviderError("Simulated provider failure.")

        start = kwargs["start_date"]
        end = kwargs["end_date"]
        unit_system = kwargs["unit_system"]
        imperial = unit_system == "imperial"
        return WeatherRangeResponse(
            unit_system=unit_system,
            requested_latitude=kwargs["latitude"],
            requested_longitude=kwargs["longitude"],
            provider_latitude=kwargs["latitude"],
            provider_longitude=kwargs["longitude"],
            elevation_m=12.0,
            timezone=kwargs["timezone_name"],
            timezone_abbreviation="GMT-4",
            utc_offset_seconds=-14400,
            start_date=start,
            end_date=end,
            total_days=2,
            source_types=["forecast"],
            units=DailyWeatherUnits(
                temperature="°F" if imperial else "°C",
                apparent_temperature="°F" if imperial else "°C",
                precipitation="inch" if imperial else "mm",
                precipitation_probability="%",
                wind_speed="mph" if imperial else "km/h",
                wind_gusts="mph" if imperial else "km/h",
                daylight_duration="s",
                sunshine_duration="s",
            ),
            days=[
                DailyWeatherObservation(
                    date=start,
                    source_type="forecast",
                    weather_code=2,
                    condition="Partly cloudy",
                    temperature_min=68.0 if imperial else 20.0,
                    temperature_max=86.0 if imperial else 30.0,
                    temperature_mean=77.0 if imperial else 25.0,
                    apparent_temperature_min=69.8 if imperial else 21.0,
                    apparent_temperature_max=87.8 if imperial else 31.0,
                    precipitation_sum=0.0,
                    precipitation_probability_max=10,
                    wind_speed_max=7.5 if imperial else 12.0,
                    wind_gusts_max=12.4 if imperial else 20.0,
                    sunrise_local=f"{start.isoformat()}T05:50",
                    sunset_local=f"{start.isoformat()}T20:20",
                    daylight_duration_seconds=52200.0,
                    sunshine_duration_seconds=36000.0,
                ),
                DailyWeatherObservation(
                    date=end,
                    source_type="forecast",
                    weather_code=61,
                    condition="Slight rain",
                    temperature_min=66.2 if imperial else 19.0,
                    temperature_max=80.6 if imperial else 27.0,
                    temperature_mean=73.4 if imperial else 23.0,
                    apparent_temperature_min=67.1 if imperial else 19.5,
                    apparent_temperature_max=82.4 if imperial else 28.0,
                    precipitation_sum=0.17 if imperial else 4.2,
                    precipitation_probability_max=70,
                    wind_speed_max=11.2 if imperial else 18.0,
                    wind_gusts_max=18.6 if imperial else 30.0,
                    sunrise_local=f"{end.isoformat()}T05:51",
                    sunset_local=f"{end.isoformat()}T20:19",
                    daylight_duration_seconds=52100.0,
                    sunshine_duration_seconds=24000.0,
                ),
            ],
        )


@pytest.fixture
def test_context() -> Generator[tuple[TestClient, FakeWeatherService, sessionmaker], None, None]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
        class_=Session,
    )
    Base.metadata.create_all(bind=engine)
    fake_weather = FakeWeatherService()

    def override_db() -> Generator[Session, None, None]:
        with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db_session] = override_db
    app.dependency_overrides[get_weather_service] = lambda: fake_weather
    with TestClient(app) as test_client:
        yield test_client, fake_weather, TestingSessionLocal
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def client(test_context: tuple[TestClient, FakeWeatherService, sessionmaker]) -> TestClient:
    return test_context[0]


CREATE_BODY = {
    "location": {
        "original_input": "Philadelphia",
        "resolved_name": "Philadelphia",
        "administrative_area": "Pennsylvania",
        "secondary_administrative_area": "Philadelphia County",
        "country": "United States",
        "country_code": "US",
        "latitude": 39.95233,
        "longitude": -75.16379,
        "timezone": "America/New_York",
    },
    "start_date": "2026-07-28",
    "end_date": "2026-07-29",
    "unit_system": "metric",
    "note": "Conference trip",
}


def create_record(client: TestClient) -> dict[str, Any]:
    response = client.post("/api/v1/weather-searches", json=CREATE_BODY)
    assert response.status_code == 201
    return response.json()


def test_create_weather_search_persists_parent_and_days(client: TestClient) -> None:
    payload = create_record(client)

    assert payload["id"] == 1
    assert payload["location"]["resolved_name"] == "Philadelphia"
    assert payload["location"]["country_code"] == "US"
    assert payload["total_days"] == 2
    assert len(payload["days"]) == 2
    assert payload["days"][1]["condition"] == "Slight rain"
    assert payload["note"] == "Conference trip"


def test_list_weather_searches_returns_paginated_summaries(client: TestClient) -> None:
    create_record(client)

    response = client.get("/api/v1/weather-searches")

    assert response.status_code == 200
    payload = response.json()
    assert payload["pagination"] == {
        "page": 1,
        "page_size": 10,
        "total_items": 1,
        "total_pages": 1,
    }
    assert len(payload["items"]) == 1
    assert payload["items"][0]["total_days"] == 2


def test_list_weather_searches_filters_by_location(client: TestClient) -> None:
    create_record(client)

    matched = client.get(
        "/api/v1/weather-searches", params={"location": "Pennsylvania"}
    )
    unmatched = client.get(
        "/api/v1/weather-searches", params={"location": "Chicago"}
    )

    assert matched.json()["pagination"]["total_items"] == 1
    assert unmatched.json()["pagination"]["total_items"] == 0


def test_get_weather_search_returns_full_detail(client: TestClient) -> None:
    created = create_record(client)

    response = client.get(f"/api/v1/weather-searches/{created['id']}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["units"]["temperature"] == "°C"
    assert payload["source_types"] == ["forecast"]
    assert payload["days"][0]["date"] == "2026-07-28"


def test_get_unknown_weather_search_returns_structured_404(client: TestClient) -> None:
    response = client.get("/api/v1/weather-searches/999")

    assert response.status_code == 404
    payload = response.json()
    assert payload["error"]["code"] == "WEATHER_SEARCH_NOT_FOUND"
    assert payload["error"]["details"]["search_id"] == 999


def test_create_weather_search_rejects_invalid_coordinates(client: TestClient) -> None:
    invalid = {
        **CREATE_BODY,
        "location": {**CREATE_BODY["location"], "latitude": 95},
    }

    response = client.post("/api/v1/weather-searches", json=invalid)

    assert response.status_code == 422


def test_note_only_update_does_not_call_weather_provider(
    test_context: tuple[TestClient, FakeWeatherService, sessionmaker],
) -> None:
    client, fake_weather, _ = test_context
    created = create_record(client)
    calls_after_create = fake_weather.calls

    response = client.patch(
        f"/api/v1/weather-searches/{created['id']}",
        json={"note": "Updated travel note"},
    )

    assert response.status_code == 200
    assert response.json()["note"] == "Updated travel note"
    assert fake_weather.calls == calls_after_create


def test_note_can_be_cleared_with_null(client: TestClient) -> None:
    created = create_record(client)

    response = client.patch(
        f"/api/v1/weather-searches/{created['id']}",
        json={"note": None},
    )

    assert response.status_code == 200
    assert response.json()["note"] is None


def test_date_update_refetches_and_replaces_daily_rows(
    test_context: tuple[TestClient, FakeWeatherService, sessionmaker],
) -> None:
    client, fake_weather, session_factory = test_context
    created = create_record(client)
    calls_after_create = fake_weather.calls

    response = client.patch(
        f"/api/v1/weather-searches/{created['id']}",
        json={"start_date": "2026-08-02", "end_date": "2026-08-03"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["start_date"] == "2026-08-02"
    assert payload["end_date"] == "2026-08-03"
    assert [day["date"] for day in payload["days"]] == [
        "2026-08-02",
        "2026-08-03",
    ]
    assert fake_weather.calls == calls_after_create + 1

    with session_factory() as session:
        child_count = session.scalar(select(func.count(WeatherDay.id)))
        assert child_count == 2


def test_unit_update_refetches_and_changes_units(client: TestClient) -> None:
    created = create_record(client)

    response = client.patch(
        f"/api/v1/weather-searches/{created['id']}",
        json={"unit_system": "imperial"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["unit_system"] == "imperial"
    assert payload["units"]["temperature"] == "°F"
    assert payload["days"][0]["temperature_min"] == 68.0


def test_provider_failure_leaves_existing_record_unchanged(
    test_context: tuple[TestClient, FakeWeatherService, sessionmaker],
) -> None:
    client, fake_weather, _ = test_context
    created = create_record(client)
    fake_weather.fail_next = True

    failed = client.patch(
        f"/api/v1/weather-searches/{created['id']}",
        json={"start_date": "2026-08-05", "end_date": "2026-08-06"},
    )
    preserved = client.get(f"/api/v1/weather-searches/{created['id']}")

    assert failed.status_code == 502
    assert failed.json()["error"]["code"] == "WEATHER_PROVIDER_ERROR"
    assert preserved.status_code == 200
    payload = preserved.json()
    assert payload["start_date"] == "2026-07-28"
    assert payload["end_date"] == "2026-07-29"
    assert payload["note"] == "Conference trip"


def test_empty_update_payload_is_rejected(client: TestClient) -> None:
    created = create_record(client)

    response = client.patch(
        f"/api/v1/weather-searches/{created['id']}",
        json={},
    )

    assert response.status_code == 422


def test_update_unknown_weather_search_returns_structured_404(
    client: TestClient,
) -> None:
    response = client.patch(
        "/api/v1/weather-searches/999",
        json={"note": "Nothing"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "WEATHER_SEARCH_NOT_FOUND"


def test_delete_weather_search_removes_parent_and_children(
    test_context: tuple[TestClient, FakeWeatherService, sessionmaker],
) -> None:
    client, _, session_factory = test_context
    created = create_record(client)

    response = client.delete(f"/api/v1/weather-searches/{created['id']}")
    missing = client.get(f"/api/v1/weather-searches/{created['id']}")

    assert response.status_code == 204
    assert response.content == b""
    assert missing.status_code == 404
    with session_factory() as session:
        child_count = session.scalar(select(func.count(WeatherDay.id)))
        assert child_count == 0


def test_delete_unknown_weather_search_returns_structured_404(
    client: TestClient,
) -> None:
    response = client.delete("/api/v1/weather-searches/999")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "WEATHER_SEARCH_NOT_FOUND"
