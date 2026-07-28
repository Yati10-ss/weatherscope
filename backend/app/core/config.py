from functools import lru_cache
from typing import Literal

from pydantic import HttpUrl, PositiveFloat, PositiveInt
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables or `.env`."""

    app_name: str = "WeatherScope API"
    app_version: str = "1.0.0"
    api_v1_prefix: str = "/api/v1"
    environment: Literal["development", "test", "production"] = "development"
    open_meteo_geocoding_url: HttpUrl = (
        "https://geocoding-api.open-meteo.com/v1/search"
    )
    open_meteo_forecast_url: HttpUrl = (
        "https://api.open-meteo.com/v1/forecast"
    )
    open_meteo_archive_url: HttpUrl = (
        "https://archive-api.open-meteo.com/v1/archive"
    )
    request_timeout_seconds: PositiveFloat = 10.0
    max_preview_days: PositiveInt = 31
    max_forecast_days: PositiveInt = 16
    database_url: str = "sqlite:///./weatherscope.db"
    allowed_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return one cached settings object for the process lifetime."""

    return Settings()


settings = get_settings()
