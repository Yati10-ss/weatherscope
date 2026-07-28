from datetime import datetime, timezone
from math import ceil

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import DatabaseOperationError, WeatherSearchNotFoundError
from app.models.weather_day import WeatherDay
from app.models.weather_search import WeatherSearch
from app.repositories.weather_search_repository import WeatherSearchRepository
from app.schemas.weather import (
    DailyWeatherObservation,
    DailyWeatherUnits,
    WeatherRangeResponse,
)
from app.schemas.weather_search import (
    PaginationMeta,
    SavedLocationInput,
    SavedLocationResponse,
    WeatherSearchCreate,
    WeatherSearchDetail,
    WeatherSearchListResponse,
    WeatherSearchSummary,
    WeatherSearchUpdate,
)
from app.services.weather_service import WeatherService


class WeatherSearchService:
    """Coordinate weather retrieval with persistent CRUD operations."""

    def __init__(
        self,
        weather_service: WeatherService,
        repository: WeatherSearchRepository | None = None,
    ) -> None:
        self.weather_service = weather_service
        self.repository = repository or WeatherSearchRepository()

    async def create(
        self,
        *,
        session: Session,
        request: WeatherSearchCreate,
    ) -> WeatherSearchDetail:
        weather = await self._retrieve_weather(
            location=request.location,
            start_date=request.start_date,
            end_date=request.end_date,
            unit_system=request.unit_system,
        )

        now = datetime.now(timezone.utc)
        search = WeatherSearch(
            original_location_input=request.location.original_input,
            resolved_name=request.location.resolved_name,
            administrative_area=request.location.administrative_area,
            secondary_administrative_area=(
                request.location.secondary_administrative_area
            ),
            country=request.location.country,
            country_code=request.location.country_code,
            latitude=request.location.latitude,
            longitude=request.location.longitude,
            timezone=request.location.timezone,
            start_date=request.start_date,
            end_date=request.end_date,
            unit_system=request.unit_system,
            note=request.note,
            created_at=now,
            updated_at=now,
            retrieved_at=now,
            **self._provider_fields(weather),
        )
        search.days = [self._day_model(day) for day in weather.days]

        try:
            self.repository.add(session, search)
            session.commit()
        except SQLAlchemyError as exc:
            session.rollback()
            raise DatabaseOperationError() from exc

        stored = self.repository.get_by_id(session, search.id)
        if stored is None:
            raise DatabaseOperationError()
        return self._detail(stored)

    def get(self, *, session: Session, search_id: int) -> WeatherSearchDetail:
        search = self._get_model(session=session, search_id=search_id)
        return self._detail(search)

    def list(
        self,
        *,
        session: Session,
        page: int,
        page_size: int,
        location: str | None,
    ) -> WeatherSearchListResponse:
        try:
            items, total = self.repository.list(
                session,
                page=page,
                page_size=page_size,
                location=location,
            )
        except SQLAlchemyError as exc:
            raise DatabaseOperationError() from exc

        total_pages = ceil(total / page_size) if total else 0
        return WeatherSearchListResponse(
            items=[self._summary(item) for item in items],
            pagination=PaginationMeta(
                page=page,
                page_size=page_size,
                total_items=total,
                total_pages=total_pages,
            ),
        )

    async def update(
        self,
        *,
        session: Session,
        search_id: int,
        request: WeatherSearchUpdate,
    ) -> WeatherSearchDetail:
        search = self._get_model(session=session, search_id=search_id)

        effective_location = request.location or self._location_input(search)
        effective_start_date = request.start_date or search.start_date
        effective_end_date = request.end_date or search.end_date
        effective_unit_system = request.unit_system or search.unit_system

        weather_fields_supplied = bool(
            request.model_fields_set
            & {"location", "start_date", "end_date", "unit_system"}
        )
        weather_values_changed = (
            self._location_changed(search, effective_location)
            or effective_start_date != search.start_date
            or effective_end_date != search.end_date
            or effective_unit_system != search.unit_system
        )

        # Retrieve before mutating the tracked entity. If the provider fails, the
        # original database record and child rows remain untouched.
        weather: WeatherRangeResponse | None = None
        if weather_fields_supplied and weather_values_changed:
            weather = await self._retrieve_weather(
                location=effective_location,
                start_date=effective_start_date,
                end_date=effective_end_date,
                unit_system=effective_unit_system,  # type: ignore[arg-type]
            )

        any_change = weather_values_changed
        if "note" in request.model_fields_set and request.note != search.note:
            search.note = request.note
            any_change = True

        if weather is not None:
            self._apply_location(search, effective_location)
            search.start_date = effective_start_date
            search.end_date = effective_end_date
            search.unit_system = effective_unit_system
            self._apply_provider_fields(search, weather)
            self.repository.replace_days(
                session,
                search=search,
                days=[self._day_model(day) for day in weather.days],
            )
            search.retrieved_at = datetime.now(timezone.utc)

        if not any_change:
            return self._detail(search)

        search.updated_at = datetime.now(timezone.utc)
        try:
            session.commit()
        except SQLAlchemyError as exc:
            session.rollback()
            raise DatabaseOperationError() from exc

        stored = self.repository.get_by_id(session, search_id)
        if stored is None:
            raise DatabaseOperationError()
        return self._detail(stored)

    def delete(self, *, session: Session, search_id: int) -> None:
        search = self._get_model(session=session, search_id=search_id)
        try:
            self.repository.delete(session, search)
            session.commit()
        except SQLAlchemyError as exc:
            session.rollback()
            raise DatabaseOperationError() from exc

    async def _retrieve_weather(
        self,
        *,
        location: SavedLocationInput,
        start_date,
        end_date,
        unit_system,
    ) -> WeatherRangeResponse:
        return await self.weather_service.preview_date_range(
            latitude=location.latitude,
            longitude=location.longitude,
            start_date=start_date,
            end_date=end_date,
            unit_system=unit_system,
            timezone_name=location.timezone,
        )

    def _get_model(self, *, session: Session, search_id: int) -> WeatherSearch:
        try:
            search = self.repository.get_by_id(session, search_id)
        except SQLAlchemyError as exc:
            raise DatabaseOperationError() from exc
        if search is None:
            raise WeatherSearchNotFoundError(details={"search_id": search_id})
        return search

    @staticmethod
    def _provider_fields(weather: WeatherRangeResponse) -> dict:
        return {
            "provider": weather.provider,
            "provider_latitude": weather.provider_latitude,
            "provider_longitude": weather.provider_longitude,
            "elevation_m": weather.elevation_m,
            "timezone_abbreviation": weather.timezone_abbreviation,
            "utc_offset_seconds": weather.utc_offset_seconds,
            "temperature_unit": weather.units.temperature,
            "apparent_temperature_unit": weather.units.apparent_temperature,
            "precipitation_unit": weather.units.precipitation,
            "precipitation_probability_unit": (
                weather.units.precipitation_probability
            ),
            "wind_speed_unit": weather.units.wind_speed,
            "wind_gusts_unit": weather.units.wind_gusts,
            "daylight_duration_unit": weather.units.daylight_duration,
            "sunshine_duration_unit": weather.units.sunshine_duration,
        }

    @classmethod
    def _apply_provider_fields(
        cls,
        search: WeatherSearch,
        weather: WeatherRangeResponse,
    ) -> None:
        for field_name, value in cls._provider_fields(weather).items():
            setattr(search, field_name, value)

    @staticmethod
    def _apply_location(
        search: WeatherSearch,
        location: SavedLocationInput,
    ) -> None:
        search.original_location_input = location.original_input
        search.resolved_name = location.resolved_name
        search.administrative_area = location.administrative_area
        search.secondary_administrative_area = (
            location.secondary_administrative_area
        )
        search.country = location.country
        search.country_code = location.country_code
        search.latitude = location.latitude
        search.longitude = location.longitude
        search.timezone = location.timezone

    @staticmethod
    def _location_input(search: WeatherSearch) -> SavedLocationInput:
        return SavedLocationInput(
            original_input=search.original_location_input,
            resolved_name=search.resolved_name,
            administrative_area=search.administrative_area,
            secondary_administrative_area=search.secondary_administrative_area,
            country=search.country,
            country_code=search.country_code,
            latitude=search.latitude,
            longitude=search.longitude,
            timezone=search.timezone,
        )

    @staticmethod
    def _location_changed(
        search: WeatherSearch,
        location: SavedLocationInput,
    ) -> bool:
        return any(
            (
                location.original_input != search.original_location_input,
                location.resolved_name != search.resolved_name,
                location.administrative_area != search.administrative_area,
                location.secondary_administrative_area
                != search.secondary_administrative_area,
                location.country != search.country,
                location.country_code != search.country_code,
                location.latitude != search.latitude,
                location.longitude != search.longitude,
                location.timezone != search.timezone,
            )
        )

    @staticmethod
    def _day_model(day: DailyWeatherObservation) -> WeatherDay:
        return WeatherDay(
            weather_date=day.date,
            source_type=day.source_type,
            weather_code=day.weather_code,
            condition=day.condition,
            temperature_min=day.temperature_min,
            temperature_max=day.temperature_max,
            temperature_mean=day.temperature_mean,
            apparent_temperature_min=day.apparent_temperature_min,
            apparent_temperature_max=day.apparent_temperature_max,
            precipitation_sum=day.precipitation_sum,
            precipitation_probability_max=day.precipitation_probability_max,
            wind_speed_max=day.wind_speed_max,
            wind_gusts_max=day.wind_gusts_max,
            sunrise_local=day.sunrise_local,
            sunset_local=day.sunset_local,
            daylight_duration_seconds=day.daylight_duration_seconds,
            sunshine_duration_seconds=day.sunshine_duration_seconds,
        )

    @staticmethod
    def _location(search: WeatherSearch) -> SavedLocationResponse:
        return SavedLocationResponse(
            original_input=search.original_location_input,
            resolved_name=search.resolved_name,
            administrative_area=search.administrative_area,
            secondary_administrative_area=search.secondary_administrative_area,
            country=search.country,
            country_code=search.country_code,
            latitude=search.latitude,
            longitude=search.longitude,
            timezone=search.timezone,
        )

    @classmethod
    def _summary(cls, search: WeatherSearch) -> WeatherSearchSummary:
        return WeatherSearchSummary(
            id=search.id,
            location=cls._location(search),
            start_date=search.start_date,
            end_date=search.end_date,
            total_days=len(search.days),
            unit_system=search.unit_system,  # type: ignore[arg-type]
            note=search.note,
            provider=search.provider,
            created_at=search.created_at,
            updated_at=search.updated_at,
            retrieved_at=search.retrieved_at,
        )

    @classmethod
    def _detail(cls, search: WeatherSearch) -> WeatherSearchDetail:
        source_types: list[str] = []
        days = []
        for day in search.days:
            if day.source_type not in source_types:
                source_types.append(day.source_type)
            days.append(
                DailyWeatherObservation(
                    date=day.weather_date,
                    source_type=day.source_type,  # type: ignore[arg-type]
                    weather_code=day.weather_code,
                    condition=day.condition,
                    temperature_min=day.temperature_min,
                    temperature_max=day.temperature_max,
                    temperature_mean=day.temperature_mean,
                    apparent_temperature_min=day.apparent_temperature_min,
                    apparent_temperature_max=day.apparent_temperature_max,
                    precipitation_sum=day.precipitation_sum,
                    precipitation_probability_max=(
                        day.precipitation_probability_max
                    ),
                    wind_speed_max=day.wind_speed_max,
                    wind_gusts_max=day.wind_gusts_max,
                    sunrise_local=day.sunrise_local,
                    sunset_local=day.sunset_local,
                    daylight_duration_seconds=day.daylight_duration_seconds,
                    sunshine_duration_seconds=day.sunshine_duration_seconds,
                )
            )

        summary = cls._summary(search)
        return WeatherSearchDetail(
            **summary.model_dump(),
            provider_latitude=search.provider_latitude,
            provider_longitude=search.provider_longitude,
            elevation_m=search.elevation_m,
            timezone_abbreviation=search.timezone_abbreviation,
            utc_offset_seconds=search.utc_offset_seconds,
            units=DailyWeatherUnits(
                temperature=search.temperature_unit,
                apparent_temperature=search.apparent_temperature_unit,
                precipitation=search.precipitation_unit,
                precipitation_probability=(
                    search.precipitation_probability_unit
                ),
                wind_speed=search.wind_speed_unit,
                wind_gusts=search.wind_gusts_unit,
                daylight_duration=search.daylight_duration_unit,
                sunshine_duration=search.sunshine_duration_unit,
            ),
            source_types=source_types,
            days=days,
        )
