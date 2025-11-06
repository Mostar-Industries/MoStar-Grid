from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone
import os
import asyncpg

router = APIRouter(prefix="/api/notes", tags=["notes"])

async def get_conn():
    """Get a database connection"""
    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        raise HTTPException(503, "DATABASE_URL not configured")
    return await asyncpg.connect(dsn)

_initialized = False

async def _ensure():
    """Try to ensure notes table exists (may be blocked by provider)"""
    conn = await get_conn()
    try:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS notes(
                id BIGSERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                body TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """)
    except Exception as e:
        # Provider may block CREATE TABLE, that's okay if table already exists
        print(f"[notes] Table creation skipped (provider restriction or table exists): {e}")
    finally:
        await conn.close()

async def _init_if_needed():
    """Ensure database table is initialized"""
    global _initialized
    if not _initialized:
        try:
            await _ensure()
        except Exception:
            pass  # Continue even if table creation fails
        _initialized = True

class NoteIn(BaseModel):
    title: str
    body: str

@router.get("")
async def list_notes():
    await _init_if_needed()
    conn = await get_conn()
    try:
        rows = await conn.fetch("SELECT id, title, body, created_at FROM notes ORDER BY id DESC")
        return [dict(row) for row in rows]
    finally:
        await conn.close()

@router.post("")
async def create_note(n: NoteIn):
    await _init_if_needed()
    conn = await get_conn()
    try:
        row = await conn.fetchrow(
            "INSERT INTO notes(title, body) VALUES($1, $2) RETURNING id, title, body, created_at",
            n.title, n.body
        )
        if not row:
            raise HTTPException(500, "Insert failed")
        return dict(row)
    finally:
        await conn.close()
