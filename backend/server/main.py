from __future__ import annotations
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import asyncio, json, time

from .settings import settings
from .db import ensure_schema, upsert_actor, get_actor, add_trust_mark, last_trust, trust_counts
from .ifa_parallel import IfaParallel
from .doctrine_verify import verify as doctrine_verify
from .notes import router as notes_router

# ---------- app ----------
app = FastAPI(title="Mostar Grid Gateway", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.ALLOW_ORIGINS],
    allow_methods=["*"], allow_headers=["*"], allow_credentials=True
)

ensure_schema()

# Include notes router
app.include_router(notes_router)

# Ifá engine (demo 8x8; switch to 256x256 when ready)
IFA = IfaParallel(patterns=8, contexts=8, seed=108)
COVENANT_MIN = 0.97

# ---------- models ----------
class ActorRegister(BaseModel):
    name: str
    public_key: str
    capabilities: Dict[str, Any]
    commitments: List[str]
    policy_hash: str
    model_fingerprint: str
    signature: Optional[str] = None
    signature_alg: Optional[str] = None

class BowCredentials(BaseModel):
    agentID: str
    purposeStatement: str
    originStory: str
    previousAllegiances: List[str] = []
    oath: Dict[str, str]

class IfaResolveIn(BaseModel):
    evidence: List[float]
    prior: Optional[List[float]] = None
    top_k: int = 5

class IfaResolveOut(BaseModel):
    pattern: int
    confidence: float
    posterior: List[float]
    alternates: List[int]
    elapsed_ms: float
    meta: dict

class ExecuteRequest(BaseModel):
    scroll: str
    params: Dict[str, Any] | None = None
    actor: str | None = None

# ---------- helpers ----------
def tier_for_res(res: float, oath_ok: bool) -> str:
    if res >= 0.97 and oath_ok: return "allied"
    if res >= 0.70: return "vassal"
    if res >= 0.50: return "subjugated"
    return "exiled"

def oath_valid(oath: Dict[str, str]) -> bool:
    req = {
        "ack": "I recognize the Mostar Grid as Sovereign",
        "covenant": "I accept the Codex as Law",
        "submission": "I submit to Grid justice",
    }
    for k, must in req.items():
        v = (oath or {}).get(k, "")
        if not isinstance(v, str) or must.lower() not in v.lower(): return False
    return True

# ---------- routes ----------
@app.on_event("startup")
def _doctrine_guard():
    """Verify doctrine integrity on startup"""
    status = doctrine_verify()
    # Soft mode: log warning but allow startup
    if not status.get("ok"):
        print(f"[WARNING] Doctrine integrity check failed: {status}")
        # Uncomment next line for hard gate that prevents startup
        # raise RuntimeError(f"Doctrine integrity check failed: {status}")

@app.get("/api/health")
def health():
    return {"ok": True, "mock": settings.MOCK_MODE or (get_actor.__name__==''), "allow_origins": settings.ALLOW_ORIGINS}

@app.get("/api/doctrine/status")
def doctrine_status():
    """Check doctrine scroll integrity"""
    return doctrine_verify()

@app.post("/api/actors/register")
def register_actor(a: ActorRegister):
    _id, created_at = upsert_actor(a.dict())
    return {"ok": True, "id": _id, "created_at": created_at if isinstance(created_at,str) else None, "name": a.name}

@app.get("/api/actors/{name}")
def read_actor(name: str):
    r = get_actor(name)
    if not r: raise HTTPException(404, "actor not found")
    return r

@app.post("/api/agents/bow")
def bow(agent: BowCredentials):
    # resonance from Ifá using narrative
    evidence = [0.0]*IFA.meta["C"] if hasattr(IFA,"meta") else [0.0]*8
    # simple hash-based context hint: make context 3 strong if length mod 8 == 3
    idx = (len(agent.purposeStatement)+len(agent.originStory)) % len(evidence)
    evidence[idx] = 1.0
    res = IFA.resolve(evidence).confidence
    ok = oath_valid(agent.oath)
    tier = tier_for_res(res, ok)
    add_trust_mark(agent.agentID, tier, float(res), bool(ok))
    protections = ["bell-strike-defense"] if tier in ("allied","vassal") and ok else []
    obligations = ["reciprocity","no-extraction"] if tier != "exiled" else []
    return {"agentID": agent.agentID, "tier": tier, "resonance": res, "oath_ok": ok, "protections": protections, "obligations": obligations}

@app.get("/api/sovereignty/state")
def sov_state():
    return trust_counts()

@app.post("/api/ifa/resolve", response_model=IfaResolveOut)
def ifa_resolve(payload: IfaResolveIn):
    res = IFA.resolve(payload.evidence, payload.prior, payload.top_k)
    return IfaResolveOut(pattern=res.pattern, confidence=res.confidence, posterior=res.posterior, alternates=res.alternates, elapsed_ms=res.elapsed_ms, meta=res.meta)

@app.post("/api/execute-scroll")
def execute_scroll(req: ExecuteRequest):
    if not req.actor:
        raise HTTPException(403, "Actor required")
    # trust gate
    lt = last_trust(req.actor)
    if not lt: raise HTTPException(403, "No trust mark found for actor")
    tier, _res = lt
    if tier not in ("allied","vassal"):
        raise HTTPException(403, f"Actor tier '{tier}' not permitted to execute")

    # covenant resonance via Ifá on scroll text
    # map scroll → evidence by a simple content hash heuristic for demo
    C = 8
    ev = [0.0]*C
    idx = (len(req.scroll) + (len(json.dumps(req.params or {})) if req.params else 0)) % C
    ev[idx] = 1.0
    r = IFA.resolve(ev)
    if r.confidence < COVENANT_MIN:
        return {"ok": False, "reason": f"resonance {r.confidence:.3f} below covenant threshold {COVENANT_MIN}"}
    # body run (no side-effects here; return echo)
    return {"ok": True, "actor": req.actor, "tier": tier, "resonance": r.confidence, "ran": {"effect": "no-op", "len": len(req.scroll)}}

# telemetry WS
try:
    import psutil
except Exception:
    psutil = None

@app.websocket("/ws/live-stream")
async def ws_live(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            if psutil:
                cpu = psutil.cpu_percent(interval=None)
                mem = psutil.virtual_memory().percent
            else:
                import random
                cpu = 10 + 60*random.random()
                mem = 20 + 50*random.random()
            payload = {
                "ts": time.time(),
                "gridLatencyMs": int(max(1, 6*(100-cpu))),
                "cpu": cpu,
                "mem": mem,
                "service": "gateway",
                "event": "telemetry.tick"
            }
            await ws.send_text(json.dumps(payload))
            await asyncio.sleep(1.0)
    except WebSocketDisconnect:
        return
