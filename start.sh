#!/bin/bash
echo "Starting TrailGuard AI..."
echo "Terminal 1: Backend on :8000"
echo "Terminal 2: Frontend on :3000"

# Run both
cd "$(dirname "$0")"

# Start backend in background
cd services/api
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Start frontend
cd ../apps/web
npm run dev &
FRONTEND_PID=$!

echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait
