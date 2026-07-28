from datetime import date, timedelta

import pytest

from app.core.exceptions import InvalidDateRangeError, UnsupportedDateRangeError
from app.services.date_range_service import DateRangeService


def test_date_range_service_splits_mixed_range() -> None:
    service = DateRangeService()
    today = date.today()
    segments = service.split_range(
        start_date=today - timedelta(days=1),
        end_date=today + timedelta(days=1),
        timezone_name=None,
    )
    assert [segment.source_type for segment in segments] == ["historical", "forecast"]
    assert segments[0].end_date == today - timedelta(days=1)
    assert segments[1].start_date == today


def test_date_range_service_rejects_reversed_range() -> None:
    service = DateRangeService()
    with pytest.raises(InvalidDateRangeError):
        service.split_range(
            start_date=date(2026, 8, 5),
            end_date=date(2026, 8, 1),
            timezone_name=None,
        )


def test_date_range_service_rejects_excessive_range() -> None:
    service = DateRangeService()
    today = date.today()
    with pytest.raises(UnsupportedDateRangeError):
        service.split_range(
            start_date=today - timedelta(days=31),
            end_date=today,
            timezone_name=None,
        )
