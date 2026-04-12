#!/bin/bash
# TraceFinder Quick Start Script
# Run from the tracefinder/ root directory

set -e

echo ""
echo "╔══════════════════════════════════════╗"
echo "║     TraceFinder — Quick Start        ║"
echo "╚══════════════════════════════════════╝"
echo ""

# ── Backend ───────────────────────────────────────────────────
echo "📦 Installing Python dependencies..."
cd backend
pip install -r requirements.txt --quiet

echo ""
echo "🚀 Starting FastAPI backend on port 8000..."
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

# Wait for backend to start
sleep 3

# ── Frontend ──────────────────────────────────────────────────
echo ""
echo "📦 Installing Node.js dependencies..."
cd ../frontend
npm install --silent

echo ""
echo "🌐 Starting Next.js frontend on port 3000..."
npm run dev &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"

echo ""
echo "╔══════════════════════════════════════╗"
echo "║  ✅ Both servers are running!        ║"
echo "║                                      ║"
echo "║  Frontend → http://localhost:3000    ║"
echo "║  Backend  → http://localhost:8000    ║"
echo "║  API Docs → http://localhost:8000/docs ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "Press Ctrl+C to stop both servers."
echo ""

# Keep script alive, kill both on Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo 'Servers stopped.'" EXIT
wait
