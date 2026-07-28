# WeatherScope

WeatherScope is a full-stack weather-information and persistence application
developed for the **PM Accelerator AI Engineer Internship technical assessment**.

It converts ambiguous location input into a resolved geographical location,
retrieves real weather information, supports historical and forecast date
ranges, persists results in SQLite, provides complete CRUD operations, and
exports stored data in CSV and JSON.

**Author:** Yateen Sakhare  
**Assessment completed:** Full-Stack AI Engineer  
**Release:** 1.0.0

## Key capabilities

- Search by city, town, landmark-style query, or postal code
- Use browser geolocation for the current location
- Display current conditions and a five-day forecast
- Preview historical, forecast, or mixed date ranges
- Persist requests and daily weather observations in SQLite
- Create, read, update, and delete saved weather searches
- Export one record or all records in CSV and JSON
- Display the selected coordinates through OpenStreetMap
- Switch between metric and imperial units
- Return structured validation, provider, and record-not-found errors
- Adapt to desktop, tablet, and mobile layouts
- Verify behaviour through backend and frontend automated tests

## Architecture

```text
Browser
  |
  v
React + TypeScript + Vite
  |
  | REST / JSON
  v
FastAPI + Pydantic
  |
  +-----------------------+
  |                       |
  v                       v
SQLAlchemy + SQLite    Open-Meteo APIs
                       - Geocoding
                       - Forecast
                       - Historical weather
```

Detailed architecture: [`docs/architecture.md`](docs/architecture.md)

## Repository structure

```text
weatherscope/
├── backend/                 FastAPI API, database, services, and tests
├── frontend/                React/TypeScript interface and tests
├── docs/                    Architecture, API, testing, and submission guides
├── scripts/                 Windows PowerShell convenience scripts
├── .github/workflows/       Continuous-integration checks
├── .gitignore
├── LICENSE
└── README.md
```

## Prerequisites

- Python 3.10 or later; developed and tested with Python 3.13
- Node.js 22.13 or later
- npm
- Internet access for Open-Meteo and OpenStreetMap

## Quick start

### 1. Backend

```powershell
cd backend
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env -Force
fastapi dev app/main.py
```

Backend URLs:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- Health: `http://127.0.0.1:8000/api/v1/health`

### 2. Frontend

Open a second terminal:

```powershell
cd frontend
npm install
Copy-Item .env.example .env -Force
npm run dev
```

Frontend URL:

- `http://127.0.0.1:5173`

## Tests and production build

Backend:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m pytest -q
```

Frontend:

```powershell
cd frontend
npm run test:run
npm run build
```

A convenience script is also provided:

```powershell
.\scripts\run-all-checks.ps1
```

## End-to-end workflow

1. Search for a location or use browser geolocation.
2. Select the intended location from normalized candidates.
3. Review current conditions and the five-day forecast.
4. Verify the selected location on the map.
5. Choose an inclusive date range.
6. Preview historical or forecast weather.
7. Add an optional note and save the result.
8. Read, update, filter, export, or delete saved records.

## Data model

WeatherScope stores:

- one `weather_searches` row per user request;
- one `weather_days` row per date in that request.

See [`docs/database-design.md`](docs/database-design.md).

## API reference

FastAPI generates interactive OpenAPI documentation automatically.
A concise endpoint summary is available in
[`docs/api-reference.md`](docs/api-reference.md).

## Screenshots

Add final desktop, tablet, and mobile screenshots under
`docs/screenshots/` before submission. Follow
[`docs/screenshots/README.md`](docs/screenshots/README.md).

## Demo video

Record a concise one-to-two-minute walkthrough using
[`docs/demo-script.md`](docs/demo-script.md), upload it to a viewable host,
and add the final URL here before submitting:

**Demo video:** `ADD_VIEWABLE_DEMO_URL_BEFORE_SUBMISSION`

## PM Accelerator

PM Accelerator supports product-management professionals from entry-level
through executive leadership by helping them strengthen practical product
and leadership skills through education, mentorship, community, and
hands-on product experience. Its broader mission includes expanding access
to education and helping professionals advance their careers.

## Known limitations

- Forecast availability is limited by the upstream weather provider.
- The application uses SQLite and does not implement multi-user authentication.
- Historical observations and forecasts may contain different variables.
- Browser geolocation requires permission and a secure context or localhost.
- The embedded map requires an internet connection.

## Submission checklist

Review [`docs/submission-checklist.md`](docs/submission-checklist.md)
before sharing the repository.

## Licence

This project is released under the MIT Licence.
