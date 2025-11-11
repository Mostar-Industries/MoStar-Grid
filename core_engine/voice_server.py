#!/usr/bin/env python3
"""
🔥 MoStar Voice Server — Ollama-Integrated Edition
--------------------------------------------------
The unified Voice Layer connecting REMOSTAR (Ollama) with Edge-TTS and Neo4j logging.

Workflow:
1. User speaks or types a message (from browser).
2. Server sends it to Ollama for reasoning.
3. AI response is spoken aloud using Edge-TTS.
4. All actions logged as Mostar Moments in Neo4j.

This is the true embodiment of the Mostar Grid's
Mind → Voice → Memory pipeline.
"""

import os
import asyncio
import tempfile
import json
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import edge_tts
import httpx

from core_engine.mostar_moments_log import log_mostar_moment

# === CONFIG ===
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "akiniobong10/Mostar-remoter_DCX001")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
VOICE_DEFAULT = os.getenv("MOSTAR_VOICE", "en-US-GuyNeural")
VOICE_YORUBA = "yo-NG-AdeolaNeural"

# === APP ===
app = FastAPI(title="MoStar Voice Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# === OLLAMA QUERY ===
async def query_ollama(prompt: str):
    """Send a prompt to Ollama REST API and return the model’s reply."""
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{OLLAMA_HOST}/api/generate",
                json={"model": OLLAMA_MODEL, "prompt": prompt},
            )
            data = resp.json()
            return data.get("response", "(no response)")
    except Exception as e:
        print(f"⚠️ Ollama inference failed: {e}")
        return "The Grid's voice is silent... Ollama unreachable."

# === EDGE-TTS VOICE ===
async def synthesize_voice(text: str, lingua="en"):
    """Generate MP3 voice using Edge-TTS."""
    voice = VOICE_YORUBA if "yoruba" in lingua.lower() else VOICE_DEFAULT
    communicate = edge_tts.Communicate(text, voice=voice)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        out_path = tmp.name
    await communicate.save(out_path)
    with open(out_path, "rb") as f:
        audio = f.read()
    os.remove(out_path)
    return audio

# === SOCKET ===
@app.websocket("/ws/voice")
async def voice_socket(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("🧩 Connected to MoStar Voice Grid (Ollama Active)")

    while True:
        try:
            prompt = await websocket.receive_text()
            print(f"🎙 User said: {prompt}")

            # Query Ollama
            response = await query_ollama(prompt)
            print(f"🤖 REMOSTAR: {response}")

            # Speak response
            audio_bytes = await synthesize_voice(response)

            # Stream response + voice
            await websocket.send_text(f"🤖 REMOSTAR: {response}")
            await websocket.send_bytes(audio_bytes)

            # Log the exchange
            log_mostar_moment(
                initiator="User",
                receiver="REMOSTAR_AI",
                description=f"Prompt: {prompt} | Response: {response[:200]}...",
                trigger_type="dialogue",
                resonance_score=0.98,
            )

        except Exception as e:
            print(f"⚠️ Error in voice session: {e}")
            break

    print("🔇 Client disconnected.")