from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


UnitSystem = Literal["metric", "imperial"]
DailySourceType = Literal["forecast", "historical"]


class CurrentWeatherUnits(BaseModel):
    temperature: str
    apparent_temperature: str
    relative_humidity: str
    precipitation: str
    wind_speed: str
    wind_direction: str
    wind_gusts: str


class CurrentWeatherObservation(BaseModel):
    observed_at_local: str
    interval_seconds: int = Field(gt=0)
    temperature: float
    apparent_temperature: float
    relative_humidity_percent: int = Field(ge=0, le=100)
    is_day: bool
    precipitation: float = Field(ge=0)
    weather_code: int
    condition: str
    wind_speed: float = Field(ge=0)
    wind_direction_degrees: int = Field(ge=0, le=360)
    wind_direction_cardinal: str
    wind_gusts: float = Field(ge=0)


class CurrentWeatherResponse(BaseModel):
    provider: Literal["Open-Meteo"] = "Open-Meteo"
    unit_system: UnitSystem
    requested_latitude: float = Field(ge=-90, le=90)
    requested_longitude: float = Field(ge=-180, le=180)
    provider_latitude: float = Field(ge=-90, le=90)
    provider_longitude: float = Field(ge=-180, le=180)
    elevation_m: float | None = None
    timezone: str
    timezone_abbreviation: str | None = None
    utc_offset_seconds: int
    units: CurrentWeatherUnits
    current: CurrentWeatherObservation


class DailyWeatherUnits(BaseModel):
    temperature: str
    apparent_temperature: str
    precipitation: str
    precipitation_probability: str
    wind_speed: str
    wind_gusts: str
    daylight_duration: str
    sunshine_duration: str


class DailyWeatherObservation(BaseModel):
    date: date
    source_type: DailySourceType
    weather_code: int
    condition: str
    temperature_min: float
    temperature_max: float
    temperature_mean: float | None = None
    apparent_temperature_min: float | None = None
    apparent_temperature_max: float | None = None
    precipitation_sum: float = Field(ge=0)
    precipitation_probability_max: int | None = Field(default=None, ge=0, le=100)
    wind_speed_max: float = Field(ge=0)
    wind_gusts_max: float | None = Field(default=None, ge=0)
    sunrise_local: str | None = None
    sunset_local: str | None = None
    daylight_duration_seconds: float | None = Field(default=None, ge=0)
    sunshine_duration_seconds: float | None = Field(default=None, ge=0)


class WeatherRangeResponse(BaseModel):
    provider: Literal["Open-Meteo"] = "Open-Meteo"
    unit_system: UnitSystem
    requested_latitude: float = Field(ge=-90, le=90)
    requested_longitude: float = Field(ge=-180, le=180)
    provider_latitude: float = Field(ge=-90, le=90)
    provider_longitude: float = Field(ge=-180, le=180)
    elevation_m: float | None = None
    timezone: str
    timezone_abbreviation: str | None = None
    utc_offset_seconds: int
    start_date: date
    end_date: date
    total_days: int = Field(gt=0)
    source_types: list[DailySourceType]
    units: DailyWeatherUnits
    days: list[DailyWeatherObservation]


class WeatherPreviewRequest(BaseModel):
    latitude: float = Field(ge=-90, le=90, examples=[39.95233])
    longitude: float = Field(ge=-180, le=180, examples=[-75.16379])
    start_date: date
    end_date: date
    unit_system: UnitSystem = "metric"
    timezone: str | None = Field(
        default=None,
        description=(
            "Optional IANA timezone from the selected location, for example "
            "America/New_York. UTC is used for date routing when omitted."
        ),
        examples=["America/New_York"],
    )
