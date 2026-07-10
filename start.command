#!/bin/zsh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PORT="${PORT:-8080}"

cd "$SCRIPT_DIR"

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

sleep 2
open "$URL"

echo ""
echo "ads.txt validator is running at ${URL}"
echo "Keep this Terminal window open while using the app."
echo "Press Control+C here when you want to stop the server."
echo ""

wait "$SERVER_PID"
