# Test Runner Script for Sportsradar Football Agent
# Runs both backend (pytest) and frontend (vitest) tests

param(
    [switch]$Backend,
    [switch]$Frontend,
    [switch]$Coverage,
    [switch]$Verbose
)

$ErrorActionPreference = "Continue"
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootPath = Split-Path -Parent $scriptPath

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Sportsradar Test Runner" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# If no specific flag is passed, run all tests
if (-not $Backend -and -not $Frontend) {
    $Backend = $true
    $Frontend = $true
}

$backendPassed = $true
$frontendPassed = $true

# Backend Tests (pytest)
if ($Backend) {
    Write-Host "Running Backend Tests (pytest)..." -ForegroundColor Yellow
    Write-Host "----------------------------------------" -ForegroundColor Gray
    
    Push-Location $rootPath
    
    try {
        if ($Coverage) {
            if ($Verbose) {
                pytest tests/ -v --cov=backend --cov-report=term-missing --cov-report=html:coverage_html
            } else {
                pytest tests/ --cov=backend --cov-report=term-missing
            }
        } else {
            if ($Verbose) {
                pytest tests/ -v
            } else {
                pytest tests/
            }
        }
        
        if ($LASTEXITCODE -ne 0) {
            $backendPassed = $false
            Write-Host "Backend tests FAILED" -ForegroundColor Red
        } else {
            Write-Host "Backend tests PASSED" -ForegroundColor Green
        }
    }
    catch {
        $backendPassed = $false
        Write-Host "Backend tests ERROR: $_" -ForegroundColor Red
    }
    
    Pop-Location
    Write-Host ""
}

# Frontend Tests (vitest)
if ($Frontend) {
    Write-Host "Running Frontend Tests (vitest)..." -ForegroundColor Yellow
    Write-Host "----------------------------------------" -ForegroundColor Gray
    
    $frontendPath = Join-Path $rootPath "frontend-react"
    Push-Location $frontendPath
    
    try {
        # Check if node_modules exists
        if (-not (Test-Path "node_modules")) {
            Write-Host "Installing frontend dependencies..." -ForegroundColor Gray
            npm install
        }
        
        if ($Coverage) {
            npm run test:coverage
        } else {
            npm run test:run
        }
        
        if ($LASTEXITCODE -ne 0) {
            $frontendPassed = $false
            Write-Host "Frontend tests FAILED" -ForegroundColor Red
        } else {
            Write-Host "Frontend tests PASSED" -ForegroundColor Green
        }
    }
    catch {
        $frontendPassed = $false
        Write-Host "Frontend tests ERROR: $_" -ForegroundColor Red
    }
    
    Pop-Location
    Write-Host ""
}

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Test Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if ($Backend) {
    if ($backendPassed) {
        Write-Host "  Backend:  " -NoNewline; Write-Host "PASSED" -ForegroundColor Green
    } else {
        Write-Host "  Backend:  " -NoNewline; Write-Host "FAILED" -ForegroundColor Red
    }
}

if ($Frontend) {
    if ($frontendPassed) {
        Write-Host "  Frontend: " -NoNewline; Write-Host "PASSED" -ForegroundColor Green
    } else {
        Write-Host "  Frontend: " -NoNewline; Write-Host "FAILED" -ForegroundColor Red
    }
}

Write-Host "========================================" -ForegroundColor Cyan

# Exit with appropriate code
if (-not $backendPassed -or -not $frontendPassed) {
    exit 1
}
