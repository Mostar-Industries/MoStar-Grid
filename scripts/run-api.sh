#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# MOSTAR GRID — API SERVICE RUNNER
# ═══════════════════════════════════════════════════════════════════

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( dirname "$SCRIPT_DIR" )"

# Source env if it exists
if [ -f "$PROJECT_ROOT/config/.env" ]; then
    export $(grep -v '^#' "$PROJECT_ROOT/config/.env" | xargs)
fi

# Set PYTHONPATH to include all service boundaries
export PYTHONPATH=$PYTHONPATH:$PROJECT_ROOT:$PROJECT_ROOT/core/grid-orchestrator:$PROJECT_ROOT/core/cognition:$PROJECT_ROOT/engines/idim-ikang:$PROJECT_ROOT/memory/neo4j-mindgraph

echo "🚀 Starting MoStar Grid API Ingress..."
python3 "$PROJECT_ROOT/core/mostar-api/main.py"
