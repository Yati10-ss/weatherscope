# API Reference

Base path: `/api/v1`

Live interactive documentation:

- Swagger UI: `/docs`
- ReDoc: `/redoc`

## Health

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Confirm API availability and version |

## Locations

| Method | Path | Purpose |
|---|---|---|
| GET | `/locations/search` | Resolve a place name or postal code |

Important query parameters:

- `q`
- `count`
- `language`
- `country_code`

## Weather previews

| Method | Path | Purpose |
|---|---|---|
| GET | `/weather/current` | Retrieve current conditions |
| GET | `/weather/forecast` | Retrieve a 1–16 day forecast |
| POST | `/weather/preview` | Preview an inclusive date range |

Preview operations do not create database records.

## Persistent weather searches

| Method | Path | CRUD |
|---|---|---|
| POST | `/weather-searches` | Create |
| GET | `/weather-searches` | Read list |
| GET | `/weather-searches/{search_id}` | Read detail |
| PATCH | `/weather-searches/{search_id}` | Update |
| DELETE | `/weather-searches/{search_id}` | Delete |

## Exports

| Method | Path | Purpose |
|---|---|---|
| GET | `/exports/weather-searches.json` | Export all as JSON |
| GET | `/exports/weather-searches.csv` | Export all as CSV |
| GET | `/exports/weather-searches/{id}.json` | Export one as JSON |
| GET | `/exports/weather-searches/{id}.csv` | Export one as CSV |

## Error contract

Predictable errors use:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message.",
    "details": {}
  }
}
```

Common status codes:

- `400` invalid business rule or date range
- `404` location or stored record not found
- `422` request validation error
- `502` upstream provider failure
- `504` upstream provider timeout
