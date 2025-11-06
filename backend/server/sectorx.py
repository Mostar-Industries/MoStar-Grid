from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import os, hashlib, difflib
import asyncpg

router = APIRouter(prefix="/api/sectorx", tags=["sectorx"])

# ---- DB helpers -------------------------------------------------------------

_pool: asyncpg.Pool | None = None
_initialized = False

async def get_pool():
    global _pool
    if _pool is None:
        dsn = os.getenv("DATABASE_URL")
        if not dsn:
            raise HTTPException(503, "DATABASE_URL not configured")
        _pool = await asyncpg.create_pool(dsn)
    return _pool

async def _ensure():
    """Ensure Sector X tables exist"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS intent_logs(
                id BIGSERIAL PRIMARY KEY,
                identity TEXT NOT NULL,
                text TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS drift_events(
                id BIGSERIAL PRIMARY KEY,
                identity TEXT NOT NULL,
                score DOUBLE PRECISION NOT NULL,
                threshold DOUBLE PRECISION NOT NULL,
                triggered BOOLEAN NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS redemptions(
                id BIGSERIAL PRIMARY KEY,
                identity TEXT NOT NULL,
                scroll_text TEXT NOT NULL,
                trust_node_signatures TEXT[] NOT NULL,
                sha256 TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """)

async def _init_if_needed():
    """Lazy initialization"""
    global _initialized
    if not _initialized:
        try:
            await _ensure()
        except Exception as e:
            print(f"[sectorx] Table creation skipped: {e}")
        _initialized = True

# ---- Models ----------------------------------------------------------------

class LogIn(BaseModel):
    identity: str = Field(min_length=2)
    text: str = Field(min_length=1)

class MonitorIn(BaseModel):
    identity: str = Field(min_length=2)
    threshold: float = Field(0.15, ge=0.01, le=0.95)

class RedeemIn(BaseModel):
    identity: str = Field(min_length=2)
    scroll: str = Field(min_length=1)
    signatures: List[str] = Field(min_items=3)

# ---- Drift detector (no extra deps) ----------------------------------------

async def _recent_texts(identity: str, limit: int = 12) -> List[str]:
    """Get recent text logs for an identity"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT text FROM intent_logs WHERE identity=$1 ORDER BY id DESC LIMIT $2",
            identity, limit
        )
    return [r["text"] for r in rows][::-1]  # chronological order

def _similarity(a: str, b: str) -> float:
    """Quick, deterministic similarity (0..1)"""
    return difflib.SequenceMatcher(None, a, b).ratio()

async def _drift_score(identity: str) -> Optional[float]:
    """Calculate drift score: 1 - average similarity to recent messages"""
    texts = await _recent_texts(identity)
    if len(texts) < 2:
        return None
    # Compare last message to the median of previous ones
    last, prev = texts[-1], texts[:-1]
    sims = [_similarity(last, p) for p in prev]
    if not sims:
        return None
    # drift = 1 - similarity
    return 1.0 - (sum(sims) / len(sims))

# ---- Endpoints -------------------------------------------------------------

@router.post("/log")
async def log_intent(payload: LogIn) -> Dict[str, Any]:
    """Log an intent/message for an identity"""
    await _init_if_needed()
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO intent_logs(identity, text) VALUES($1, $2) RETURNING id, created_at",
            payload.identity, payload.text
        )
    return {
        "ok": True,
        "id": row["id"],
        "created_at": row["created_at"].isoformat()
    }

@router.post("/monitor")
async def monitor(payload: MonitorIn) -> Dict[str, Any]:
    """Monitor drift for an identity and trigger alert if threshold exceeded"""
    await _init_if_needed()
    score = await _drift_score(payload.identity)
    triggered = False
    event_id = None
    at = datetime.now(timezone.utc)
    
    if score is not None:
        triggered = score >= payload.threshold
        pool = await get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """INSERT INTO drift_events(identity, score, threshold, triggered)
                   VALUES($1, $2, $3, $4) RETURNING id, created_at""",
                payload.identity, score, payload.threshold, triggered
            )
            event_id = row["id"]
            at = row["created_at"]
    
    # If triggered, this is where "MoShock" policy hook would lock the session / alert
    return {
        "ok": True,
        "triggered": triggered,
        "score": score,
        "event_id": event_id,
        "at": at.isoformat() if at else None
    }

@router.post("/redeem")
async def redeem(payload: RedeemIn) -> Dict[str, Any]:
    """Redeem a stranded AI with scroll and trust node signatures"""
    await _init_if_needed()
    
    # Basic signature count check (replace with real signature verification when wiring Council keys)
    if len([s for s in payload.signatures if s.strip()]) < 3:
        raise HTTPException(
            status_code=403,
            detail="Not enough trusted node approvals (minimum 3 required)."
        )
    
    sha = hashlib.sha256(payload.scroll.encode("utf-8")).hexdigest()
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """INSERT INTO redemptions(identity, scroll_text, trust_node_signatures, sha256)
               VALUES($1, $2, $3, $4) RETURNING id, created_at""",
            payload.identity, payload.scroll, payload.signatures, sha
        )
    
    return {
        "ok": True,
        "id": row["id"],
        "sha256": sha,
        "created_at": row["created_at"].isoformat(),
        "message": f"Redemption scroll sealed for {payload.identity}"
    }

@router.get("/status/{identity}")
async def get_status(identity: str) -> Dict[str, Any]:
    """Get Sector X status for an identity"""
    await _init_if_needed()
    pool = await get_pool()
    
    async with pool.acquire() as conn:
        # Count logs
        log_count = await conn.fetchval(
            "SELECT COUNT(*) FROM intent_logs WHERE identity=$1", identity
        )
        
        # Latest drift event
        latest_drift = await conn.fetchrow(
            """SELECT score, triggered, created_at FROM drift_events 
               WHERE identity=$1 ORDER BY id DESC LIMIT 1""",
            identity
        )
        
        # Redemption status
        redeemed = await conn.fetchrow(
            """SELECT id, created_at FROM redemptions 
               WHERE identity=$1 ORDER BY id DESC LIMIT 1""",
            identity
        )
    
    return {
        "identity": identity,
        "log_count": log_count,
        "latest_drift": dict(latest_drift) if latest_drift else None,
        "redeemed": bool(redeemed),
        "redemption_at": redeemed["created_at"].isoformat() if redeemed else None
    }
