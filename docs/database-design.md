# Database Design

WeatherScope uses SQLite through SQLAlchemy.

## Relationship

```text
weather_searches (1) ─────────────── (*) weather_days
```

## `weather_searches`

Stores one row per saved user request:

- original and resolved location information
- latitude and longitude
- timezone
- start and end date
- unit system
- optional note
- provider and weather units
- creation, update, and retrieval timestamps

## `weather_days`

Stores one row per date:

- foreign key to the parent search
- weather date and source type
- readable condition and weather code
- minimum, maximum, and mean temperature
- apparent temperature
- precipitation
- wind speed and gusts
- sunrise, sunset, daylight, and sunshine duration

## Data-integrity rules

- Parent and child rows are created within one transaction.
- A weather search is not saved when provider retrieval fails.
- Deleting a parent cascades to its daily rows.
- Weather-affecting updates replace daily rows atomically.
- Provider-generated measurements are not directly user-editable.
