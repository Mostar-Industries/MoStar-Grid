#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# MOSTAR GRID — ORCHESTRATOR RUNNER (EXECUTIVE LOOP)
# ═══════════════════════════════════════════════════════════════════

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( dirname "$SCRIPT_DIR" )"

# Source env if it exists
if [ -f "$PROJECT_ROOT/config/.env" ]; then
    export $(grep -v '^#' "$PROJECT_ROOT/config/.env" | xargs)
fi

# Set PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$PROJECT_ROOT:$PROJECT_ROOT/core/grid-orchestrator:$PROJECT_ROOT/core/cognition:$PROJECT_ROOT/engines/idim-ikang:$PROJECT_ROOT/memory/neo4j-mindgraph

echo "🌑 Starting Grid Orchestrator (MoExecutor)..."
python3 "$PROJECT_ROOT/core/grid-orchestrator/mo_executor.py"
