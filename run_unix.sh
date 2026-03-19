#!/bin/bash

# ===============================================
# AI TraceFinder - Quick Run Script
# ===============================================

echo ""
echo "========================================="
echo "AI TraceFinder - Starting Server"
echo "========================================="
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found!"
    echo "Please run ./setup_unix.sh first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Change to backend directory
cd backend

# Start the Flask app
echo "Starting Flask server..."
echo ""
echo "Navigate to: http://localhost:5000"
echo "API Docs: http://localhost:5000/api/docs"
echo "Press Ctrl+C to stop the server"
echo ""

python app.py
