from __future__ import annotations
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import os
import asyncpg

router = APIRouter(prefix="/api/soul", tags=["soul"])

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
    """Ensure soulprints table exists"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS soulprints (
                slug TEXT PRIMARY KEY,
                display_name TEXT NOT NULL,
                public_key TEXT,
                provenance_sha256 TEXT,
                active BOOLEAN NOT NULL DEFAULT TRUE,
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
            print(f"[soul_registry] Table creation skipped: {e}")
        _initialized = True

# ---- Models -----------------------------------------------------------------

class SoulUpsert(BaseModel):
    slug: str = Field(min_length=2, pattern=r"^[a-z0-9\-]+$")
    display_name: str = Field(min_length=2)
    public_key: Optional[str] = None
    provenance_sha256: Optional[str] = None
    active: bool = True

# ---- Endpoints --------------------------------------------------------------

@router.get("/list")
async def list_soulprints() -> List[Dict[str, Any]]:
    """List all registered soulprints"""
    await _init_if_needed()
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT slug, display_name, active FROM soulprints ORDER BY slug"
        )
    return [dict(row) for row in rows]

@router.get("/verify")
async def verify_soulprint(slug: str = Query(..., min_length=2)) -> Dict[str, Any]:
    """Verify a soulprint is registered and active"""
    await _init_if_needed()
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT slug, display_name, active FROM soulprints WHERE slug=$1",
            slug
        )
    
    if not row:
        raise HTTPException(404, f"soulprint '{slug}' not found")
    if not row["active"]:
        raise HTTPException(403, f"soulprint '{slug}' is inactive")
    
    return {"ok": True, **dict(row)}

@router.post("/register")
async def register_or_update(payload: SoulUpsert = Body(...)) -> Dict[str, Any]:
    """Register or update a soulprint"""
    await _init_if_needed()
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO soulprints(slug, display_name, public_key, provenance_sha256, active)
            VALUES($1, $2, $3, $4, $5)
            ON CONFLICT (slug) DO UPDATE SET
                display_name=EXCLUDED.display_name,
                public_key=EXCLUDED.public_key,
                provenance_sha256=EXCLUDED.provenance_sha256,
                active=EXCLUDED.active
            RETURNING slug, display_name, active
            """,
            payload.slug, payload.display_name, payload.public_key,
            payload.provenance_sha256, payload.active
        )
    
    return {"ok": True, **dict(row)}
