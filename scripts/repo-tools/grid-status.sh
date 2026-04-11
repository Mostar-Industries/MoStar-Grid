#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PM2_BIN="$ROOT/node_modules/.bin/pm2"
PM2_HOME_DIR="$ROOT/.pm2-mostar"
export PM2_HOME="$PM2_HOME_DIR"

check_port() {
  local name="$1"
  local port="$2"

  if bash -lc "</dev/tcp/127.0.0.1/${port}" >/dev/null 2>&1; then
    echo "$name open $port"
    return
  fi

  echo "$name closed $port"
}

check_url() {
  local name="$1"
  local url="$2"

  if command -v curl >/dev/null 2>&1; then
    local code
    code=$(curl -s -o /dev/null -w "%{http_code}" "$url" || true)
    echo "$name $code $url"
    return
  fi

  echo "$name curl-unavailable $url"
}

if [ -x "$PM2_BIN" ]; then
  "$PM2_BIN" status
elif command -v pm2 >/dev/null 2>&1; then
  pm2 status
fi

if command -v service >/dev/null 2>&1; then
  service redis-server status || true
fi

check_port neo4j 7687
check_port ollama-port 11434
check_port memory-port 8000
check_port core-port 8001
check_port frontend-port 3000
check_url frontend http://127.0.0.1:3000
check_url memory http://127.0.0.1:8000/
check_url core http://127.0.0.1:8001/api/v1/status
check_url ollama http://127.0.0.1:11434/api/tags
