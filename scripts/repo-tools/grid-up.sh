#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PM2_BIN="$ROOT/node_modules/.bin/pm2"
PM2_HOME_DIR="$ROOT/.pm2-mostar"
cd "$ROOT"
mkdir -p "$ROOT/logs" "$PM2_HOME_DIR"
export PM2_HOME="$PM2_HOME_DIR"

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "$1 is required but not installed"
    exit 1
  fi
}

start_service() {
  local service_name="$1"

  if command -v systemctl >/dev/null 2>&1 && systemctl list-unit-files "${service_name}.service" >/dev/null 2>&1; then
    sudo systemctl start "$service_name"
    return
  fi

  sudo service "$service_name" start
}

require_cmd python3
require_cmd node
require_cmd npm
require_cmd redis-server
require_cmd neo4j

if [ ! -x "$PM2_BIN" ]; then
  PM2_BIN="$(command -v pm2 || true)"
fi

if [ -z "$PM2_BIN" ]; then
  echo "PM2 is not installed for WSL. Run: bash $ROOT/scripts/bootstrap-wsl.sh"
  exit 1
fi

start_service redis-server
bash "$ROOT/scripts/run-neo4j.sh" start

"$PM2_BIN" start "$ROOT/ecosystem.config.js" --update-env
"$PM2_BIN" save
"$PM2_BIN" status
