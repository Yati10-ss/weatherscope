from pydantic import BaseModel, ConfigDict, Field


class LocationResult(BaseModel):
    model_config = ConfigDict(extra="ignore")

    provider_id: int | None = None
    name: str
    display_name: str
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    country: str | None = None
    country_code: str | None = None
    administrative_area: str | None = None
    secondary_administrative_area: str | None = None
    timezone: str | None = None
    elevation_m: float | None = None
    population: int | None = None
    postcodes: list[str] = Field(default_factory=list)


class LocationSearchResponse(BaseModel):
    query: str
    result_count: int
    results: list[LocationResult]
