# ═══════════════════════════════════════════════════════════════════
# MOSTAR GRID — SOVEREIGN API INGRESS
# The Flame Architect — MSTR-⚡ — MoStar Industries
# "Built from African intelligence. For African sovereignty."
# ═══════════════════════════════════════════════════════════════════

import os
import sys
import uvicorn
from fastapi import FastAPI

# Ensure orchestrator and engine paths are available
# These are typically set via PYTHONPATH in production/WSL, 
# but we add them here for local workbench robustness.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "core", "grid-orchestrator"))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "engines", "idim-ikang"))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "memory", "neo4j-mindgraph"))

try:
    from core_engine.api_gateway import app
    print("✅ MoStar Grid API Gateway loaded successfully.")
except ImportError as e:
    print(f"⚠️  Import error: {e}")
    print("Ensure PYTHONPATH is set or core/grid-orchestrator/core_engine exists.")
    app = FastAPI(title="MoStar Grid API (Fallback)")

if __name__ == "__main__":
    port = int(os.getenv("GRID_PORT", "7001"))
    host = os.getenv("GRID_HOST", "0.0.0.0")
    
    print(f"🚀 Starting MoStar Grid API Ingress on {host}:{port}")
    # We call the app from api_gateway
    uvicorn.run(app, host=host, port=port, reload=False, log_level="info")
