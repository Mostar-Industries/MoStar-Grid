# tools/scaffold-server.ps1  — create a complete backend/server (FastAPI)
$ErrorActionPreference = "Stop"
$root   = Resolve-Path "."
$back   = Join-Path $root "backend"
$server = Join-Path $back "server"
New-Item -ItemType Directory -Force -Path $server | Out-Null

# ---------------- files ----------------
# requirements
@'
fastapi>=0.115
uvicorn[standard]>=0.30
pydantic>=2.7
httpx>=0.27
python-dotenv>=1.0
psutil>=5.9
'@ | Set-Content -Encoding UTF8 (Join-Path $server "requirements.txt")

# settings.py
@'
import os

def _to_bool(v: str | None, default: bool=False) -> bool:
    if v is None: return default
    return v.strip().lower() in ("1","true","yes","y","on")

class Settings:
    MOCK_MODE = _to_bool(os.getenv("MOCK_MODE"), False)
    DATABASE_URL = os.getenv("DATABASE_URL")  # optional
    ALLOW_ORIGINS = os.getenv("ALLOW_ORIGINS", "http://localhost:5173")

settings = Settings()
'@ | Set-Content -Encoding UTF8 (Join-Path $server "settings.py")

# db.py  (optional Neon; falls back to file storage if psycopg not available)
@'
from __future__ import annotations
import json, os, threading
from typing import Any, Dict, Optional, List, Tuple
from .settings import settings

pool = None
_use_file = False
_data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(_data_dir, exist_ok=True)
_actors_file = os.path.join(_data_dir, "actors.json")
_trust_file  = os.path.join(_data_dir, "trust_marks.json")
_lock = threading.Lock()

try:
    import psycopg
    if settings.DATABASE_URL:
        pool = psycopg.Connection.connect(settings.DATABASE_URL)
    else:
        _use_file = True
except Exception:
    _use_file = True
    pool = None

def ensure_schema() -> None:
    if _use_file or pool is None:
        for path in (_actors_file, _trust_file):
            if not os.path.exists(path):
                with open(path, "w", encoding="utf-8") as f: json.dump([], f)
        return
    with pool.cursor() as cur:
        cur.execute("""
        create table if not exists actors (
          id bigserial primary key,
          name text unique not null,
          public_key text not null,
          capabilities jsonb not null,
          commitments jsonb not null,
          policy_hash text not null,
          model_fingerprint text not null,
          created_at timestamptz default now()
        );
        create table if not exists trust_marks (
          id bigserial primary key,
          actor_name text not null,
          tier text not null,
          resonance numeric not null,
          oath_ok boolean not null,
          created_at timestamptz default now()
        );
        """)
        pool.commit()

def upsert_actor(a: Dict[str, Any]) -> Tuple[int, str]:
    if _use_file or pool is None:
        with _lock:
            data = []
            if os.path.exists(_actors_file):
                data = json.load(open(_actors_file, "r", encoding="utf-8"))
            # replace or append
            data = [x for x in data if x.get("name") != a["name"]]
            data.append(a)
            json.dump(data, open(_actors_file, "w", encoding="utf-8"), indent=2)
        return (len(data), "file")
    with pool.cursor() as cur:
        cur.execute("""
        insert into actors(name, public_key, capabilities, commitments, policy_hash, model_fingerprint)
        values (%s,%s,%s::jsonb,%s::jsonb,%s,%s)
        on conflict (name) do update set
          public_key=excluded.public_key,
          capabilities=excluded.capabilities,
          commitments=excluded.commitments,
          policy_hash=excluded.policy_hash,
          model_fingerprint=excluded.model_fingerprint
        returning id, now()::text
        """, (a["name"], a["public_key"], json.dumps(a["capabilities"]), json.dumps(a["commitments"]), a["policy_hash"], a["model_fingerprint"]))
        row = cur.fetchone()
        pool.commit()
        return (row[0], row[1])

def get_actor(name: str) -> Optional[Dict[str, Any]]:
    if _use_file or pool is None:
        if not os.path.exists(_actors_file): return None
        for x in json.load(open(_actors_file, "r", encoding="utf-8")):
            if x.get("name") == name: return x
        return None
    with pool.cursor() as cur:
        cur.execute("select name, public_key, capabilities, commitments, policy_hash, model_fingerprint from actors where name=%s", (name,))
        r = cur.fetchone()
        if not r: return None
        return {"name": r[0], "public_key": r[1], "capabilities": r[2], "commitments": r[3], "policy_hash": r[4], "model_fingerprint": r[5]}

def add_trust_mark(actor: str, tier: str, resonance: float, oath_ok: bool) -> None:
    if _use_file or pool is None:
        with _lock:
            data = []
            if os.path.exists(_trust_file):
                data = json.load(open(_trust_file, "r", encoding="utf-8"))
            data.append({"actor_name": actor, "tier": tier, "resonance": resonance, "oath_ok": oath_ok})
            json.dump(data, open(_trust_file, "w", encoding="utf-8"), indent=2)
        return
    with pool.cursor() as cur:
        cur.execute("insert into trust_marks(actor_name, tier, resonance, oath_ok) values (%s,%s,%s,%s)", (actor, tier, resonance, oath_ok))
        pool.commit()

def last_trust(actor: str) -> Optional[Tuple[str, float]]:
    if _use_file or pool is None:
        if not os.path.exists(_trust_file): return None
        data = [x for x in json.load(open(_trust_file, "r", encoding="utf-8")) if x.get("actor_name")==actor]
        if not data: return None
        t = data[-1]
        return (t["tier"], float(t["resonance"]))
    with pool.cursor() as cur:
        cur.execute("select tier, resonance from trust_marks where actor_name=%s order by created_at desc limit 1", (actor,))
        r = cur.fetchone()
        return (r[0], float(r[1])) if r else None

def trust_counts() -> Dict[str,int]:
    if _use_file or pool is None:
        if not os.path.exists(_trust_file): return {"allied":0,"vassal":0,"subjugated":0,"exiled":0}
        data = json.load(open(_trust_file, "r", encoding="utf-8"))
        from collections import Counter
        c = Counter([x.get("tier","exiled") for x in data])
        return {"allied": c.get("allied",0), "vassal": c.get("vassal",0), "subjugated": c.get("subjugated",0), "exiled": c.get("exiled",0)}
    with pool.cursor() as cur:
        res = {}
        for t in ("allied","vassal","subjugated","exiled"):
            cur.execute("select count(*) from trust_marks where tier=%s", (t,))
            res[t] = int(cur.fetchone()[0])
        return res
'@ | Set-Content -Encoding UTF8 (Join-Path $server "db.py")

# ifa_parallel.py
@'
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import time, random

def _normalize(vec: List[float]) -> List[float]:
    s = sum(x for x in vec if x > 0.0)
    if s <= 0.0:
        n = len(vec)
        return [1.0/n]*n
    return [max(0.0,x)/s for x in vec]

@dataclass
class IfaResult:
    pattern: int
    confidence: float
    posterior: List[float]
    alternates: List[int]
    elapsed_ms: float
    meta: Dict[str,Any]

class IfaParallel:
    def __init__(self, patterns: int=8, contexts: int=8, seed: int=108):
        assert patterns>1 and contexts>1
        self.P, self.C = patterns, contexts
        self.rng = random.Random(seed)
        raw = [[self.rng.random()+1e-6 for _ in range(self.P)] for __ in range(self.C)]
        for i in range(self.P):
            col_sum = sum(raw[j][i] for j in range(self.C))
            for j in range(self.C):
                raw[j][i] = raw[j][i]/col_sum
        self.likelihood = raw  # C x P
        self.prior = [1.0/self.P]*self.P

    def resolve(self, evidence: List[float], prior: Optional[List[float]]=None, top_k: int=5) -> IfaResult:
        if len(evidence)!=self.C: raise ValueError("evidence length mismatch")
        ev = _normalize(evidence)
        pr = _normalize(prior) if prior is not None else self.prior
        t0 = time.perf_counter()
        score = [0.0]*self.P
        for i in range(self.P):
            s = 0.0
            for j in range(self.C):
                s += self.likelihood[j][i]*ev[j]
            score[i] = pr[i]*s
        s = sum(score) or 1.0
        post = [x/s for x in score]
        best = max(range(self.P), key=lambda i: post[i])
        order = sorted(range(self.P), key=lambda i: post[i], reverse=True)
        alts = [i for i in order if i!=best][:max(0, top_k)]
        return IfaResult(pattern=best, confidence=post[best], posterior=post, alternates=alts, elapsed_ms=(time.perf_counter()-t0)*1000.0, meta={"P":self.P,"C":self.C})
'@ | Set-Content -Encoding UTF8 (Join-Path $server "ifa_parallel.py")

# main.py
@'
from __future__ import annotations
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import asyncio, json, time

from .settings import settings
from .db import ensure_schema, upsert_actor, get_actor, add_trust_mark, last_trust, trust_counts
from .ifa_parallel import IfaParallel

# ---------- app ----------
app = FastAPI(title="Mostar Grid Gateway", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.ALLOW_ORIGINS],
    allow_methods=["*"], allow_headers=["*"], allow_credentials=True
)

ensure_schema()

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
@app.get("/api/health")
def health():
    return {"ok": True, "mock": settings.MOCK_MODE or (get_actor.__name__==''), "allow_origins": settings.ALLOW_ORIGINS}

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
'@ | Set-Content -Encoding UTF8 (Join-Path $server "main.py")

# __init__.py (empty file)
"" | Set-Content -Encoding UTF8 (Join-Path $server "__init__.py")

Write-Host "[OK] backend/server scaffolded." -ForegroundColor Green
Write-Host "Next:"
Write-Host "  python -m venv backend\\server\\.venv"
Write-Host "  backend\\server\\.venv\\Scripts\\Activate.ps1"
Write-Host "  pip install -r backend\\server\\requirements.txt"
Write-Host "  uvicorn backend.server.main:app --reload --port 8000"
