#!/usr/bin/env bash
set -euo pipefail

# start.sh - Start backend (FastAPI) and frontend (Vite) for development
# Usage: ./start.sh [--dry-run]

DRY_RUN=0
while [[ ${1:-} != "" ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1 ; shift ;;
    -h|--help) echo "Usage: $0 [--dry-run]"; exit 0 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

ROOT_DIR=$(cd "$(dirname "$0")" && pwd)
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

BACKEND_CMD="cd \"$BACKEND_DIR\" && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
FRONTEND_CMD="cd \"$FRONTEND_DIR\" && npm run dev"

echo "Start script running from: $ROOT_DIR"
echo "Backend command: $BACKEND_CMD"
echo "Frontend command: $FRONTEND_CMD"

if [ "$DRY_RUN" -eq 1 ]; then
  echo "Dry-run mode: not executing commands"
  exit 0
fi

# Basic checks
command -v node >/dev/null 2>&1 || { echo "node not found in PATH" >&2; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "npm not found in PATH" >&2; exit 1; }
command -v python >/dev/null 2>&1 || { echo "python not found in PATH" >&2; exit 1; }

LOGDIR="$ROOT_DIR/logs"
mkdir -p "$LOGDIR"

echo "Starting backend... (logs: $LOGDIR/backend.log)"
cd "$BACKEND_DIR"
nohup bash -lc "$BACKEND_CMD" > "$LOGDIR/backend.log" 2>&1 &
BACK_PID=$!
echo "Backend PID: $BACK_PID"

echo "Starting frontend... (logs: $LOGDIR/frontend.log)"
cd "$FRONTEND_DIR"
nohup bash -lc "$FRONTEND_CMD" > "$LOGDIR/frontend.log" 2>&1 &
FRONT_PID=$!
echo "Frontend PID: $FRONT_PID"

cleanup() {
  echo "Stopping services..."
  kill "$FRONT_PID" 2>/dev/null || true
  kill "$BACK_PID" 2>/dev/null || true
  wait "$FRONT_PID" 2>/dev/null || true
  wait "$BACK_PID" 2>/dev/null || true
  echo "Stopped. Logs available in $LOGDIR"
}

trap cleanup INT TERM EXIT

echo "Both services launched. Press Ctrl+C to stop."

# Wait for both processes
wait "$BACK_PID" "$FRONT_PID"
