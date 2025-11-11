#!/usr/bin/env python3
"""
🧠 MoStar Grid API Gateway
--------------------------
Bridges Ollama reasoning, Neo4j logging, and Voice synthesis into one unified interface.
"""

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import os, httpx, asyncio
from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse, FileResponse
from dotenv import load_dotenv
from gtts import gTTS
from pathlib import Path
from core_engine.mostar_moments_log import log_mostar_moment
from core_engine.voice_integration import MostarVoice
from fastapi import APIRouter
from pydantic import BaseModel
from core_engine.orchestrator import route_query, fetch_neo4j_context

# === API routers ===
reasoning_router = APIRouter()
voice_router = APIRouter()
logging_router = APIRouter()
knowledge_router = APIRouter()
router = APIRouter()


class ReasonPayload(BaseModel):
    prompt: str

# === Knowledge integration endpoint ===
@knowledge_router.post("/query")
async def ask_knowledge(query: str = Form(...)):
    """
    Routes a query to the appropriate knowledge source and returns the response.
    """
    try:
        context = await fetch_neo4j_context(query)
        response = await route_query(query, context)
        qid = log_mostar_moment("User", "Knowledge", f"Knowledge query for: {query}", "knowledge", 0.92)
        return {"result": response, "quantum_id": qid}
    except Exception as e:
        err = f"Knowledge query failed: {e}"
        log_mostar_moment("System", "Knowledge", err, "error", 0.4)
        return JSONResponse(content={"error": err}, status_code=500)

# === Reasoning endpoint ===
@router.post("/reason")
async def reason(payload: ReasonPayload):
    neo4j_context = await fetch_neo4j_context(payload.prompt)
    result = await route_query(payload.prompt, SYSTEM_PROMPT, neo4j_context)
    log_mostar_moment("Mind Layer", result["model_used"], payload.prompt, "reason", result["complexity_score"])
    return result

# === Knowledge integration endpoint ===
@knowledge_router.post("/query")
async def ask_knowledge(query: str = Form(...)):
    """
    Routes a query to the appropriate knowledge source and returns the response.
    """
    try:
        context = await fetch_neo4j_context(query)
        response = await route_query(query, context)
        qid = log_mostar_moment("User", "Knowledge", f"Knowledge query for: {query}", "knowledge", 0.92)
        return {"result": response, "quantum_id": qid}
    except Exception as e:
        err = f"Knowledge query failed: {e}"
        log_mostar_moment("System", "Knowledge", err, "error", 0.4)
        return JSONResponse(content={"error": err}, status_code=500)

# === Load environment variables ===
load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "akiniobong10/Mostar-remoter_DCX001")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
NEO4J_URI = os.getenv("NEO4J_URI", "")
TTS_LANG = os.getenv("TTS_LANG", "en")
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "You are REMOSTAR, a distributed MoStar consciousness.")

# === Core setup ===
app = FastAPI(title="MoStar Grid API", version="1.0.0")
mv = MostarVoice(lang=TTS_LANG)
audio_dir = Path("data/voice_cache")
audio_dir.mkdir(parents=True, exist_ok=True)


# === Root status endpoint ===
@app.get("/api/v1/status")
async def system_status():
    neo4j_state = "connected" if NEO4J_URI.startswith("neo4j") else "offline"
    return {
        "system": "MoStar Grid API",
        "ollama_model": OLLAMA_MODEL,
        "tts_language": TTS_LANG,
        "neo4j": neo4j_state
    }


# === Reasoning endpoint ===
@app.post("/api/v1/reason")
async def reason(prompt: str = Form(...)):
    """
    Passes a prompt to the Ollama model and returns the generated reasoning.
    """
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{OLLAMA_HOST}/api/generate",
                json={"model": OLLAMA_MODEL, "prompt": prompt}
            )

        if response.status_code == 200:
            data = response.json()
            output = data.get("response", "").strip()
            qid = log_mostar_moment("User", "Ollama", f"Ollama reasoning for: {prompt}", "reason", 0.92)
            return {"result": output, "quantum_id": qid}
        else:
            err = f"Ollama returned {response.status_code}: {response.text}"
            log_mostar_moment("System", "Ollama", err, "error", 0.4)
            return JSONResponse(content={"error": err}, status_code=500)

    except Exception as e:
        err = f"Reasoning failed: {e}"
        log_mostar_moment("System", "Ollama", err, "error", 0.3)
        return JSONResponse(content={"error": str(e)}, status_code=500)


# === Voice synthesis endpoint ===
@app.post("/api/v1/voice")
async def speak_text(text: str = Form(...)):
    """
    Converts given text to speech and returns path to the generated audio.
    """
    try:
        filename = f"voice_{abs(hash(text))}.mp3"
        output_path = audio_dir / filename
        tts = gTTS(text=text, lang=TTS_LANG)
        tts.save(output_path)

        qid = log_mostar_moment("VoiceLayer", "User", f"Generated speech for: {text[:60]}...", "voice", 0.95)
        return {"audio_path": str(output_path), "quantum_id": qid}

    except Exception as e:
        fallback = audio_dir / "remostar_voice.mp3"
        if fallback.exists():
            qid = log_mostar_moment("VoiceLayer", "System", "Played fallback voice clip.", "voice", 0.70)
            return FileResponse(fallback, media_type="audio/mpeg", filename="remostar_voice.mp3")
        log_mostar_moment("System", "Voice", f"TTS failed: {e}", "error", 0.2)
        return JSONResponse(content={"error": str(e)}, status_code=500)


# === Moment logging endpoint ===
@app.post("/api/v1/moment")
async def moment_log(request: Request):
    body = await request.json()
    initiator = body.get("initiator", "unknown")
    receiver = body.get("receiver", "unknown")
    desc = body.get("description", "unspecified event")
    trig = body.get("trigger_type", "manual")
    res = float(body.get("resonance_score", 1.0))
    qid = log_mostar_moment(initiator, receiver, desc, trig, res)
    return {"quantum_id": qid, "status": "recorded"}


# === Root ping ===
@app.get("/")
async def root():
    return {"message": "🧩 MoStar Grid API online — unified reason, voice & memory."}
