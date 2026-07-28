from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.weather_day import WeatherDay
from app.models.weather_search import WeatherSearch


class WeatherSearchRepository:
    """Database access for saved weather searches."""

    def add(self, session: Session, search: WeatherSearch) -> WeatherSearch:
        session.add(search)
        session.flush()
        return search

    def get_by_id(self, session: Session, search_id: int) -> WeatherSearch | None:
        statement = (
            select(WeatherSearch)
            .options(selectinload(WeatherSearch.days))
            .where(WeatherSearch.id == search_id)
        )
        return session.scalar(statement)

    def list(
        self,
        session: Session,
        *,
        page: int,
        page_size: int,
        location: str | None,
    ) -> tuple[list[WeatherSearch], int]:
        filters = []
        if location:
            pattern = f"%{location.strip()}%"
            filters.append(
                or_(
                    WeatherSearch.resolved_name.ilike(pattern),
                    WeatherSearch.administrative_area.ilike(pattern),
                    WeatherSearch.country.ilike(pattern),
                    WeatherSearch.original_location_input.ilike(pattern),
                )
            )

        count_statement = select(func.count(WeatherSearch.id))
        list_statement = (
            select(WeatherSearch)
            .options(selectinload(WeatherSearch.days))
            .order_by(WeatherSearch.created_at.desc(), WeatherSearch.id.desc())
        )
        if filters:
            count_statement = count_statement.where(*filters)
            list_statement = list_statement.where(*filters)

        total = int(session.scalar(count_statement) or 0)
        items = list(
            session.scalars(
                list_statement.offset((page - 1) * page_size).limit(page_size)
            )
        )
        return items, total

    def list_all(self, session: Session) -> list[WeatherSearch]:
        """Return all saved searches with their daily rows for file export."""

        statement = (
            select(WeatherSearch)
            .options(selectinload(WeatherSearch.days))
            .order_by(WeatherSearch.created_at.desc(), WeatherSearch.id.desc())
        )
        return list(session.scalars(statement))

    def replace_days(
        self,
        session: Session,
        *,
        search: WeatherSearch,
        days: list[WeatherDay],
    ) -> None:
        """Replace all child rows inside the caller's active transaction."""

        search.days.clear()
        session.flush()
        search.days.extend(days)
        session.flush()

    def delete(self, session: Session, search: WeatherSearch) -> None:
        session.delete(search)
        session.flush()
