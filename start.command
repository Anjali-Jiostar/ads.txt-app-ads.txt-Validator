#!/bin/zsh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PORT="${PORT:-8080}"

cd "$SCRIPT_DIR"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is not installed or not available in PATH."
  echo "Install Python 3, then run start.command again."
  exit 1
fi

while lsof -iTCP:"${PORT}" -sTCP:LISTEN >/dev/null 2>&1; do
  echo "Port ${PORT} is already in use, trying next port..."
  PORT=$((PORT + 1))
done

URL="http://localhost:${PORT}"

echo "Starting ads.txt validator server..."
PORT="$PORT" python3 server.py &
SERVER_PID=$!

cleanup() {
  if kill -0 "$SERVER_PID" >/dev/null 2>&1; then
    kill "$SERVER_PID" >/dev/null 2>&1 || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

for _ in {1..20}; do
  if ! kill -0 "$SERVER_PID" >/dev/null 2>&1; then
    echo "The local server exited before startup completed."
    wait "$SERVER_PID"
  fi

  if lsof -iTCP:"${PORT}" -sTCP:LISTEN >/dev/null 2>&1; then
    break
  fi

  sleep 0.25
done

if command -v open >/dev/null 2>&1; then
  open "$URL"
fi

echo ""
echo "ads.txt validator is running at ${URL}"
echo "Keep this Terminal window open while using the app."
echo "Press Control+C here when you want to stop the server."
echo ""

wait "$SERVER_PID"
