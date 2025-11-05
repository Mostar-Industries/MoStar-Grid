import asyncio
import json
import logging
import os
import shlex
import subprocess
import time
import uuid
import asyncpg
import uvicorn
from config import get_db_connection_string
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from contextlib import asynccontextmanager
from config import ALLOW_NO_DB, API_HOST, API_PORT, GRID_MODE, get_db_connection_string
from fastapi import BackgroundTasks, FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocketDisconnect
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("grid")


class GridEvent(BaseModel):
    event_type: str
    source_agent: str
    location: str
    data: Dict[str, Any]
    priority: str = "medium"


class GridMemory:
    def __init__(self):
        self.events = []
        self.metrics = {"active_nodes": 410, "coherence": 0.9904, "total_events": 0}
        self.subscribers = []

    def store_event(self, event, response):
        self.events.append(
            {
                "event": event.dict(),
                "response": response,
                "timestamp": datetime.now().isoformat(),
            }
        )
        self.metrics["total_events"] += 1


memory = GridMemory()

# Database connection
db_pool = None
schema_mutable = True  # set to False if provider forbids schema changes


async def init_database():
    global db_pool, schema_mutable
    try:
        db_pool = await asyncpg.create_pool(
            get_db_connection_string(), min_size=2, max_size=10
        )
        logger.info("🔌 Connected to database (connection OK)")

        # Try to create tables; if provider forbids schema mutation, skip creation
        try:
            async with db_pool.acquire() as conn:
                await conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS grid_events (
                        event_id TEXT PRIMARY KEY,
                        event_type TEXT,
                        source_agent TEXT,
                        location TEXT,
                        data JSONB,
                        resonance_score FLOAT,
                        timestamp TIMESTAMPTZ DEFAULT NOW()
                    )
                """
                )
            logger.info("✅ grid_events table ready")
            schema_mutable = True
        except Exception as e:
            msg = str(e).lower()
            # Detect Neon / managed-provider schema mutation policy message
            if (
                ("covenantal" in msg)
                or ("forbidden" in msg)
                or ("permission denied" in msg)
                or ("schema mutation" in msg)
            ):
                schema_mutable = False
                logger.warning(
                    "⚠️  Provider forbids direct schema changes. Skipping CREATE TABLE."
                )
                logger.warning(
                    "   Guidance: use provider migration tooling (e.g. Code Conduit / Neon migrations) or run DDL via the DB admin panel."
                )
            else:
                # Unknown table-creation error — still keep connection but log details
                schema_mutable = False
                logger.error(f"❌ Table creation failed: {e}")
                logger.debug(e, exc_info=True)

        logger.info("✅ Database initialization complete (connection present)")
    except Exception as e:
        db_pool = None
        schema_mutable = False
        logger.error(f"❌ Database connection failed: {e}")
        logger.info("⚠️  Running without database")


app = FastAPI(title="MoStar GRID Coordinator")

# Add CORS - allow FRONTEND_ORIGIN env or allow all in dev
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN] if FRONTEND_ORIGIN != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db_connected = False


@app.on_event("startup")
async def startup_event():
    global db_connected
    conn_str = get_db_connection_string()

    if not conn_str:
        if not ALLOW_NO_DB:
            raise RuntimeError("Database configuration is required but not provided")
        logger.warning("⚠️  No database configuration found")
        return

    try:
        # Initialize actual DB pool and tables
        await init_database()
        if db_pool is not None:
            db_connected = True
            logger.info("✅ Database connected successfully")
        else:
            db_connected = False
            if not ALLOW_NO_DB:
                raise RuntimeError(
                    "Failed to connect to database and ALLOW_NO_DB is false"
                )
            logger.warning("⚠️  Running without database")
    except Exception as e:
        db_connected = False
        if not ALLOW_NO_DB:
            logger.error("Fatal DB error during startup")
            raise
        logger.error(f"❌ Database connection failed at startup: {str(e)}")
        logger.warning("⚠️  Continuing without database")


@app.on_event("shutdown")
async def shutdown_event():
    global db_pool
    try:
        if db_pool:
            await db_pool.close()
            logger.info("✅ Database pool closed")
    except Exception as e:
        logger.warning(f"Error closing DB pool: {e}")


@app.get("/")
async def root():
    return {"status": "online", "service": "MoStar GRID Coordinator"}


@app.get("/health")
async def health():
    db_info = {
        "connected": bool(db_pool is not None),
        "pool_min": getattr(db_pool, "_min_size", None) if db_pool else None,
        "pool_max": getattr(db_pool, "_max_size", None) if db_pool else None,
    }
    return {
        "status": "OK",
        "db": db_info,
        "consciousness": {
            "active_nodes": memory.metrics["active_nodes"],
            "coherence": memory.metrics["coherence"],
            "consciousness_uploads": memory.metrics["total_events"],
        },
    }


@app.get("/db/status")
async def db_status():
    return {
        "connected": db_pool is not None,
        "schema_mutable": schema_mutable,
        "pool_min": getattr(db_pool, "_min_size", None) if db_pool else None,
        "pool_max": getattr(db_pool, "_max_size", None) if db_pool else None,
    }


@app.post("/events")
async def submit_event(event: GridEvent):
    event_id = str(uuid.uuid4())
    resonance = 0.75
    woo = "The ancestors smile upon this scroll; it serves the covenant."

    response = {
        "event_id": event_id,
        "status": "processed",
        "resonance_score": resonance,
        "woo_judgment": woo,
    }

    memory.store_event(event, response)
    logger.info(f"Event processed: {event.event_type} from {event.source_agent}")

    # Persist to DB if available and schema allows it; otherwise keep in-memory only
    if db_pool and schema_mutable:
        try:
            async with db_pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO grid_events(event_id, event_type, source_agent, location, data, resonance_score)
                    VALUES($1, $2, $3, $4, $5::jsonb, $6)
                    """,
                    event_id,
                    event.event_type,
                    event.source_agent,
                    event.location,
                    json.dumps(event.data),
                    resonance,
                )
                logger.debug(f"Event {event_id} saved to DB")
        except Exception as e:
            logger.error(f"Failed to persist event {event_id}: {e}")
            logger.debug(e, exc_info=True)
    else:
        if db_pool and not schema_mutable:
            logger.warning(
                "DB connected but schema mutation not allowed; event stored in-memory only."
            )
        else:
            logger.info("No DB connection; event stored in-memory only.")

    return response


@app.websocket("/ws/live-stream")
async def ws_live_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        # Import psutil here to avoid startup dependency
        try:
            import psutil
            has_psutil = True
        except ImportError:
            has_psutil = False
            logger.warning("psutil not installed; using simulated metrics")
        
        while True:
            if has_psutil:
                cpu = psutil.cpu_percent(interval=None)
                mem = psutil.virtual_memory().percent
            else:
                # Fallback simulation
                cpu = 45.0 + (time.time() % 30) - 15
                mem = 60.0 + (time.time() % 20) - 10
            
            payload = {
                "ts": time.time(),
                "gridLatencyMs": int(max(1, 6 * (100 - cpu))),
                "cpu": cpu,
                "mem": mem,
                "service": "gateway",
                "event": "telemetry.tick",
                "mock": not has_psutil
            }
            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()


# New endpoint: trigger synthetic data generation in background
@app.post("/api/generate-synthetic-data")
async def generate_synthetic_data_api(
    size: int = 100,
    batch_size: int = 10000,
    scenario: Optional[str] = None,
    load_db: bool = False,
    truncate: bool = False,
    export: bool = False,
    background_tasks: BackgroundTasks = None,
):
    """
    Trigger the synthetic data pipeline as a background task.
    This spawns a separate process that runs synthetic_data/mostar_grid_sync.py
    so the API thread remains responsive.
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    script_path = os.path.join(project_root, "synthetic_data", "mostar_grid_sync.py")

    if not os.path.exists(script_path):
        return {
            "status": "error",
            "message": "Generator script not found",
            "path": script_path,
        }

    cmd = ["python", script_path, "--size", str(size), "--batch-size", str(batch_size)]
    if scenario:
        cmd += ["--scenario", scenario]
    if load_db:
        cmd.append("--load-db")
    if truncate:
        cmd.append("--truncate")
    if export:
        cmd.append("--export")

    # Use shlex for a readable command string in logs (but execute list form)
    cmd_str = " ".join(shlex.quote(p) for p in cmd)
    logger.info(f"Starting generator process: {cmd_str}")

    def _run_generator(cmd_list, cwd):
        try:
            proc = subprocess.Popen(cmd_list, cwd=cwd)
            logger.info(f"Generator started (pid={proc.pid})")
            proc.wait()
            logger.info(
                f"Generator finished (pid={proc.pid}, returncode={proc.returncode})"
            )
        except Exception as e:
            logger.error(f"Generator process failed: {e}")

    # Schedule background process
    background_tasks.add_task(_run_generator, cmd, project_root)

    return {"status": "started", "cmd": cmd_str}


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("MoStar GRID - First African AI Homeworld")
    logger.info(f"Mode: {GRID_MODE}")
    logger.info(f"Starting on http://{API_HOST}:{API_PORT}")
    logger.info("=" * 60)

    uvicorn.run(
        "grid_main:app", host=API_HOST, port=API_PORT, reload=True, log_level="info"
    )
