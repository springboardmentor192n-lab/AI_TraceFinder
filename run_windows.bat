@echo off
REM ===============================================
REM AI TraceFinder - Quick Run Script
REM ===============================================

echo.
echo =========================================
echo AI TraceFinder - Starting Server
echo =========================================
echo.

REM Check if venv exists
if not exist "venv\" (
    echo Virtual environment not found!
    echo Please run setup_windows.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Change to backend directory
cd backend

REM Start the Flask app
echo Starting Flask server...
echo.
echo Navigate to: http://localhost:5000
echo API Docs: http://localhost:5000/api/docs
echo Press Ctrl+C to stop the server
echo.

python app.py

pause
