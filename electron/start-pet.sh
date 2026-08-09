#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$(dirname "$DIR")"

echo "=== HealthMate Desktop Pet ==="
echo ""
echo "Starting backend..."
cd "$BACKEND_DIR"

# Kill any existing process on port 8000
lsof -ti:8000 2>/dev/null | xargs kill -9 2>/dev/null

# Start backend
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to be ready
echo -n "Waiting for backend"
for i in $(seq 1 30); do
  if curl -s http://localhost:8000/api/v1/health >/dev/null 2>&1; then
    echo ""
    echo "Backend ready!"
    break
  fi
  echo -n "."
  sleep 1
done

if ! curl -s http://localhost:8000/api/v1/health >/dev/null 2>&1; then
  echo ""
  echo "ERROR: Backend did not start. Check terminal for errors."
  kill $BACKEND_PID 2>/dev/null
  exit 1
fi

# Launch Electron
echo "Launching pet..."
cd "$DIR"
npx electron .

# Cleanup
echo "Shutting down..."
kill $BACKEND_PID 2>/dev/null
