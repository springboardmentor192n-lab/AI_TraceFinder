@echo off
REM AI TraceFinder Quick Start Script
REM This script activates the virtual environment and runs the Flask backend

setlocal enabledelayedexpansion

REM Get the script directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo.
echo ========================================================
echo     AI TraceFinder Backend - Startup Script
echo ========================================================
echo.

REM Check if venv exists
if not exist "venv" (
    echo ERROR: Virtual environment not found!
    echo Please run setup_windows.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment!
    pause
    exit /b 1
)

REM Check if requirements are installed
echo.
echo Checking dependencies...
python -c "import flask, opencv_python, joblib, scipy" 2>nul
if errorlevel 1 (
    echo Installing missing dependencies...
    pip install -r requirements.txt
)

REM Start the backend server
echo.
echo ========================================================
echo Starting Flask Backend Server...
echo ========================================================
echo.
echo Server will be available at: http://localhost:10000
echo Press Ctrl+C to stop the server
echo.

python backend/app.py

pause
