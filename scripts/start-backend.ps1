$ErrorActionPreference = "Stop"
Set-Location "$PSScriptRoot\..\backend"

if (-not (Test-Path ".venv")) {
    py -3.13 -m venv .venv
}

& ".\.venv\Scripts\Activate.ps1"
python -m pip install -r requirements-dev.txt

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
}

fastapi dev app/main.py
