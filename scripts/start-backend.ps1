# Start Backend API Service
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Football Agent - Backend API Service" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (!(Test-Path ".env")) {
    Write-Host "Warning: .env file not found. Copy .env.example to .env" -ForegroundColor Yellow
}

# Activate virtual environment if it exists
if (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Green
    . .\.venv\Scripts\Activate.ps1
}

Write-Host "Starting Backend API on port 8000..." -ForegroundColor Green
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""

# Run the backend server
uvicorn backend.server:app --reload --host 0.0.0.0 --port 8000
