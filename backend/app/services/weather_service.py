import asyncio
from datetime import date
from typing import Any

from app.clients.open_meteo_client import OpenMeteoClient
from app.core.exceptions import WeatherDataUnavailableError
from app.schemas.weather import (
    CurrentWeatherObservation,
    CurrentWeatherResponse,
    CurrentWeatherUnits,
    DailySourceType,
    DailyWeatherObservation,
    DailyWeatherUnits,
    UnitSystem,
    WeatherRangeResponse,
)
from app.services.date_range_service import DateRangeService, DateSegment
from app.utils.weather_codes import degrees_to_cardinal, weather_code_to_label


_UNIT_PARAMETERS = {
    "metric": {
        "temperature_unit": "celsius",
        "wind_speed_unit": "kmh",
        "precipitation_unit": "mm",
    },
    "imperial": {
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "mph",
        "precipitation_unit": "inch",
    },
}

_REQUIRED_DAILY_FIELDS = {
    "time",
    "weather_code",
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "wind_speed_10m_max",
}


class WeatherService:
    """Retrieve, route, merge, and normalize weather-provider responses."""

    def __init__(
        self,
        client: OpenMeteoClient,
        date_range_service: DateRangeService | None = None,
    ) -> None:
        self.client = client
        self.date_range_service = date_range_service or DateRangeService()

    async def get_current_weather(
        self,
        *,
        latitude: float,
        longitude: float,
        unit_system: UnitSystem,
    ) -> CurrentWeatherResponse:
        unit_parameters = _UNIT_PARAMETERS[unit_system]
        payload = await self.client.get_current_weather(
            latitude=latitude,
            longitude=longitude,
            **unit_parameters,
        )
        return self._normalize_current_weather(
            payload=payload,
            requested_latitude=latitude,
            requested_longitude=longitude,
            unit_system=unit_system,
        )

    async def get_daily_forecast(
        self,
        *,
        latitude: float,
        longitude: float,
        days: int,
        unit_system: UnitSystem,
    ) -> WeatherRangeResponse:
        payload = await self.client.get_daily_forecast(
            latitude=latitude,
            longitude=longitude,
            forecast_days=days,
            **_UNIT_PARAMETERS[unit_system],
        )
        return self._normalize_daily_weather(
            payload=payload,
            requested_latitude=latitude,
            requested_longitude=longitude,
            unit_system=unit_system,
            source_type="forecast",
        )

    async def preview_date_range(
        self,
        *,
        latitude: float,
        longitude: float,
        start_date: date,
        end_date: date,
        unit_system: UnitSystem,
        timezone_name: str | None,
    ) -> WeatherRangeResponse:
        segments = self.date_range_service.split_range(
            start_date=start_date,
            end_date=end_date,
            timezone_name=timezone_name,
        )
        payloads = await asyncio.gather(
            *[
                self._retrieve_segment(
                    segment=segment,
                    latitude=latitude,
                    longitude=longitude,
                    unit_system=unit_system,
                )
                for segment in segments
            ]
        )
        responses = [
            self._normalize_daily_weather(
                payload=payload,
                requested_latitude=latitude,
                requested_longitude=longitude,
                unit_system=unit_system,
                source_type=segment.source_type,  # type: ignore[arg-type]
            )
            for segment, payload in zip(segments, payloads, strict=True)
        ]
        return self._merge_range_responses(responses)

    async def _retrieve_segment(
        self,
        *,
        segment: DateSegment,
        latitude: float,
        longitude: float,
        unit_system: UnitSystem,
    ) -> dict[str, Any]:
        kwargs = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": segment.start_date,
            "end_date": segment.end_date,
            **_UNIT_PARAMETERS[unit_system],
        }
        if segment.source_type == "historical":
            return await self.client.get_historical_range(**kwargs)
        return await self.client.get_forecast_range(**kwargs)

    @staticmethod
    def _normalize_current_weather(
        *,
        payload: dict[str, Any],
        requested_latitude: float,
        requested_longitude: float,
        unit_system: UnitSystem,
    ) -> CurrentWeatherResponse:
        current = payload.get("current")
        units = payload.get("current_units")
        if not isinstance(current, dict) or not isinstance(units, dict):
            raise WeatherDataUnavailableError()

        required_current = {
            "time", "interval", "temperature_2m", "relative_humidity_2m",
            "apparent_temperature", "is_day", "precipitation", "weather_code",
            "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m",
        }
        required_root = {"latitude", "longitude", "timezone", "utc_offset_seconds"}
        missing = sorted((required_current - current.keys()) | (required_root - payload.keys()))
        if missing:
            raise WeatherDataUnavailableError(details={"missing_fields": missing})

        weather_code = int(current["weather_code"])
        wind_direction = int(round(float(current["wind_direction_10m"]))) % 360

        return CurrentWeatherResponse(
            unit_system=unit_system,
            requested_latitude=requested_latitude,
            requested_longitude=requested_longitude,
            provider_latitude=float(payload["latitude"]),
            provider_longitude=float(payload["longitude"]),
            elevation_m=float(payload["elevation"]) if payload.get("elevation") is not None else None,
            timezone=str(payload["timezone"]),
            timezone_abbreviation=str(payload["timezone_abbreviation"]) if payload.get("timezone_abbreviation") is not None else None,
            utc_offset_seconds=int(payload["utc_offset_seconds"]),
            units=CurrentWeatherUnits(
                temperature=str(units.get("temperature_2m", "")),
                apparent_temperature=str(units.get("apparent_temperature", "")),
                relative_humidity=str(units.get("relative_humidity_2m", "%")),
                precipitation=str(units.get("precipitation", "")),
                wind_speed=str(units.get("wind_speed_10m", "")),
                wind_direction=str(units.get("wind_direction_10m", "°")),
                wind_gusts=str(units.get("wind_gusts_10m", "")),
            ),
            current=CurrentWeatherObservation(
                observed_at_local=str(current["time"]),
                interval_seconds=int(current["interval"]),
                temperature=float(current["temperature_2m"]),
                apparent_temperature=float(current["apparent_temperature"]),
                relative_humidity_percent=int(current["relative_humidity_2m"]),
                is_day=bool(current["is_day"]),
                precipitation=float(current["precipitation"]),
                weather_code=weather_code,
                condition=weather_code_to_label(weather_code),
                wind_speed=float(current["wind_speed_10m"]),
                wind_direction_degrees=wind_direction,
                wind_direction_cardinal=degrees_to_cardinal(wind_direction),
                wind_gusts=float(current["wind_gusts_10m"]),
            ),
        )

    @classmethod
    def _normalize_daily_weather(
        cls,
        *,
        payload: dict[str, Any],
        requested_latitude: float,
        requested_longitude: float,
        unit_system: UnitSystem,
        source_type: DailySourceType,
    ) -> WeatherRangeResponse:
        daily = payload.get("daily")
        units = payload.get("daily_units")
        required_root = {"latitude", "longitude", "timezone", "utc_offset_seconds"}
        if not isinstance(daily, dict) or not isinstance(units, dict):
            raise WeatherDataUnavailableError()

        missing = sorted((_REQUIRED_DAILY_FIELDS - daily.keys()) | (required_root - payload.keys()))
        if missing:
            raise WeatherDataUnavailableError(details={"missing_fields": missing})

        dates = daily["time"]
        if not isinstance(dates, list) or not dates:
            raise WeatherDataUnavailableError(details={"field": "daily.time"})

        for field in _REQUIRED_DAILY_FIELDS:
            values = daily[field]
            if not isinstance(values, list) or len(values) != len(dates):
                raise WeatherDataUnavailableError(
                    details={"field": f"daily.{field}", "expected_length": len(dates)}
                )

        observations = [
            DailyWeatherObservation(
                date=day,
                source_type=source_type,
                weather_code=int(daily["weather_code"][index]),
                condition=weather_code_to_label(int(daily["weather_code"][index])),
                temperature_min=float(daily["temperature_2m_min"][index]),
                temperature_max=float(daily["temperature_2m_max"][index]),
                temperature_mean=cls._optional_float(daily, "temperature_2m_mean", index),
                apparent_temperature_min=cls._optional_float(daily, "apparent_temperature_min", index),
                apparent_temperature_max=cls._optional_float(daily, "apparent_temperature_max", index),
                precipitation_sum=float(daily["precipitation_sum"][index]),
                precipitation_probability_max=cls._optional_int(daily, "precipitation_probability_max", index),
                wind_speed_max=float(daily["wind_speed_10m_max"][index]),
                wind_gusts_max=cls._optional_float(daily, "wind_gusts_10m_max", index),
                sunrise_local=cls._optional_str(daily, "sunrise", index),
                sunset_local=cls._optional_str(daily, "sunset", index),
                daylight_duration_seconds=cls._optional_float(daily, "daylight_duration", index),
                sunshine_duration_seconds=cls._optional_float(daily, "sunshine_duration", index),
            )
            for index, day in enumerate(dates)
        ]

        return WeatherRangeResponse(
            unit_system=unit_system,
            requested_latitude=requested_latitude,
            requested_longitude=requested_longitude,
            provider_latitude=float(payload["latitude"]),
            provider_longitude=float(payload["longitude"]),
            elevation_m=float(payload["elevation"]) if payload.get("elevation") is not None else None,
            timezone=str(payload["timezone"]),
            timezone_abbreviation=str(payload["timezone_abbreviation"]) if payload.get("timezone_abbreviation") is not None else None,
            utc_offset_seconds=int(payload["utc_offset_seconds"]),
            start_date=observations[0].date,
            end_date=observations[-1].date,
            total_days=len(observations),
            source_types=[source_type],
            units=DailyWeatherUnits(
                temperature=str(units.get("temperature_2m_max", "")),
                apparent_temperature=str(units.get("apparent_temperature_max", "")),
                precipitation=str(units.get("precipitation_sum", "")),
                precipitation_probability=str(units.get("precipitation_probability_max", "%")),
                wind_speed=str(units.get("wind_speed_10m_max", "")),
                wind_gusts=str(units.get("wind_gusts_10m_max", "")),
                daylight_duration=str(units.get("daylight_duration", "s")),
                sunshine_duration=str(units.get("sunshine_duration", "s")),
            ),
            days=observations,
        )

    @staticmethod
    def _merge_range_responses(responses: list[WeatherRangeResponse]) -> WeatherRangeResponse:
        if not responses:
            raise WeatherDataUnavailableError()
        base = responses[0]
        by_date = {
            observation.date: observation
            for response in responses
            for observation in response.days
        }
        days = [by_date[key] for key in sorted(by_date)]
        source_types: list[DailySourceType] = []
        for observation in days:
            if observation.source_type not in source_types:
                source_types.append(observation.source_type)
        return base.model_copy(
            update={
                "start_date": days[0].date,
                "end_date": days[-1].date,
                "total_days": len(days),
                "source_types": source_types,
                "days": days,
            }
        )

    @staticmethod
    def _optional_value(daily: dict[str, Any], key: str, index: int) -> Any | None:
        values = daily.get(key)
        if not isinstance(values, list) or index >= len(values):
            return None
        return values[index]

    @classmethod
    def _optional_float(cls, daily: dict[str, Any], key: str, index: int) -> float | None:
        value = cls._optional_value(daily, key, index)
        return None if value is None else float(value)

    @classmethod
    def _optional_int(cls, daily: dict[str, Any], key: str, index: int) -> int | None:
        value = cls._optional_value(daily, key, index)
        return None if value is None else int(value)

    @classmethod
    def _optional_str(cls, daily: dict[str, Any], key: str, index: int) -> str | None:
        value = cls._optional_value(daily, key, index)
        return None if value is None else str(value)
