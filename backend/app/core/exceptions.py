from typing import Any


class AppError(Exception):
    """Base exception for predictable application errors."""

    status_code = 500
    code = "INTERNAL_ERROR"
    default_message = "An unexpected error occurred."

    def __init__(
        self,
        message: str | None = None,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message or self.default_message
        self.details = details or {}
        super().__init__(self.message)


class InvalidLocationQueryError(AppError):
    status_code = 400
    code = "INVALID_LOCATION_QUERY"
    default_message = "Enter at least two non-space characters for the location."


class LocationNotFoundError(AppError):
    status_code = 404
    code = "LOCATION_NOT_FOUND"
    default_message = "No matching location was found."


class GeocodingProviderError(AppError):
    status_code = 502
    code = "GEOCODING_PROVIDER_ERROR"
    default_message = "The location service is temporarily unavailable."


class GeocodingProviderTimeoutError(AppError):
    status_code = 504
    code = "GEOCODING_PROVIDER_TIMEOUT"
    default_message = "The location service took too long to respond."


class InvalidDateRangeError(AppError):
    status_code = 400
    code = "INVALID_DATE_RANGE"
    default_message = "The requested date range is invalid."


class UnsupportedDateRangeError(AppError):
    status_code = 400
    code = "UNSUPPORTED_DATE_RANGE"
    default_message = "The requested date range is not supported."


class InvalidTimezoneError(AppError):
    status_code = 400
    code = "INVALID_TIMEZONE"
    default_message = "The timezone must be a valid IANA timezone name."


class WeatherProviderError(AppError):
    status_code = 502
    code = "WEATHER_PROVIDER_ERROR"
    default_message = "The weather service is temporarily unavailable."


class WeatherProviderTimeoutError(AppError):
    status_code = 504
    code = "WEATHER_PROVIDER_TIMEOUT"
    default_message = "The weather service took too long to respond."


class WeatherDataUnavailableError(AppError):
    status_code = 502
    code = "WEATHER_DATA_UNAVAILABLE"
    default_message = "The weather service returned incomplete data."


class WeatherSearchNotFoundError(AppError):
    status_code = 404
    code = "WEATHER_SEARCH_NOT_FOUND"
    default_message = "The saved weather search was not found."


class DatabaseOperationError(AppError):
    status_code = 500
    code = "DATABASE_OPERATION_ERROR"
    default_message = "The database operation could not be completed."
