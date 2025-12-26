#!/usr/bin/env bash
set -euo pipefail

# Run end-to-end tests with local dev servers and DB started as needed.
# - Starts Postgres (docker-compose) if not running
# - Starts backend (Node) and frontend (Vite) dev servers
# - Waits for required ports
# - Installs Playwright browsers if needed
# - Runs Playwright tests
# - Cleans up started servers unless KEEP_RESOURCES=1

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

DOCKER_COMPOSE="docker compose"

echo "[e2e] Starting prerequisites..."

# Start Postgres services if not healthy
function start_postgres() {
  echo "[e2e] Ensuring Postgres containers are up..."
  $DOCKER_COMPOSE up -d postgres postgres_test
}

function wait_for_port() {
  local host=$1
  local port=$2
  local timeout=${3:-60}
  echo "[e2e] Waiting for $host:$port (timeout ${timeout}s)"
  local start_time=$(date +%s)
  while :; do
    if (echo > /dev/tcp/$host/$port) >/dev/null 2>&1; then
      echo "[e2e] $host:$port is available"
      return 0
    fi
    sleep 1
    if [ $(( $(date +%s) - start_time )) -ge $timeout ]; then
      echo "[e2e] Timeout waiting for $host:$port" >&2
      return 1
    fi
  done
}

DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}

# If running in CI, a service may already provide Postgres (GitHub Actions services).
# In that case skip starting docker-compose to avoid host port collisions.
if [ "${CI:-}" = "true" ]; then
  echo "[e2e] CI environment detected; skipping docker-compose Postgres startup"
else
  start_postgres
fi

if ! wait_for_port "$DB_HOST" "$DB_PORT" 60; then
  echo "[e2e] Postgres not available on ${DB_HOST}:${DB_PORT}" >&2
  exit 1
fi

BACKEND_LOG="/tmp/news_backend_e2e.log"
FRONTEND_LOG="/tmp/news_frontend_e2e.log"
PIDS=()

echo "[e2e] Starting backend..."
pushd backend > /dev/null
# Install deps if missing
if [ ! -d node_modules ]; then
  echo "[e2e] Installing backend dependencies..."
  npm ci
fi
# Start backend on port 3000 (Playwright expects 3000)
PORT=3000 SKIP_DB_CHECK=0 npm run dev > "$BACKEND_LOG" 2>&1 &
PIDS+=("$!")
popd > /dev/null

echo "[e2e] Starting frontend..."
pushd frontend > /dev/null
if [ ! -d node_modules ]; then
  echo "[e2e] Installing frontend dependencies..."
  npm ci
fi
# Ensure Playwright browsers are installed
echo "[e2e] Ensuring Playwright browsers are installed"
npx playwright install --with-deps || true
# Start Vite on port 3001
npm run dev -- --port 3001 --host > "$FRONTEND_LOG" 2>&1 &
PIDS+=("$!")
popd > /dev/null

trap 'echo "[e2e] Cleaning up..."; for p in "${PIDS[@]:-}"; do kill "$p" >/dev/null 2>&1 || true; done; if [ "${KEEP_RESOURCES:-}" != "1" ]; then $DOCKER_COMPOSE down --remove-orphans; fi' EXIT

echo "[e2e] Waiting for backend and frontend ports..."
wait_for_port localhost 3000 60
wait_for_port localhost 3001 60

echo "[e2e] Running Playwright tests"
pushd frontend > /dev/null
npx playwright test "$@"
RESULT=$?
popd > /dev/null

if [ $RESULT -eq 0 ]; then
  echo "[e2e] Playwright tests passed"
else
  echo "[e2e] Playwright tests failed (exit $RESULT). Logs: $BACKEND_LOG, $FRONTEND_LOG" >&2
fi

exit $RESULT
