from __future__ import annotations
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Query, Body
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Set
from datetime import datetime, timezone
import json, os, asyncio, asyncpg

router = APIRouter(prefix="/api/bus", tags=["bus"])

# ---------- DB ----------
_pool: asyncpg.Pool | None = None

async def get_pool():
    global _pool
    if _pool is None:
        dsn = os.getenv("DATABASE_URL")
        if not dsn:
            raise RuntimeError("DATABASE_URL not set")
        _pool = await asyncpg.create_pool(dsn)
    return _pool

async def _ensure():
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS grid_events (
          id BIGSERIAL PRIMARY KEY,
          ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
          topic TEXT NOT NULL,
          origin TEXT NOT NULL,
          target TEXT,
          payload JSONB NOT NULL,
          sig TEXT
        );
        """)
        await conn.execute("""
        CREATE INDEX IF NOT EXISTS grid_events_topic_ts_idx
          ON grid_events(topic, ts DESC);
        """)

@router.on_event("startup")
async def startup():
    await _ensure()

async def _soul_active(slug: str) -> bool:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT active FROM soulprints WHERE slug=$1", slug)
    return bool(row and row["active"])

# ---------- Models ----------
class BusPublish(BaseModel):
    origin: str = Field(min_length=2)   # must be active soulprint
    topic: str = Field(min_length=2, pattern=r"^[a-z0-9\.\-\_:]+$")
    payload: Dict[str, Any]
    target: Optional[str] = None        # direct message (optional)
    sig: Optional[str] = None           # placeholder for future signatures

# ---------- REST ----------
@router.get("/topics")
async def list_topics(limit: int = 32):
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT topic, COUNT(*) AS n FROM grid_events GROUP BY topic ORDER BY n DESC LIMIT $1", limit)
    return [dict(row) for row in rows]

@router.get("/history")
async def history(topic: str, limit: int = 100):
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
          SELECT id, ts, topic, origin, target, payload
          FROM grid_events
          WHERE topic=$1
          ORDER BY id DESC
          LIMIT $2
        """, topic, limit)
    return [dict(row) for row in rows[::-1]]

@router.post("/publish")
async def publish(msg: BusPublish = Body(...)):
    if not await _soul_active(msg.origin):
        raise HTTPException(403, f"origin '{msg.origin}' not active in soul registry")
    if msg.target and not await _soul_active(msg.target):
        raise HTTPException(404, f"target '{msg.target}' not found")

    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
          INSERT INTO grid_events(topic, origin, target, payload, sig)
          VALUES($1, $2, $3, $4::jsonb, $5)
          RETURNING id, ts
        """, msg.topic, msg.origin, msg.target, json.dumps(msg.payload), msg.sig)

    envelope = {
        "id": row["id"],
        "ts": row["ts"].isoformat(),
        "topic": msg.topic,
        "origin": msg.origin,
        "target": msg.target,
        "payload": msg.payload,
    }

    # broadcast
    try:
        q: asyncio.Queue = router.apps.state.bus_queue  # type: ignore[attr-defined]
    except Exception:
        raise HTTPException(500, "bus queue not initialized")
    q.put_nowait(envelope)
    router.apps.state.bus_events = getattr(router.apps.state, "bus_events", 0) + 1  # type: ignore
    return {"ok": True, **envelope}

# ---------- WebSocket (subscribe) ----------
# URL: ws://.../ws/bus?topics=sectorx.alert,doctrine.change (or omit for all)
@router.websocket("/ws/bus")
async def ws_bus(ws: WebSocket, topics: Optional[str] = Query(None)):
    await ws.accept()
    app = router.apps
    app.state.bus_clients = getattr(app.state, "bus_clients", 0) + 1
    try:
        subs: Optional[Set[str]] = None
        if topics:
            subs = {t.strip() for t in topics.split(",") if t.strip()}
        # register reader
        queue: asyncio.Queue = app.state.bus_queue  # type: ignore
        # lightweight fan-out: each client loops on global queue snapshots
        # (for higher scale use a proper pub/sub)
        last_seen = 0
        while True:
            env = await queue.get()  # type: ignore
            # topic filter
            if subs and env["topic"] not in subs:
                continue
            await ws.send_text(json.dumps(env))
    except WebSocketDisconnect:
        pass
    finally:
        app.state.bus_clients = max(0, getattr(app.state, "bus_clients", 1) - 1)
        await ws.close()
