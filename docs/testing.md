# Testing Strategy

## Backend

Run:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m pytest -q
```

Coverage areas include:

- health and configuration
- location validation and normalization
- current weather normalization
- date-range routing
- historical, forecast, and mixed previews
- Create, Read, Update, and Delete
- transaction rollback
- CSV and JSON exports
- consistent error responses

External provider calls are mocked in automated tests so results do not
depend on live internet availability.

## Frontend

Run:

```powershell
cd frontend
npm run test:run
npm run build
```

Coverage areas include:

- location search and selection
- current-location geolocation
- current weather
- five-day forecast
- date-range validation
- saving a preview
- saved-search interactions
- map rendering

## Manual end-to-end checks

1. Search a valid and invalid location.
2. Use current location and deny permission once.
3. Switch metric and imperial units.
4. Preview historical, forecast, and mixed ranges.
5. Save, refresh, read, update, export, and delete a record.
6. Stop the backend and confirm a graceful frontend error.
7. Test desktop, tablet, mobile, portrait, and landscape views.
8. Verify no secrets, databases, caches, or build output are committed.
