#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$ROOT/.venv-wsl"
PYTHON_BIN="$VENV_DIR/bin/python"
PIP_BIN="$VENV_DIR/bin/pip"

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "$1 is required but not installed"
    exit 1
  fi
}

require_cmd python3
require_cmd node
require_cmd npm
require_cmd neo4j

mkdir -p "$ROOT/logs" "$ROOT/run"
cd "$ROOT"

if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
fi

"$PYTHON_BIN" -m pip install --upgrade pip
"$PIP_BIN" install -r "$ROOT/backend/requirements.txt"
npm install

echo
echo "WSL bootstrap complete"
echo "Python: $PYTHON_BIN"
echo "Node modules: $ROOT/node_modules"
echo "PM2 bin: $ROOT/node_modules/.bin/pm2"
