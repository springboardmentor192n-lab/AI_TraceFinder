#!/bin/bash

# ===============================================
# AI TraceFinder - macOS/Linux Setup Script
# ===============================================

echo ""
echo "========================================="
echo "AI TraceFinder - Setup"
echo "========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.8+ from https://www.python.org"
    exit 1
fi

echo "[1/4] Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "Error: Failed to create virtual environment"
    exit 1
fi

echo "[2/4] Activating virtual environment..."
source venv/bin/activate

echo "[3/4] Installing dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "To run the application:"
echo "  1. Activate venv: source venv/bin/activate"
echo "  2. Run the app: python backend/app.py"
echo "  3. Open browser: http://localhost:5000"
echo ""
