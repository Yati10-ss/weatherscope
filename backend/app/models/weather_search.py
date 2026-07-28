from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class WeatherSearch(Base):
    """One saved location and date-range weather request."""

    __tablename__ = "weather_searches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    original_location_input: Mapped[str] = mapped_column(String(120))
    resolved_name: Mapped[str] = mapped_column(String(120), index=True)
    administrative_area: Mapped[str | None] = mapped_column(String(120), nullable=True)
    secondary_administrative_area: Mapped[str | None] = mapped_column(
        String(120), nullable=True
    )
    country: Mapped[str | None] = mapped_column(String(120), nullable=True)
    country_code: Mapped[str | None] = mapped_column(String(2), nullable=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    timezone: Mapped[str] = mapped_column(String(80))

    start_date: Mapped[date] = mapped_column(Date, index=True)
    end_date: Mapped[date] = mapped_column(Date, index=True)
    unit_system: Mapped[str] = mapped_column(String(10))
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    provider: Mapped[str] = mapped_column(String(50), default="Open-Meteo")
    provider_latitude: Mapped[float] = mapped_column(Float)
    provider_longitude: Mapped[float] = mapped_column(Float)
    elevation_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    timezone_abbreviation: Mapped[str | None] = mapped_column(String(20), nullable=True)
    utc_offset_seconds: Mapped[int] = mapped_column(Integer)

    temperature_unit: Mapped[str] = mapped_column(String(20))
    apparent_temperature_unit: Mapped[str] = mapped_column(String(20))
    precipitation_unit: Mapped[str] = mapped_column(String(20))
    precipitation_probability_unit: Mapped[str] = mapped_column(String(20))
    wind_speed_unit: Mapped[str] = mapped_column(String(20))
    wind_gusts_unit: Mapped[str] = mapped_column(String(20))
    daylight_duration_unit: Mapped[str] = mapped_column(String(20))
    sunshine_duration_unit: Mapped[str] = mapped_column(String(20))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )
    retrieved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )

    days: Mapped[list[WeatherDay]] = relationship(
        back_populates="search",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="WeatherDay.weather_date",
    )
