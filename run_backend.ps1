# AI TraceFinder Quick Start Script (PowerShell)
# This script activates the virtual environment and runs the Flask backend

Write-Host ""
Write-Host "========================================================"
Write-Host "     AI TraceFinder Backend - Startup Script"
Write-Host "========================================================"
Write-Host ""

# Get the script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Check if venv exists
if (-not (Test-Path "venv")) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run setup_windows.bat first." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Green
& "venv\Scripts\Activate.ps1"

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to activate virtual environment!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if requirements are installed
Write-Host ""
Write-Host "Checking dependencies..." -ForegroundColor Green
python -c "import flask, cv2, joblib, scipy" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing missing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

# Start the backend server
Write-Host ""
Write-Host "========================================================"
Write-Host "Starting Flask Backend Server..." -ForegroundColor Cyan
Write-Host "========================================================"
Write-Host ""
Write-Host "Server will be available at: http://localhost:10000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

python backend/app.py

Read-Host "Press Enter to exit"
