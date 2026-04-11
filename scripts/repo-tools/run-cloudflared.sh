#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

BIN="${CLOUDFLARED_BIN:-/mnt/c/Users/idona/Desktop/cloudflared-windows-amd64.exe}"
CONFIG="${CLOUDFLARED_CONFIG:-$ROOT/cloudflared/config-direct.yml}"
TOKEN="${CLOUDFLARED_TOKEN:-}"

if [ ! -f "$BIN" ]; then
  echo "cloudflared binary not found at $BIN"
  exit 1
fi

if [ -n "$TOKEN" ]; then
  exec "$BIN" tunnel run --token "$TOKEN"
fi

exec "$BIN" tunnel --config "$CONFIG" run
