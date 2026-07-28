from app.database.base import Base
from app.database.session import engine

# Import models so SQLAlchemy registers their tables before create_all runs.
from app.models.weather_day import WeatherDay  # noqa: F401
from app.models.weather_search import WeatherSearch  # noqa: F401


def init_db() -> None:
    """Create missing database tables for local development and evaluation."""

    Base.metadata.create_all(bind=engine)
