from datetime import date, datetime
from typing import Self

from pydantic import BaseModel, Field, field_validator, model_validator

from app.schemas.weather import DailyWeatherObservation, DailyWeatherUnits, UnitSystem


class SavedLocationInput(BaseModel):
    original_input: str = Field(min_length=1, max_length=120)
    resolved_name: str = Field(min_length=1, max_length=120)
    administrative_area: str | None = Field(default=None, max_length=120)
    secondary_administrative_area: str | None = Field(default=None, max_length=120)
    country: str | None = Field(default=None, max_length=120)
    country_code: str | None = Field(default=None, min_length=2, max_length=2)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    timezone: str = Field(min_length=1, max_length=80)

    @field_validator("original_input", "resolved_name", "timezone")
    @classmethod
    def normalize_required_text(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Value must contain non-space characters.")
        return stripped

    @field_validator(
        "administrative_area",
        "secondary_administrative_area",
        "country",
    )
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None

    @field_validator("country_code")
    @classmethod
    def normalize_country_code(cls, value: str | None) -> str | None:
        return value.upper() if value else None


class WeatherSearchCreate(BaseModel):
    location: SavedLocationInput
    start_date: date
    end_date: date
    unit_system: UnitSystem = "metric"
    note: str | None = Field(default=None, max_length=500)

    @field_validator("note")
    @classmethod
    def normalize_note(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class WeatherSearchUpdate(BaseModel):
    """Partial update for a saved search.

    Supplying location, either date, or the unit system triggers a fresh provider
    request. Supplying only note updates database metadata without an API call.
    """

    location: SavedLocationInput | None = None
    start_date: date | None = None
    end_date: date | None = None
    unit_system: UnitSystem | None = None
    note: str | None = Field(default=None, max_length=500)

    @field_validator("note")
    @classmethod
    def normalize_note(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None

    @model_validator(mode="after")
    def validate_partial_update(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("Provide at least one field to update.")

        for field_name in ("location", "start_date", "end_date", "unit_system"):
            if field_name in self.model_fields_set and getattr(self, field_name) is None:
                raise ValueError(f"'{field_name}' cannot be null.")
        return self


class SavedLocationResponse(SavedLocationInput):
    pass


class WeatherSearchSummary(BaseModel):
    id: int
    location: SavedLocationResponse
    start_date: date
    end_date: date
    total_days: int
    unit_system: UnitSystem
    note: str | None
    provider: str
    created_at: datetime
    updated_at: datetime
    retrieved_at: datetime


class WeatherSearchDetail(WeatherSearchSummary):
    provider_latitude: float
    provider_longitude: float
    elevation_m: float | None
    timezone_abbreviation: str | None
    utc_offset_seconds: int
    units: DailyWeatherUnits
    source_types: list[str]
    days: list[DailyWeatherObservation]


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int


class WeatherSearchListResponse(BaseModel):
    items: list[WeatherSearchSummary]
    pagination: PaginationMeta
