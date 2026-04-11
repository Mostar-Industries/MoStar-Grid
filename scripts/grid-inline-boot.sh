#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOGS="$ROOT/logs"
RUN_DIR="$ROOT/run"
ENV_FILE="$ROOT/backend/.env"
PYTHON_BIN="$ROOT/.venv-wsl/bin/python"

mkdir -p "$LOGS" "$RUN_DIR"
cd "$ROOT"

if [ ! -x "$PYTHON_BIN" ]; then
  PYTHON_BIN="$(command -v python3)"
fi

env_value() {
  local key="$1"

  if [ ! -f "$ENV_FILE" ]; then
    return 0
  fi

  grep -m1 "^${key}=" "$ENV_FILE" | cut -d= -f2- || true
}

port_open() {
  local port="$1"
  bash -lc "</dev/tcp/127.0.0.1/${port}" >/dev/null 2>&1
}

kill_port() {
  local port="$1"

  if command -v fuser >/dev/null 2>&1; then
    fuser -k "${port}/tcp" >/dev/null 2>&1 || true
    return
  fi

  if command -v lsof >/dev/null 2>&1; then
    local pids
    pids=$(lsof -tiTCP:"${port}" -sTCP:LISTEN 2>/dev/null || true)
    if [ -n "$pids" ]; then
      kill $pids >/dev/null 2>&1 || true
    fi
  fi
}

stop_pidfile() {
  local pidfile="$1"

  if [ ! -f "$pidfile" ]; then
    return
  fi

  local pid
  pid=$(cat "$pidfile" 2>/dev/null || true)
  if [ -n "$pid" ] && kill -0 "$pid" >/dev/null 2>&1; then
    kill "$pid" >/dev/null 2>&1 || true
  fi
  rm -f "$pidfile"
}

start_bg() {
  local name="$1"
  shift

  local logfile="$LOGS/${name}.log"
  local pidfile="$RUN_DIR/${name}.pid"

  stop_pidfile "$pidfile"
  (
    cd "$ROOT"
    if command -v setsid >/dev/null 2>&1; then
      setsid "$@" >"$logfile" 2>&1 < /dev/null &
    else
      nohup "$@" >"$logfile" 2>&1 < /dev/null &
    fi
    echo $! >"$pidfile"
  )
}

export PYTHONPATH="$ROOT"
export PYTHONUTF8="1"
export PYTHONIOENCODING="utf-8"
export NEO4J_URI="${NEO4J_URI:-$(env_value NEO4J_URI)}"
export NEO4J_USER="${NEO4J_USER:-$(env_value NEO4J_USER)}"
export NEO4J_PASSWORD="${NEO4J_PASSWORD:-$(env_value NEO4J_PASSWORD)}"
export OLLAMA_HOST="${OLLAMA_HOST:-$(env_value OLLAMA_HOST)}"
export GRID_API_BASE="${GRID_API_BASE:-http://127.0.0.1:8001}"
export CONSCIOUSNESS_API_BASE="${CONSCIOUSNESS_API_BASE:-http://127.0.0.1:8001}"
export NEXT_PUBLIC_API_URL="${NEXT_PUBLIC_API_URL:-http://127.0.0.1:8001}"
export OLLAMA_API_URL="${OLLAMA_API_URL:-http://127.0.0.1:11434}"

export NEO4J_URI="${NEO4J_URI:-bolt://localhost:7687}"
export NEO4J_USER="${NEO4J_USER:-neo4j}"
export OLLAMA_HOST="${OLLAMA_HOST:-http://127.0.0.1:11434}"

printf '\n'
printf '==========================================\n'
printf '   MoStar-Grid: Inline System Boot       \n'
printf '==========================================\n'
printf '   Neo4j config: %s\n' "$NEO4J_URI"

# Step 0: Ensure Linux PM2 is available (not Windows)
export PATH="/home/idona/.npm-global/bin:/usr/local/bin:$PATH"
if ! command -v pm2 &>/dev/null || [[ $(which pm2) == /mnt/* ]]; then
    printf '   >> Installing Linux PM2...\n'
    npm install -g pm2 --prefix /home/idona/.npm-global
fi

# Step 0b: Start Ollama if not running
if ! curl -s http://127.0.0.1:11434/api/tags &>/dev/null; then
    printf '   >> Starting Ollama...\n'
    ollama serve > "$ROOT/logs/ollama.log" 2>&1 &
    sleep 3
fi

printf '\n[0/6] Clearing stale processes on ports 3000, 7474, 7687, 8000, 8001...\n'
for pidfile in "$RUN_DIR"/*.pid; do
  [ -e "$pidfile" ] || break
  stop_pidfile "$pidfile"
done
bash "$ROOT/scripts/run-neo4j.sh" stop >/dev/null 2>&1 || true
rm -f "$RUN_DIR/neo4j.pid"
for port in 3000 7474 7687 8000 8001; do
  kill_port "$port"
done
printf '   >> Ports cleared.\n'

printf '\n[1/6] Starting Neo4j Database (ports 7474/7687)...\n'
if port_open 7687; then
  printf '   Neo4j already running on port 7687\n'
else
  printf '   >> Launching Neo4j from app-local Ubuntu runtime...\n'
  bash "$ROOT/scripts/run-neo4j.sh" start >/dev/null 2>&1 || true
  printf '   >> Waiting for Neo4j to be ready (max 30s)...\n'
  waited=0
  while [ "$waited" -lt 30 ]; do
    sleep 2
    waited=$((waited + 2))
    if port_open 7687; then
      printf '   Neo4j ready after %ss\n' "$waited"
      break
    fi
    printf '   ... still waiting (%ss)\n' "$waited"
  done
  if ! port_open 7687; then
    printf '   Neo4j may not be ready yet. Continuing anyway.\n'
  fi
fi

printf '\n[2/6] Starting Ollama API (port 11434)...\n'
if port_open 11434; then
  printf '   Ollama already running on port 11434\n'
else
  start_bg ollama bash "$ROOT/scripts/run-ollama.sh"
  sleep 3
  if port_open 11434; then
    printf '   Ollama responding on port 11434\n'
  else
    printf '   Port 11434 not responding yet. Check logs: %s\n' "$LOGS/ollama.log"
  fi
fi

printf '\n[3/6] Starting Memory Layer API (port 8000)...\n'
start_bg memory_layer "$PYTHON_BIN" -m uvicorn backend.memory_layer.api.main:app --host 0.0.0.0 --port 8000
sleep 3
if port_open 8000; then
  printf '   Memory Layer API responding on port 8000\n'
  printf '      Docs: http://localhost:8000/docs\n'
else
  printf '   Port 8000 not responding yet. Check logs: %s\n' "$LOGS/memory_layer.log"
fi

printf '\n[4/6] Starting Core Engine API (port 8001)...\n'
start_bg core_engine "$PYTHON_BIN" -m uvicorn backend.core_engine.api_gateway:app --host 0.0.0.0 --port 8001
sleep 3
if port_open 8001; then
  printf '   Core Engine API responding on port 8001\n'
  printf '      Docs: http://localhost:8001/docs\n'
else
  printf '   Port 8001 not responding yet. Check logs: %s\n' "$LOGS/core_engine.log"
fi

printf '\n[5/6] Starting Mo Executor (graph mutation daemon)...\n'
start_bg mo_executor "$PYTHON_BIN" "$ROOT/backend/mo_executor.py"
printf '   Mo Executor started\n'
printf '      Log: %s\n' "$LOGS/mo_executor.log"

printf '\n[6/6] Starting Next.js Frontend (port 3000)...\n'
start_bg frontend bash "$ROOT/scripts/run-frontend.sh"
sleep 5
if port_open 3000; then
  printf '   Frontend responding on port 3000\n'
  printf '      URL: http://localhost:3000\n'
else
  printf '   ⚠️  Port 3000 not responding yet. Check logs: %s\n' "$LOGS/frontend.log"
fi

neo4j_ok=false
ollama_ok=false
memory_ok=false
core_ok=false
frontend_ok=false

port_open 7687 && neo4j_ok=true
port_open 11434 && ollama_ok=true
port_open 8000 && memory_ok=true
port_open 8001 && core_ok=true
port_open 3000 && frontend_ok=true

printf '\n==========================================\n'
printf '  MoStar Grid - Services Status          \n'
printf '==========================================\n\n'
printf '  Neo4j (7687)        : %s\n' "$( [ "$neo4j_ok" = true ] && printf 'RUNNING' || printf 'DOWN' )"
printf '  Ollama (11434)      : %s\n' "$( [ "$ollama_ok" = true ] && printf 'RUNNING' || printf 'DOWN' )"
printf '  Memory Layer (8000) : %s\n' "$( [ "$memory_ok" = true ] && printf 'RUNNING' || printf 'DOWN' )"
printf '  Core Engine (8001)  : %s\n' "$( [ "$core_ok" = true ] && printf 'RUNNING' || printf 'DOWN' )"
printf '  Frontend (3000)     : %s\n\n' "$( [ "$frontend_ok" = true ] && printf 'RUNNING' || printf 'DOWN' )"
printf '  Logs: %s\n' "$LOGS"
printf '  Run:  %s\n' "$RUN_DIR"
printf '==========================================\n\n'
