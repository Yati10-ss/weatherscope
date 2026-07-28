$ErrorActionPreference = "Stop"
Set-Location "$PSScriptRoot\..\frontend"

npm install

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
}

npm run dev
