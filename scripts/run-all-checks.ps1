$ErrorActionPreference = "Stop"

Write-Host "Running backend tests..."
Set-Location "$PSScriptRoot\..\backend"

if (-not (Test-Path ".venv")) {
    throw "Backend virtual environment not found. Create backend\.venv first."
}

& ".\.venv\Scripts\Activate.ps1"
python -m pytest -q

Write-Host "Running frontend tests and build..."
Set-Location "$PSScriptRoot\..\frontend"
npm run test:run
npm run build

Write-Host "All WeatherScope checks passed."
