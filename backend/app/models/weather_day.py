from __future__ import annotations

from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class WeatherDay(Base):
    """One daily weather observation belonging to a saved search."""

    __tablename__ = "weather_days"
    __table_args__ = (
        UniqueConstraint("search_id", "weather_date", name="uq_search_weather_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    search_id: Mapped[int] = mapped_column(
        ForeignKey("weather_searches.id", ondelete="CASCADE"),
        index=True,
    )
    weather_date: Mapped[date] = mapped_column(Date, index=True)
    source_type: Mapped[str] = mapped_column(String(20))
    weather_code: Mapped[int] = mapped_column(Integer)
    condition: Mapped[str] = mapped_column(String(80))
    temperature_min: Mapped[float] = mapped_column(Float)
    temperature_max: Mapped[float] = mapped_column(Float)
    temperature_mean: Mapped[float | None] = mapped_column(Float, nullable=True)
    apparent_temperature_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    apparent_temperature_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    precipitation_sum: Mapped[float] = mapped_column(Float)
    precipitation_probability_max: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    wind_speed_max: Mapped[float] = mapped_column(Float)
    wind_gusts_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    sunrise_local: Mapped[str | None] = mapped_column(String(40), nullable=True)
    sunset_local: Mapped[str | None] = mapped_column(String(40), nullable=True)
    daylight_duration_seconds: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    sunshine_duration_seconds: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )

    search: Mapped[WeatherSearch] = relationship(back_populates="days")
