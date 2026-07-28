# Architecture

## Architectural style

WeatherScope uses a modular full-stack monolith:

- one React single-page application;
- one FastAPI backend;
- one SQLite relational database;
- one weather/geocoding provider.

This avoids unnecessary distributed-system complexity while preserving
clear internal boundaries.

## Data flow

```text
User
  |
  v
React components
  |
  v
Typed frontend API clients
  |
  v
FastAPI routes
  |
  v
Application services
  |-------------------|
  v                   v
Repositories       Open-Meteo client
  |                   |
  v                   v
SQLite             External APIs
```

## Backend layers

### API routes

Handle HTTP methods, query parameters, request bodies, response models,
status codes, and dependency injection.

### Services

Implement business rules: validation, date-range routing, weather
normalization, CRUD coordination, and export generation.

### External client

Encapsulates Open-Meteo URLs, parameters, timeouts, status handling, and
JSON parsing.

### Repositories

Encapsulate SQLAlchemy database queries and persistence operations.

### Models and schemas

SQLAlchemy models define storage. Pydantic schemas define public API
contracts. Keeping them separate prevents database implementation details
from leaking into the API.

## Date-range routing

A request may be:

- historical;
- current/future forecast;
- mixed across the present date.

The backend separates mixed ranges, retrieves each segment from the
appropriate provider endpoint, normalizes both responses, removes duplicate
dates, and returns one chronological result.

## Update integrity

Metadata-only changes such as notes update the database directly.

Changes to location, dates, or units retrieve replacement weather before
mutating persisted data. The database update then replaces the parent
metadata and child rows within one transaction.

## Security and configuration

- Secrets and local environment files are excluded from Git.
- The frontend never calls the weather provider directly.
- Input is validated by both TypeScript forms and Pydantic/FastAPI.
- CORS is restricted to the local frontend origins in development.
