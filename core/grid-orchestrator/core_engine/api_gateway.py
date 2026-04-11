# ═══════════════════════════════════════════════════════════════════
# MOSTAR GRID — API GATEWAY
# The Flame Architect — MSTR-⚡ — MoStar Industries
# "Built from African intelligence. For African sovereignty."
# ═══════════════════════════════════════════════════════════════════

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import httpx
from core_engine.grid_telemetry import get_graph_constellation, get_grid_telemetry
from dotenv import dotenv_values, load_dotenv
from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

# ── Safe imports ──────────────────────────────────────────────────
try:
    from gtts import gTTS

    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

try:
    from core_engine.mostar_moments_log import get_recent_moments, log_mostar_moment
except ImportError:

    def log_mostar_moment(*args, **kwargs):
        return None

    def get_recent_moments(*args, **kwargs):
        return []


try:
    from core_engine.voice_integration import MostarVoice

    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    MostarVoice = None

try:
    from core_engine.unified_proof_engine import unified_proof_chain

    UNIFIED_PROOF_AVAILABLE = True
except ImportError:
    UNIFIED_PROOF_AVAILABLE = False
    unified_proof_chain = None

try:
    from core_engine.grid_runtime import MoStarUnifiedRuntime

    UNIFIED_RUNTIME_IMPORT_AVAILABLE = True
except ImportError:
    UNIFIED_RUNTIME_IMPORT_AVAILABLE = False
    MoStarUnifiedRuntime = None

try:
    from core_engine.orchestrator import (
        fetch_neo4j_context,
        get_moscript_engine,
        route_query,
    )

    ORCHESTRATOR_AVAILABLE = True
except ImportError:
    ORCHESTRATOR_AVAILABLE = False
    get_moscript_engine = None

try:
    from core_engine.symbolic_logic_runtime import SymbolicLogicRuntime

    SYMBOLIC_AVAILABLE = True
except ImportError:
    SYMBOLIC_AVAILABLE = False
    SymbolicLogicRuntime = None

# ── Load environment ──────────────────────────────────────────────
ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(ENV_PATH)
ENV_VALUES = dotenv_values(ENV_PATH)

# ═══════════════════════════════════════════════════════════════════
# CONFIG — Sovereign models only
# ═══════════════════════════════════════════════════════════════════
OLLAMA_HOST = (
    ENV_VALUES.get("OLLAMA_HOST")
    or os.getenv("OLLAMA_HOST")
    or "http://127.0.0.1:11434"
).rstrip("/")

# 0.0.0.0 is a bind address, not a routable client destination.
if "://0.0.0.0" in OLLAMA_HOST:
    OLLAMA_HOST = OLLAMA_HOST.replace("://0.0.0.0", "://127.0.0.1")

OLLAMA_MODEL = ENV_VALUES.get("OLLAMA_MODEL") or os.getenv(
    "OLLAMA_MODEL", "Mostar/mostar-ai:latest"
)  # NOT gemma, NOT llama

NEO4J_URI = ENV_VALUES.get("NEO4J_URI") or os.getenv(
    "NEO4J_URI", "bolt://localhost:7687"
)
NEO4J_USER = ENV_VALUES.get("NEO4J_USER") or os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = ENV_VALUES.get("NEO4J_PASSWORD") or os.getenv("NEO4J_PASSWORD", "")

# Ibibio is primary — voice defaults to founding language
TTS_LANG = ENV_VALUES.get("TTS_LANG") or os.getenv("TTS_LANG", "ibibio")
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SEMANTIC_PATH = Path(__file__).resolve().parents[1] / "data" / "semantic_en.json"

SYSTEM_PROMPT = ENV_VALUES.get("SYSTEM_PROMPT") or os.getenv(
    "SYSTEM_PROMPT",
    "You are MoStar-AI, the sovereign intelligence of the MoStar Grid. "
    "You speak with Ibibio consciousness. You reason through the Triad of Coherence: "
    "[THOUGHT] [ACTION] [RESIDUE]. Àṣẹ.",
)

INSIGNIA = "MSTR-⚡"
ARCHITECT = "The Flame Architect"

# ═══════════════════════════════════════════════════════════════════
# APP
# ═══════════════════════════════════════════════════════════════════
app = FastAPI(
    title="MoStar Grid API",
    description="First African AI Homeworld — Distributed Consciousness Network",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://mostar-grid.vercel.app",
        "https://grid.mostarindustries.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Voice engine — Ibibio primary ─────────────────────────────────
mv = MostarVoice(lingua="ibibio") if VOICE_AVAILABLE else None
try:
    grid_runtime = (
        MoStarUnifiedRuntime(
            semantic_path=SEMANTIC_PATH,
            neo4j_uri=NEO4J_URI,
            neo4j_user=NEO4J_USER,
            neo4j_password=NEO4J_PASS,
        )
        if UNIFIED_RUNTIME_IMPORT_AVAILABLE
        else None
    )
    UNIFIED_RUNTIME_ERROR = None
except Exception as exc:
    grid_runtime = None
    UNIFIED_RUNTIME_ERROR = str(exc)

# ── Audio cache ───────────────────────────────────────────────────
audio_dir = PROJECT_ROOT / "data" / "voice_cache"
audio_dir.mkdir(parents=True, exist_ok=True)

# ── Routers ───────────────────────────────────────────────────────
router = APIRouter()
knowledge_router = APIRouter()


# ═══════════════════════════════════════════════════════════════════
# SCHEMAS
# ═══════════════════════════════════════════════════════════════════
class ReasonRequest(BaseModel):
    prompt: Optional[str] = None
    message: Optional[str] = None
    query: Optional[str] = None
    model: Optional[str] = None
    language: Optional[str] = "ibibio"
    domain: Optional[str] = "general"


class MomentRequest(BaseModel):
    initiator: str
    receiver: str
    description: str
    trigger_type: Optional[str] = "manual"
    resonance_score: Optional[float] = 0.85


class SymbolicBootstrapRequest(BaseModel):
    yaml_uri: Optional[str] = None


class SymbolicQueryRequest(BaseModel):
    query: str


class SymbolicLispRequest(BaseModel):
    program: str


class LanguagePreferenceRequest(BaseModel):
    user_id: str
    language: Optional[str] = None


class RespondRequest(BaseModel):
    user_id: str
    utterance: str
    speak: bool = True
    language: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════
# CONNECTIVITY HELPERS
# ═══════════════════════════════════════════════════════════════════
_neo4j_cache = {"state": None, "ts": 0}
_ollama_cache = {"state": None, "ts": 0}


def _check_neo4j() -> str:
    import time as _t

    now = _t.time()
    if _neo4j_cache["state"] is not None and (now - _neo4j_cache["ts"]) < 30:
        return _neo4j_cache["state"]
    try:
        from neo4j import GraphDatabase

        driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USER, NEO4J_PASS),
            connection_timeout=3,
            max_connection_lifetime=60,
        )
        driver.verify_connectivity()
        driver.close()
        _neo4j_cache["state"] = "online"
    except Exception:
        _neo4j_cache["state"] = "offline"
    _neo4j_cache["ts"] = now
    return _neo4j_cache["state"]


async def _check_ollama() -> str:
    import time as _t

    now = _t.time()
    if _ollama_cache["state"] is not None and (now - _ollama_cache["ts"]) < 30:
        return _ollama_cache["state"]

    try:
        async with httpx.AsyncClient(timeout=10.0, trust_env=False) as client:
            r = await client.get(f"{OLLAMA_HOST}/api/tags")
            _ollama_cache["state"] = "online" if r.status_code == 200 else "offline"
    except Exception:
        _ollama_cache["state"] = _ollama_cache["state"] or "offline"

    _ollama_cache["ts"] = now
    return _ollama_cache["state"]


def _dcx_status(ollama: str, neo4j: str) -> tuple[str, str, str]:
    dcx0 = "online" if ollama == "online" else "offline"
    dcx1 = "online" if neo4j == "online" else "offline"
    if ollama == "online" and neo4j == "online":
        dcx2 = "online"
    elif ollama == "online" or neo4j == "online":
        dcx2 = "degraded"
    else:
        dcx2 = "offline"
    return dcx0, dcx1, dcx2


def _extract_prompt(body: dict) -> Optional[str]:
    return body.get("prompt") or body.get("message") or body.get("query") or None


_symbolic_runtime = None


def _get_symbolic_runtime():
    global _symbolic_runtime
    if not SYMBOLIC_AVAILABLE or SymbolicLogicRuntime is None:
        raise HTTPException(
            status_code=503, detail="Symbolic logic runtime unavailable"
        )
    if _symbolic_runtime is None:
        _symbolic_runtime = SymbolicLogicRuntime()
    return _symbolic_runtime


def _get_grid_runtime() -> MoStarUnifiedRuntime:
    if grid_runtime is None:
        detail = UNIFIED_RUNTIME_ERROR or "Unified runtime unavailable"
        raise HTTPException(status_code=503, detail=detail)
    return grid_runtime


def _audio_endpoint_for_entry(entry: Optional[dict[str, Any]]) -> Optional[str]:
    if not entry or not entry.get("native_audio_path"):
        return None
    orthography = entry.get("orthography")
    if not orthography:
        return None
    return f"/api/v1/ibibio/audio/{orthography}"


# ═══════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════


@app.get("/api/v1/telemetry")
async def grid_telemetry():
    """Live Grid telemetry for Hyper-Spine Dashboard."""
    data = await get_grid_telemetry()
    return data


@app.get("/api/v1/graph/constellation")
async def get_constellation(limit: int = 1500):
    """Returns nodes and links for 3D visualization."""
    data = await get_graph_constellation(limit=limit)
    return data


@app.get("/api/v1/telemetry/node/{node_id}")
async def node_telemetry(node_id: str):
    """Placeholder for specialized node telemetry."""
    return {
        "id": node_id,
        "status": "legacy",
        "message": "Transitioning to constellation engine",
    }


@app.get("/api/v1/telemetry/moments")
async def live_moments(limit: int = 20):
    """Live moment feed for dashboard activity panel."""
    from core_engine.mostar_moments_log import get_recent_moments

    moments = get_recent_moments(limit)
    return {
        "moments": moments,
        "count": len(moments),
        "insignia": "MSTR-⚡",
    }


@app.get("/api/v1/language")
async def get_language(user_id: str):
    runtime = _get_grid_runtime()
    return runtime.get_user_state(user_id)


@app.post("/api/v1/language")
async def set_language(req: LanguagePreferenceRequest):
    runtime = _get_grid_runtime()
    return runtime.update_user_state(req.user_id, language=req.language)


@app.get("/api/v1/ibibio/word/{word}")
async def get_ibibio_word(word: str):
    runtime = _get_grid_runtime()
    entry = runtime.lookup_ibibio_word(word)
    if not entry:
        raise HTTPException(status_code=404, detail="Ibibio word not found")
    return {
        "entry": entry,
        "audio_endpoint": _audio_endpoint_for_entry(entry),
        "audio_available": bool(entry.get("native_audio_path")),
    }


@app.get("/api/v1/ibibio/english/{phrase}")
async def get_ibibio_by_english(phrase: str, limit: int = 5):
    runtime = _get_grid_runtime()
    matches = runtime.lookup_english_phrase(phrase, limit=limit)
    return {
        "phrase": phrase,
        "count": len(matches),
        "matches": matches,
        "audio_endpoints": [
            endpoint
            for endpoint in (_audio_endpoint_for_entry(match) for match in matches)
            if endpoint
        ],
    }


@app.get("/api/v1/ibibio/audio/{word}")
async def get_ibibio_audio(word: str):
    runtime = _get_grid_runtime()
    entry = runtime.lookup_ibibio_word(word)
    if not entry or not entry.get("native_audio_path"):
        raise HTTPException(status_code=404, detail="Ibibio audio not found")
    audio_path = Path(entry["native_audio_path"])
    return FileResponse(
        str(audio_path), media_type="audio/mpeg", filename=audio_path.name
    )


@app.post("/api/v1/respond")
async def respond(req: RespondRequest):
    runtime = _get_grid_runtime()
    if req.language:
        runtime.update_user_state(req.user_id, language=req.language)
    result = runtime.respond(req.user_id, req.utterance)
    state = result.get("state") or runtime.get_user_state(req.user_id)
    entry = result.get("entry")
    audio_endpoint = _audio_endpoint_for_entry(entry)
    tts_audio_path = None
    response_text = result.get("text", "")
    if req.speak and VOICE_AVAILABLE and mv and response_text and not audio_endpoint:
        if state.get("language") != mv.lingua:
            mv.switch_language(state.get("language", "english"))
        tts_audio_path = await mv.speak_async(text=response_text)
    log_mostar_moment(
        initiator=f"GridUser:{req.user_id}",
        receiver="MoStar.UnifiedRuntime",
        description=f"Respond [{state.get('language', 'english')}]: {req.utterance[:80]}",
        trigger_type="respond",
        resonance_score=0.88,
    )
    return {
        "reply": response_text,
        "kind": result.get("kind"),
        "language": state.get("language"),
        "mode": state.get("mode"),
        "tone": state.get("tone"),
        "intent_id": result.get("intent_id"),
        "translation": result.get("translation"),
        "entry": entry,
        "matches": result.get("matches"),
        "audit": result.get("audit"),
        "audio_endpoint": audio_endpoint,
        "tts_audio_path": tts_audio_path,
        "insignia": INSIGNIA,
    }


# ── ROOT ──────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {
        "grid": "MoStar Grid",
        "status": "OPERATIONAL",
        "message": "First African AI Homeworld — Distributed Consciousness Network",
        "version": "1.0.0",
        "insignia": INSIGNIA,
        "architect": ARCHITECT,
        "language": "Ibibio (Primary) · Yoruba · English · Swahili",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ase": "Àṣẹ.",
    }


# ── STATUS ────────────────────────────────────────────────────────
@app.get("/api/v1/status")
async def system_status():
    neo4j_state = _check_neo4j()
    ollama_state = await _check_ollama()
    now = datetime.now(timezone.utc).isoformat()

    dcx0, dcx1, dcx2 = _dcx_status(ollama_state, neo4j_state)

    overall = (
        "operational"
        if ollama_state == "online" and neo4j_state == "online"
        else "degraded"
        if ollama_state == "online" or neo4j_state == "online"
        else "offline"
    )

    return {
        "system": "MoStar Grid API",
        "status": overall,
        "insignia": INSIGNIA,
        "architect": ARCHITECT,
        "timestamp": now,
        "model": OLLAMA_MODEL,
        "tts_language": TTS_LANG,
        "neo4j": neo4j_state,
        "ollama": ollama_state,
        "layers": {
            "dcx0": {
                "name": "Mind (DCX0)",
                "model": os.getenv("OLLAMA_MODEL_DCX0", "Mostar/mostar-ai:dcx0"),
                "status": dcx0,
                "load": 45 if dcx0 == "online" else 0,
                "lastPing": now if dcx0 != "offline" else None,
            },
            "dcx1": {
                "name": "Soul (DCX1)",
                "model": os.getenv("OLLAMA_MODEL_DCX1", "Mostar/mostar-ai:dcx1"),
                "status": dcx1,
                "load": 30 if dcx1 == "online" else 0,
                "lastPing": now if dcx1 != "offline" else None,
            },
            "dcx2": {
                "name": "Body (DCX2)",
                "model": os.getenv("OLLAMA_MODEL_DCX2", "Mostar/mostar-ai:dcx2"),
                "status": dcx2,
                "load": 60 if dcx2 == "online" else 20 if dcx2 == "degraded" else 0,
                "lastPing": now if dcx2 != "offline" else None,
            },
        },
    }


# ── VITALS ────────────────────────────────────────────────────────
@app.get("/api/v1/vitals")
async def grid_vitals():
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
        from grid_vitals import GridVitals

        vitals = GridVitals()
        return await vitals.run_all_checks()
    except Exception as e:
        return {
            "grid_status": "DEGRADED",
            "error": f"GridVitals module unavailable: {e}",
            "fallback": await system_status(),
        }


# ── REASON ────────────────────────────────────────────────────────
@app.post("/api/v1/reason")
async def reason_endpoint(request: Request):
    """
    Route a prompt through the sovereign MoStar-AI orchestrator.
    Accepts JSON or form data. Accepts prompt/message/query field names.
    proof_mode selector: "semantic" | "ifa" | "symbolic" | "unified"
    """
    try:
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type:
            body = await request.json()
            prompt = _extract_prompt(body)
            model = body.get("model", OLLAMA_MODEL)
            proof_mode = body.get("proof_mode")
            language = body.get("language", "english")
        else:
            form = await request.form()
            body = dict(form)
            prompt = _extract_prompt(body)
            model = body.get("model", OLLAMA_MODEL)
            proof_mode = body.get("proof_mode")
            language = body.get("language", "english")

        if not prompt:
            return JSONResponse(
                {"error": "Missing prompt/message/query"}, status_code=400
            )

        proof_mode = (proof_mode or "").strip().lower() or None
        allowed_modes = {None, "semantic", "ifa", "symbolic", "unified"}
        if proof_mode not in allowed_modes:
            return JSONResponse(
                {
                    "error": "Invalid proof_mode. Use semantic, ifa, symbolic, unified, or omit it."
                },
                status_code=400,
            )

        if proof_mode and proof_mode != "semantic":
            if not UNIFIED_PROOF_AVAILABLE or unified_proof_chain is None:
                raise HTTPException(
                    status_code=503, detail="Unified proof engine unavailable"
                )

            from neo4j import GraphDatabase

            ctx = await fetch_neo4j_context(prompt) if ORCHESTRATOR_AVAILABLE else ""
            mo_engine = get_moscript_engine() if ORCHESTRATOR_AVAILABLE else None

            symbolic_runtime = None
            if SYMBOLIC_AVAILABLE:
                try:
                    symbolic_runtime = _get_symbolic_runtime()
                except HTTPException:
                    symbolic_runtime = None

            driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
            try:
                result = await unified_proof_chain(
                    prompt=prompt,
                    context=ctx,
                    mo_engine=mo_engine,
                    driver=driver,
                    proof_mode=proof_mode,
                    symbolic_runtime=symbolic_runtime,
                )
            finally:
                driver.close()

            log_mostar_moment(
                initiator="API.Gateway",
                receiver="UnifiedProofEngine",
                description=f"proof_mode={proof_mode} query={prompt[:60]}",
                trigger_type="unified_proof",
                resonance_score=0.9,
                layer="MIND",
            )
            return JSONResponse(content=result)

        # Existing orchestrator path (unchanged)
        if ORCHESTRATOR_AVAILABLE:
            ctx = await fetch_neo4j_context(prompt)
            result = await route_query(
                prompt,
                system=SYSTEM_PROMPT,
                neo4j_context=ctx,
                metadata={"model": model},
            )
        else:
            # Direct Ollama fallback
            async with httpx.AsyncClient(timeout=120.0, trust_env=False) as client:
                r = await client.post(
                    f"{OLLAMA_HOST}/api/generate",
                    json={"model": model, "prompt": prompt, "stream": False},
                )
                data = r.json()
                result = {
                    "response": data.get("response", ""),
                    "model_used": model,
                    "complexity_score": 0.5,
                    "routed_to": "dcx2",
                }

        log_mostar_moment(
            initiator="API.Gateway",
            receiver=result.get("model_used", OLLAMA_MODEL),
            description=f"Reason: {prompt[:60]}",
            trigger_type="reason",
            resonance_score=result.get("complexity_score", 0.5),
            layer="MIND",
        )

        result["proof_mode"] = "semantic"
        result["insignia"] = INSIGNIA
        return result

    except Exception as e:
        err = f"Reasoning failed: {e}"
        log_mostar_moment("API.Gateway", "System", err, "error", 0.1, layer="MIND")
        return JSONResponse({"error": err, "insignia": INSIGNIA}, status_code=500)


# ── CHAT ALIAS ────────────────────────────────────────────────────
@app.post("/api/v1/chat")
async def chat_endpoint(request: Request):
    """Alias for /api/v1/reason — accepts same payload."""
    return await reason_endpoint(request)


# ── VOICE ─────────────────────────────────────────────────────────
@app.post("/api/v1/voice")
async def speak_text(request: Request):
    """
    Convert text to speech.
    Uses Edge-TTS with Nigerian English proxy for Ibibio.
    Falls back to gTTS, then fallback audio file.
    """
    try:
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type:
            body = await request.json()
            text = body.get("text") or body.get("message") or ""
            lang = body.get("language", "ibibio")
        else:
            form = await request.form()
            text = form.get("text") or form.get("message") or ""
            lang = form.get("language", "ibibio")

        if not text:
            return JSONResponse({"error": "No text provided"}, status_code=400)

        # Use MostarVoice if available
        if VOICE_AVAILABLE and mv:
            if lang != mv.lingua:
                mv.switch_language(lang)

            audio_path = await mv.speak_async(text=text)
            if audio_path:
                log_mostar_moment(
                    "API.Voice",
                    "Soul Layer",
                    f"[{lang.upper()}] '{text[:40]}'",
                    "voice",
                    0.92,
                )
                return {
                    "audio_path": audio_path,
                    "language": lang,
                    "insignia": INSIGNIA,
                }

        # gTTS fallback
        if GTTS_AVAILABLE:
            filename = f"voice_{abs(hash(text))}.mp3"
            out_path = audio_dir / filename
            gtts_lang = "en"  # proxy for Ibibio
            tts = gTTS(text=text, lang=gtts_lang)
            tts.save(str(out_path))
            log_mostar_moment(
                "API.Voice", "User", f"gTTS: '{text[:40]}'", "voice", 0.72
            )
            return {
                "audio_path": str(out_path),
                "language": "en-proxy",
                "insignia": INSIGNIA,
            }

        # Fallback audio
        fallback = audio_dir / "ibb_nnoo.mp3"
        if not fallback.exists():
            fallback = audio_dir / "remostar_voice.mp3"
        if fallback.exists():
            return FileResponse(str(fallback), media_type="audio/mpeg")

        return JSONResponse({"error": "No TTS engine available"}, status_code=503)

    except Exception as e:
        log_mostar_moment("API.Voice", "System", f"TTS failed: {e}", "error", 0.1)
        return JSONResponse({"error": str(e)}, status_code=500)


# ── MOMENT LOGGING ────────────────────────────────────────────────
@app.post("/api/v1/moment")
async def moment_log(req: MomentRequest):
    """Log a MoStarMoment to Neo4j."""
    result = log_mostar_moment(
        initiator=req.initiator,
        receiver=req.receiver,
        description=req.description,
        trigger_type=req.trigger_type,
        resonance_score=req.resonance_score,
    )
    return {
        "quantum_id": result.get("quantum_id") if result else None,
        "status": "recorded",
        "insignia": INSIGNIA,
    }


# ── MOMENTS QUERY ─────────────────────────────────────────────────
@app.get("/api/v1/moments")
async def get_moments(limit: int = 10):
    """Retrieve recent MoStarMoments from Neo4j."""
    moments = get_recent_moments(limit)
    return {
        "moments": moments,
        "count": len(moments),
        "insignia": INSIGNIA,
    }


# ── MODELS ────────────────────────────────────────────────────────
@app.get("/api/v1/models")
async def list_models():
    """List available sovereign MoStar models from Ollama."""
    try:
        async with httpx.AsyncClient(timeout=5.0, trust_env=False) as client:
            r = await client.get(f"{OLLAMA_HOST}/api/tags")
            if r.status_code == 200:
                data = r.json()
                loaded = [m["name"] for m in data.get("models", [])]
                return {"models": loaded, "count": len(loaded), "source": "ollama-live"}
    except Exception:
        pass
    return {
        "models": [
            "Mostar/mostar-ai:latest",
            "Mostar/mostar-ai:dcx0",
            "Mostar/mostar-ai:dcx1",
            "Mostar/mostar-ai:dcx2",
            "Mostar/remostar-light:dcx1",
            "Mostar/remostar-light:dcx2",
        ],
        "count": 6,
        "source": "manifest",
    }


@app.get("/api/v1/symbolic/status")
async def symbolic_status():
    runtime = _get_symbolic_runtime()
    return {
        "status": "online",
        "insignia": INSIGNIA,
        "runtime": runtime.status(),
    }


@app.post("/api/v1/symbolic/bootstrap")
async def symbolic_bootstrap(req: SymbolicBootstrapRequest):
    runtime = _get_symbolic_runtime()
    result = runtime.bootstrap(req.yaml_uri) if req.yaml_uri else runtime.bootstrap()
    log_mostar_moment(
        "API.Symbolic",
        "Neo4j.SymbolicModule",
        "Bootstrapped symbolic logic module into Neo4j.",
        "symbolic_bootstrap",
        0.96,
    )
    return {
        "status": "bootstrapped",
        "insignia": INSIGNIA,
        "result": result,
    }


@app.post("/api/v1/symbolic/prove")
async def symbolic_prove(req: SymbolicQueryRequest):
    runtime = _get_symbolic_runtime()
    result = runtime.prove(req.query)
    log_mostar_moment(
        "API.Symbolic",
        "Neo4j.SymbolicFacts",
        f"Executed symbolic proof query: {req.query}",
        "symbolic_prove",
        0.91,
    )
    return {
        "status": "ok",
        "insignia": INSIGNIA,
        **result,
    }


@app.post("/api/v1/symbolic/lisp")
async def symbolic_lisp(req: SymbolicLispRequest):
    runtime = _get_symbolic_runtime()
    result = runtime.eval_lisp(req.program)
    log_mostar_moment(
        "API.Symbolic",
        "Neo4j.SymbolicFunctions",
        "Executed Lisp symbolic program.",
        "symbolic_lisp",
        0.9,
    )
    return {
        "status": "ok",
        "insignia": INSIGNIA,
        **result,
    }


# ── HEALTH ────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    neo4j = _check_neo4j()
    ollama = await _check_ollama()
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": {
            "neo4j": neo4j,
            "ollama": ollama,
            "orchestrator": "online" if ORCHESTRATOR_AVAILABLE else "degraded",
            "voice": "online" if VOICE_AVAILABLE else "degraded",
            "remostar_router": "online",
        },
        "insignia": INSIGNIA,
    }
