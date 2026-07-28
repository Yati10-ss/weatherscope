from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.core.config import settings
from app.core.exceptions import (
    InvalidDateRangeError,
    InvalidTimezoneError,
    UnsupportedDateRangeError,
)


EARLIEST_HISTORICAL_DATE = date(1940, 1, 1)


@dataclass(frozen=True)
class DateSegment:
    source_type: str
    start_date: date
    end_date: date


class DateRangeService:
    """Validate an inclusive date range and route it to weather data sources."""

    def split_range(
        self,
        *,
        start_date: date,
        end_date: date,
        timezone_name: str | None,
    ) -> list[DateSegment]:
        today = self._today(timezone_name)
        self._validate(start_date=start_date, end_date=end_date, today=today)

        segments: list[DateSegment] = []
        yesterday = today - timedelta(days=1)

        if start_date <= yesterday:
            segments.append(
                DateSegment(
                    source_type="historical",
                    start_date=start_date,
                    end_date=min(end_date, yesterday),
                )
            )

        if end_date >= today:
            segments.append(
                DateSegment(
                    source_type="forecast",
                    start_date=max(start_date, today),
                    end_date=end_date,
                )
            )

        return segments

    @staticmethod
    def _today(timezone_name: str | None) -> date:
        if timezone_name is None:
            return datetime.now(timezone.utc).date()
        try:
            return datetime.now(ZoneInfo(timezone_name)).date()
        except ZoneInfoNotFoundError as exc:
            raise InvalidTimezoneError(
                details={"timezone": timezone_name}
            ) from exc

    @staticmethod
    def _validate(*, start_date: date, end_date: date, today: date) -> None:
        if start_date > end_date:
            raise InvalidDateRangeError(
                "The start date must not be later than the end date.",
                details={
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                },
            )

        inclusive_days = (end_date - start_date).days + 1
        if inclusive_days > settings.max_preview_days:
            raise UnsupportedDateRangeError(
                f"A preview may contain at most {settings.max_preview_days} days.",
                details={
                    "requested_days": inclusive_days,
                    "maximum_days": settings.max_preview_days,
                },
            )

        if start_date < EARLIEST_HISTORICAL_DATE:
            raise UnsupportedDateRangeError(
                "Historical weather is available from 1940-01-01 onward.",
                details={"earliest_date": EARLIEST_HISTORICAL_DATE.isoformat()},
            )

        latest_forecast_date = today + timedelta(
            days=settings.max_forecast_days - 1
        )
        if end_date > latest_forecast_date:
            raise UnsupportedDateRangeError(
                f"Forecast dates may extend at most {settings.max_forecast_days} days including today.",
                details={
                    "latest_supported_date": latest_forecast_date.isoformat(),
                    "requested_end_date": end_date.isoformat(),
                },
            )
