import asyncio
import logging
import time
import uuid
import asyncpg
from config import get_db_connection_string, API_PORT, API_HOST, ALLOW_NO_DB, GRID_MODE
from datetime import datetime, timezone
from typing import Dict, Any
import json
import traceback

from fastapi import FastAPI, WebSocket
from fastapi.websockets import WebSocketDisconnect
from pydantic import BaseModel
import uvicorn

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
        self.events.append({"event": event.dict(), "response": response, "timestamp": datetime.now().isoformat()})
        self.metrics["total_events"] += 1

memory = GridMemory()

# Database connection
db_pool = None
schema_mutable = True  # set to False if provider forbids schema changes

async def init_database():
    global db_pool, schema_mutable
    try:
        db_pool = await asyncpg.create_pool(
            get_db_connection_string(),
            min_size=2,
            max_size=10
        )
        logger.info("🔌 Connected to database (connection OK)")

        # Try to create tables; if provider forbids schema mutation, skip creation
        try:
            async with db_pool.acquire() as conn:
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS grid_events (
                        event_id TEXT PRIMARY KEY,
                        event_type TEXT,
                        source_agent TEXT,
                        location TEXT,
                        data JSONB,
                        resonance_score FLOAT,
                        timestamp TIMESTAMPTZ DEFAULT NOW()
                    )
                """)
            logger.info("✅ grid_events table ready")
            schema_mutable = True
        except Exception as e:
            msg = str(e).lower()
            # Detect Neon / managed-provider schema mutation policy message
            if ("covenantal" in msg) or ("forbidden" in msg) or ("permission denied" in msg) or ("schema mutation" in msg):
                schema_mutable = False
                logger.warning("⚠️  Provider forbids direct schema changes. Skipping CREATE TABLE.")
                logger.warning("   Guidance: use provider migration tooling (e.g. Code Conduit / Neon migrations) or run DDL via the DB admin panel.")
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
                raise RuntimeError("Failed to connect to database and ALLOW_NO_DB is false")
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
        "pool_max": getattr(db_pool, "_max_size", None) if db_pool else None
    }
    return {
        "status": "OK",
        "db": db_info,
        "consciousness": {
            "active_nodes": memory.metrics["active_nodes"],
            "coherence": memory.metrics["coherence"],
            "consciousness_uploads": memory.metrics["total_events"]
        }
    }

@app.get("/db/status")
async def db_status():
    return {
        "connected": db_pool is not None,
        "schema_mutable": schema_mutable,
        "pool_min": getattr(db_pool, "_min_size", None) if db_pool else None,
        "pool_max": getattr(db_pool, "_max_size", None) if db_pool else None
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
        "woo_judgment": woo
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
                    resonance
                )
                logger.debug(f"Event {event_id} saved to DB")
        except Exception as e:
            logger.error(f"Failed to persist event {event_id}: {e}")
            logger.debug(e, exc_info=True)
    else:
        if db_pool and not schema_mutable:
            logger.warning("DB connected but schema mutation not allowed; event stored in-memory only.")
        else:
            logger.info("No DB connection; event stored in-memory only.")

    return response

@app.websocket("/ws/live-stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message received: {data}")
    except Exception:
        await websocket.close()

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("MoStar GRID - First African AI Homeworld")
    logger.info(f"Mode: {GRID_MODE}")
    logger.info(f"Starting on http://{API_HOST}:{API_PORT}")
    logger.info("=" * 60)
    
    uvicorn.run(
        "grid_main:app",
        host=API_HOST,
        port=API_PORT,
        reload=True,
        log_level="info"
    )