import csv
import json
from dataclasses import dataclass
from io import StringIO
from typing import Any

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import DatabaseOperationError, WeatherSearchNotFoundError
from app.models.weather_day import WeatherDay
from app.models.weather_search import WeatherSearch
from app.repositories.weather_search_repository import WeatherSearchRepository


@dataclass(frozen=True, slots=True)
class ExportFile:
    """File content and HTTP metadata returned by an export operation."""

    filename: str
    media_type: str
    content: str


class ExportService:
    """Generate database-backed CSV and JSON exports."""

    CSV_COLUMNS = [
        "search_id",
        "original_location_input",
        "resolved_name",
        "administrative_area",
        "country",
        "country_code",
        "latitude",
        "longitude",
        "timezone",
        "start_date",
        "end_date",
        "unit_system",
        "note",
        "provider",
        "created_at",
        "updated_at",
        "retrieved_at",
        "weather_date",
        "source_type",
        "weather_code",
        "condition",
        "temperature_min",
        "temperature_max",
        "temperature_mean",
        "temperature_unit",
        "apparent_temperature_min",
        "apparent_temperature_max",
        "apparent_temperature_unit",
        "precipitation_sum",
        "precipitation_unit",
        "precipitation_probability_max",
        "precipitation_probability_unit",
        "wind_speed_max",
        "wind_speed_unit",
        "wind_gusts_max",
        "wind_gusts_unit",
        "sunrise_local",
        "sunset_local",
        "daylight_duration_seconds",
        "sunshine_duration_seconds",
    ]

    def __init__(self, repository: WeatherSearchRepository | None = None) -> None:
        self.repository = repository or WeatherSearchRepository()

    def one_json(self, *, session: Session, search_id: int) -> ExportFile:
        search = self._get_search(session=session, search_id=search_id)
        payload = self._search_payload(search)
        return ExportFile(
            filename=f"weatherscope-search-{search_id}.json",
            media_type="application/json",
            content=json.dumps(payload, indent=2, ensure_ascii=False),
        )

    def all_json(self, *, session: Session) -> ExportFile:
        searches = self._list_all(session)
        payload = {
            "exported_search_count": len(searches),
            "searches": [self._search_payload(search) for search in searches],
        }
        return ExportFile(
            filename="weatherscope-searches.json",
            media_type="application/json",
            content=json.dumps(payload, indent=2, ensure_ascii=False),
        )

    def one_csv(self, *, session: Session, search_id: int) -> ExportFile:
        search = self._get_search(session=session, search_id=search_id)
        return ExportFile(
            filename=f"weatherscope-search-{search_id}.csv",
            media_type="text/csv",
            content=self._csv_content([search]),
        )

    def all_csv(self, *, session: Session) -> ExportFile:
        searches = self._list_all(session)
        return ExportFile(
            filename="weatherscope-searches.csv",
            media_type="text/csv",
            content=self._csv_content(searches),
        )

    def _get_search(self, *, session: Session, search_id: int) -> WeatherSearch:
        try:
            search = self.repository.get_by_id(session, search_id)
        except SQLAlchemyError as exc:
            raise DatabaseOperationError() from exc
        if search is None:
            raise WeatherSearchNotFoundError(details={"search_id": search_id})
        return search

    def _list_all(self, session: Session) -> list[WeatherSearch]:
        try:
            return self.repository.list_all(session)
        except SQLAlchemyError as exc:
            raise DatabaseOperationError() from exc

    @classmethod
    def _csv_content(cls, searches: list[WeatherSearch]) -> str:
        stream = StringIO(newline="")
        writer = csv.DictWriter(stream, fieldnames=cls.CSV_COLUMNS)
        writer.writeheader()
        for search in searches:
            for day in search.days:
                writer.writerow(cls._csv_row(search, day))
        return stream.getvalue()

    @staticmethod
    def _location_payload(search: WeatherSearch) -> dict[str, Any]:
        return {
            "original_input": search.original_location_input,
            "resolved_name": search.resolved_name,
            "administrative_area": search.administrative_area,
            "secondary_administrative_area": search.secondary_administrative_area,
            "country": search.country,
            "country_code": search.country_code,
            "latitude": search.latitude,
            "longitude": search.longitude,
            "timezone": search.timezone,
        }

    @classmethod
    def _search_payload(cls, search: WeatherSearch) -> dict[str, Any]:
        return {
            "id": search.id,
            "location": cls._location_payload(search),
            "start_date": search.start_date.isoformat(),
            "end_date": search.end_date.isoformat(),
            "unit_system": search.unit_system,
            "note": search.note,
            "provider": {
                "name": search.provider,
                "latitude": search.provider_latitude,
                "longitude": search.provider_longitude,
                "elevation_m": search.elevation_m,
                "timezone_abbreviation": search.timezone_abbreviation,
                "utc_offset_seconds": search.utc_offset_seconds,
            },
            "units": {
                "temperature": search.temperature_unit,
                "apparent_temperature": search.apparent_temperature_unit,
                "precipitation": search.precipitation_unit,
                "precipitation_probability": search.precipitation_probability_unit,
                "wind_speed": search.wind_speed_unit,
                "wind_gusts": search.wind_gusts_unit,
                "daylight_duration": search.daylight_duration_unit,
                "sunshine_duration": search.sunshine_duration_unit,
            },
            "created_at": search.created_at.isoformat(),
            "updated_at": search.updated_at.isoformat(),
            "retrieved_at": search.retrieved_at.isoformat(),
            "total_days": len(search.days),
            "days": [cls._day_payload(day) for day in search.days],
        }

    @staticmethod
    def _day_payload(day: WeatherDay) -> dict[str, Any]:
        return {
            "date": day.weather_date.isoformat(),
            "source_type": day.source_type,
            "weather_code": day.weather_code,
            "condition": day.condition,
            "temperature_min": day.temperature_min,
            "temperature_max": day.temperature_max,
            "temperature_mean": day.temperature_mean,
            "apparent_temperature_min": day.apparent_temperature_min,
            "apparent_temperature_max": day.apparent_temperature_max,
            "precipitation_sum": day.precipitation_sum,
            "precipitation_probability_max": day.precipitation_probability_max,
            "wind_speed_max": day.wind_speed_max,
            "wind_gusts_max": day.wind_gusts_max,
            "sunrise_local": day.sunrise_local,
            "sunset_local": day.sunset_local,
            "daylight_duration_seconds": day.daylight_duration_seconds,
            "sunshine_duration_seconds": day.sunshine_duration_seconds,
        }

    @staticmethod
    def _csv_row(search: WeatherSearch, day: WeatherDay) -> dict[str, Any]:
        return {
            "search_id": search.id,
            "original_location_input": search.original_location_input,
            "resolved_name": search.resolved_name,
            "administrative_area": search.administrative_area,
            "country": search.country,
            "country_code": search.country_code,
            "latitude": search.latitude,
            "longitude": search.longitude,
            "timezone": search.timezone,
            "start_date": search.start_date.isoformat(),
            "end_date": search.end_date.isoformat(),
            "unit_system": search.unit_system,
            "note": search.note,
            "provider": search.provider,
            "created_at": search.created_at.isoformat(),
            "updated_at": search.updated_at.isoformat(),
            "retrieved_at": search.retrieved_at.isoformat(),
            "weather_date": day.weather_date.isoformat(),
            "source_type": day.source_type,
            "weather_code": day.weather_code,
            "condition": day.condition,
            "temperature_min": day.temperature_min,
            "temperature_max": day.temperature_max,
            "temperature_mean": day.temperature_mean,
            "temperature_unit": search.temperature_unit,
            "apparent_temperature_min": day.apparent_temperature_min,
            "apparent_temperature_max": day.apparent_temperature_max,
            "apparent_temperature_unit": search.apparent_temperature_unit,
            "precipitation_sum": day.precipitation_sum,
            "precipitation_unit": search.precipitation_unit,
            "precipitation_probability_max": day.precipitation_probability_max,
            "precipitation_probability_unit": search.precipitation_probability_unit,
            "wind_speed_max": day.wind_speed_max,
            "wind_speed_unit": search.wind_speed_unit,
            "wind_gusts_max": day.wind_gusts_max,
            "wind_gusts_unit": search.wind_gusts_unit,
            "sunrise_local": day.sunrise_local,
            "sunset_local": day.sunset_local,
            "daylight_duration_seconds": day.daylight_duration_seconds,
            "sunshine_duration_seconds": day.sunshine_duration_seconds,
        }
