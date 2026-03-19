@echo off
REM ===============================================
REM AI TraceFinder - Windows Setup Script
REM ===============================================

echo.
echo =========================================
echo AI TraceFinder - Setup
echo =========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org
    pause
    exit /b 1
)

echo [1/4] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo Error: Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/4] Installing dependencies...
python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
    echo Error: Failed to upgrade pip, setuptools, wheel
    pause
    exit /b 1
)
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install requirements
    pause
    exit /b 1
)

echo.
echo =========================================
echo Setup Complete!
echo =========================================
echo.
echo To run the application:
echo   1. Activate venv: venv\Scripts\activate
echo   2. Run the app: python backend/app.py
echo   3. Open browser: http://localhost:5000
echo.
pause
