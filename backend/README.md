# WeatherScope Backend

FastAPI backend for the PM Accelerator AI Engineer technical assessment.

## Responsibilities

- Resolve place names and postal codes
- Retrieve current, forecast, and historical weather
- Validate coordinates and date ranges
- Normalize provider-specific responses
- Persist weather searches and daily values
- Provide complete CRUD operations
- Generate CSV and JSON exports
- Return a consistent error contract

## Setup

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env -Force
```

## Run

```powershell
fastapi dev app/main.py
```

- Swagger: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Test

```powershell
python -m pytest -q
```

## Local database

The application creates `weatherscope.db` at runtime. The database file is
intentionally excluded from Git. A reviewer receives a clean database when
starting the API for the first time.

## Configuration

Use `.env.example` as the template. Never commit `.env`.

## Main API groups

- Health
- Locations
- Weather
- Weather Searches
- Exports
