import csv
import io
import json

from fastapi.testclient import TestClient

from tests.test_weather_searches import (
    CREATE_BODY,
    client,  # imported pytest fixture
    create_record,
    test_context,  # imported dependency fixture
)


def test_export_one_json_downloads_nested_database_data(client: TestClient) -> None:
    created = create_record(client)

    response = client.get(
        f"/api/v1/exports/weather-searches/{created['id']}.json"
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert response.headers["content-disposition"] == (
        'attachment; filename="weatherscope-search-1.json"'
    )
    payload = response.json()
    assert payload["id"] == created["id"]
    assert payload["location"]["resolved_name"] == "Philadelphia"
    assert payload["total_days"] == 2
    assert payload["days"][1]["condition"] == "Slight rain"


def test_export_one_csv_returns_one_row_per_weather_day(client: TestClient) -> None:
    created = create_record(client)

    response = client.get(
        f"/api/v1/exports/weather-searches/{created['id']}.csv"
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert response.headers["content-disposition"] == (
        'attachment; filename="weatherscope-search-1.csv"'
    )
    rows = list(csv.DictReader(io.StringIO(response.text)))
    assert len(rows) == 2
    assert rows[0]["resolved_name"] == "Philadelphia"
    assert rows[0]["temperature_unit"] == "°C"
    assert rows[1]["weather_date"] == "2026-07-29"
    assert rows[1]["condition"] == "Slight rain"


def test_export_all_json_contains_every_saved_search(client: TestClient) -> None:
    create_record(client)
    second_body = {
        **CREATE_BODY,
        "location": {
            **CREATE_BODY["location"],
            "original_input": "New York",
            "resolved_name": "New York",
            "administrative_area": "New York",
            "latitude": 40.7128,
            "longitude": -74.006,
        },
        "note": "Second record",
    }
    second = client.post("/api/v1/weather-searches", json=second_body)
    assert second.status_code == 201

    response = client.get("/api/v1/exports/weather-searches.json")

    assert response.status_code == 200
    payload = json.loads(response.text)
    assert payload["exported_search_count"] == 2
    assert {item["location"]["resolved_name"] for item in payload["searches"]} == {
        "Philadelphia",
        "New York",
    }


def test_export_all_csv_on_empty_database_returns_header_only(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/exports/weather-searches.csv")

    assert response.status_code == 200
    rows = list(csv.DictReader(io.StringIO(response.text)))
    assert rows == []
    assert "search_id" in response.text.splitlines()[0]


def test_export_unknown_search_returns_structured_404(client: TestClient) -> None:
    response = client.get("/api/v1/exports/weather-searches/999.json")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "WEATHER_SEARCH_NOT_FOUND"
