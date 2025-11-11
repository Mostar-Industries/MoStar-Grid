#!/usr/bin/env python3
"""
🧠 MoStar Unified API Gateway
-----------------------------
Integrates:
- Ollama reasoning
- Neo4j memory persistence
- gTTS voice synthesis
- Mostar Moment logging
"""

import os
from fastapi import FastAPI, Body
import httpx
from gtts import gTTS
from core_engine.mostar_moments_log import log_mostar_moment

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "akiniobong10/Mostar-remoter_DCX001")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
TTS_LANG = os.getenv("MOSTAR_TTS_LANG", "en")

app = FastAPI(title="MoStar Grid API v1")

# === Ollama Reasoning ===
@app.post("/api/v1/reason")
async def reason(prompt: str = Body(..., embed=True)):
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{OLLAMA_HOST}/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": prompt}
        )
        data = resp.json()
        reply = data.get("response", "(no response)")
    log_mostar_moment("User", "REMOSTAR", f"Reasoned: {prompt} → {reply[:100]}")
    return {"response": reply}

# === Voice Synthesis ===
@app.post("/api/v1/voice")
def voice(text: str = Body(..., embed=True)):
    try:
        tts = gTTS(text=text, lang=TTS_LANG)
        output_file = "data/voice_cache/tmp_voice.mp3"
        tts.save(output_file)
        log_mostar_moment("REMOSTAR", "VoiceLayer", f"Spoke: {text[:120]}")
        return {"message": "Voice synthesized", "file": output_file}
    except Exception as e:
        return {"error": str(e)}

# === Memory Logging ===
@app.post("/api/v1/moment")
def record_moment(payload: dict = Body(...)):
    try:
        qid = log_mostar_moment(
            payload.get("initiator", "system"),
            payload.get("receiver", "unknown"),
            payload.get("description", ""),
            payload.get("trigger_type", "system"),
            payload.get("resonance_score", 1.0)
        )
        return {"status": "recorded", "quantum_id": qid}
    except Exception as e:
        return {"error": str(e)}

# === System Health ===
@app.get("/api/v1/status")
def status():
    return {
        "system": "MoStar Grid API",
        "ollama_model": OLLAMA_MODEL,
        "tts_language": TTS_LANG,
        "neo4j": "connected" if os.getenv("NEO4J_URI") else "offline"
    }
