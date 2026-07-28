# WeatherScope Frontend

React and TypeScript frontend for the WeatherScope full-stack assessment.

## Features

- Manual and current-location selection
- Current weather and five-day forecast
- Date-range preview and database save
- Saved-search history and filtering
- View, update, delete, and export workflows
- Embedded OpenStreetMap view
- Responsive and accessible controls

## Setup

```powershell
npm install
Copy-Item .env.example .env -Force
```

The frontend environment file must contain:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

## Commands

```powershell
npm run test:run
npm run build
npm run dev
```

The FastAPI backend must be running at `http://127.0.0.1:8000` for
live browser testing.
