from __future__ import annotations
from typing import Any, Dict
from datetime import datetime, timezone
import os, asyncpg

from doctrine_verify import verify as doctrine_verify
from synthetic import get_generator_info  # will raise HTTPException if misconfigured

_pool: asyncpg.Pool | None = None

async def get_pool():
    global _pool
    if _pool is None:
        dsn = os.getenv("DATABASE_URL")
        if not dsn:
            raise RuntimeError("DATABASE_URL not set")
        _pool = await asyncpg.create_pool(dsn)
    return _pool

async def _count(pool, sql: str) -> int:
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql)
    return row["n"]

async def health_summary(app) -> Dict[str, Any]:
    # doctrine
    doc = doctrine_verify()
    doctrine_ok = bool(doc.get("ok"))

    # db counters
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("select 1")
        db_ok = True
        notes = await _count(pool, "select count(*) as n from notes")
        souls = await _count(pool, "select count(*) as n from soulprints")
        logs  = await _count(pool, "select count(*) as n from intent_logs")
        drifts= await _count(pool, "select count(*) as n from drift_events")
        reds  = await _count(pool, "select count(*) as n from redemptions")

    # ws metrics (maintained in app.state by your WS handler; defaults safe)
    ws = {
        "clients": getattr(app.state, "ws_clients", 0),
        "frames":  getattr(app.state, "ws_frames", 0),
        "last_latency_ms": getattr(app.state, "ws_last_latency_ms", None),
    }

    # synthetic status
    synthetic = {}
    try:
        g = get_generator_info()
        synthetic = {
            "configured": True,
            "generator_id": g["id"],
            "status": g["status"],
            "tables": [t["name"] for t in g["tables"]],
        }
    except Exception as e:
        msg = str(e).lower()
        busy = ("busy" in msg) or ("429" in msg)
        synthetic = {
            "configured": "not configured" not in msg,
            "status": "busy" if busy else "unavailable",
            "note": str(e),
        }

    return {
        "ts": datetime.now(timezone.utc).isoformat(),
        "api": {"status": "ok"},
        "doctrine": {"sealed": doctrine_ok, "scrolls": doc.get("scrolls", [])},
        "db": {"status": "ok" if db_ok else "fail",
               "notes": notes, "soulprints": souls,
               "intent_logs": logs, "drift_events": drifts, "redemptions": reds},
        "ws": ws,
        "synthetic": synthetic,
        "guardians": {"active": souls, "expected": ["mostar-ai","code-conduit","woo"]},
        "version": "v1.0.0-doctrine"
    }
