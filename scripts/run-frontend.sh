#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT/frontend"

FRONTEND_HOST="${FRONTEND_HOST:-0.0.0.0}"
export PORT="${PORT:-3000}"
export GRID_API_BASE="${GRID_API_BASE:-http://127.0.0.1:8001}"
export CONSCIOUSNESS_API_BASE="${CONSCIOUSNESS_API_BASE:-http://127.0.0.1:8001}"
export NEXT_PUBLIC_API_URL="${NEXT_PUBLIC_API_URL:-http://127.0.0.1:8001}"
export NEO4J_URI="${NEO4J_URI:-bolt://127.0.0.1:7687}"
export NEO4J_USER="${NEO4J_USER:-neo4j}"
export OLLAMA_API_URL="${OLLAMA_API_URL:-http://127.0.0.1:11434}"

NEXT_BIN="$ROOT/node_modules/next/dist/bin/next"
WIN_SWC_DIR="$ROOT/node_modules/@next/swc-win32-x64-msvc"

if [ ! -f "$NEXT_BIN" ]; then
  echo "Next.js CLI not found at $NEXT_BIN"
  exit 1
fi

if [ -d "$WIN_SWC_DIR" ] && ! compgen -G "$ROOT/node_modules/@next/swc-linux-*" >/dev/null; then
  echo "WSL frontend dependencies are not installed. Run: bash $ROOT/scripts/bootstrap-wsl.sh"
  exit 1
fi

exec /usr/bin/node "$NEXT_BIN" dev -H "$FRONTEND_HOST" -p "$PORT"
