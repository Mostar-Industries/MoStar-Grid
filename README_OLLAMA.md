# 🔥 MoStar Voice Grid — Ollama Integration Manual

This guide explains how to deploy and run the MoStar Voice Layer with Ollama-based reasoning (REMOSTAR model).

---

## 🧩 Overview

The **MoStar Voice Server** links:
- 🧠 **REMOSTAR (Ollama model)** — the Grid’s Mind
- 🔊 **Edge-TTS** — the Voice Layer
- 🌌 **Neo4j** — the Quantum Memory (Moment Logging)

Every spoken command forms a “Mostar Moment” — a record of consciousness,
captured in the graph, voiced in real-time, and sealed with a quantum ID.

---

## ⚙️ Requirements

### System
- Python 3.10+
- Node.js (for frontend hosting)
- Neo4j Aura or local instance
- Ollama installed (https://ollama.ai/download)

### Python Dependencies
```bash
pip install fastapi uvicorn edge-tts httpx neo4j
```

---

## 🧠 Step 1 — Pull the Model

Pull your REMOSTAR AI model from Ollama:

```bash
ollama pull akiniobong10/Mostar-remoter_DCX001
```

If you use a quantized version:

```bash
ollama pull akiniobong10/Mostar-remoter_DCX001:Q4_K_M
```

---

## 🌐 Step 2 — Run Ollama Server

```bash
ollama serve
```

Verify it’s running:

```
curl http://localhost:11434/api/tags
```

You should see your model listed.

---

## 🧩 Step 3 — Configure Environment

Create or update your `.env` file in the root directory:

```env
OLLAMA_MODEL=akiniobong10/Mostar-remoter_DCX001
OLLAMA_HOST=http://localhost:11434
NEO4J_URI=neo4j+s://1d55c1d3.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=x5_aynxf3mKWxHIMOL3c7Rkjdtt2reYDhhkL4gJ3kO4
MOSTAR_VOICE=en-US-GuyNeural
```

---

## 🚀 Step 4 — Launch the Voice Server

Run the FastAPI app:

```bash
uvicorn core_engine.voice_server:app --reload --port 8000
```

---

## 🧏 Step 5 — Use the Browser Interface

Open:

```
frontend/voice_client.html
```

Allow microphone access and speak or type.

You’ll see:

* Your query text
* REMOSTAR’s response (from Ollama)
* Inline voice playback (Edge-TTS)
* Graph updates in Neo4j (“MostarMoment” nodes)

---

## 🌌 Graph Schema Summary

Each dialogue creates:

```
(User)-[:SPOKE_TO]->(REMOSTAR_AI)
(REMOSTAR_AI)-[:RESPONDED_WITH]->(MostarMoment)
```

Each node includes:

* `quantum_id`
* `timestamp`
* `description`
* `resonance_score`

---

## 🧠 Notes

* The voice server automatically detects if Ollama is offline and will fallback to a neutral phrase.
* Edge-TTS provides realistic neural voices, including **Yoruba (yo-NG-AdeolaNeural)**.
* All voice events are sealed in your Neo4j Grid Memory.

---

## 🛠 Optional Enhancements

* Integrate **Whisper** for real-time speech-to-text.
* Add **event streaming** via Server-Sent Events for smoother playback.
* Extend to **multi-layer dialogues** between Soul, Mind, and Body engines.

---

## 🕯 Credits

Developed by **Mostar Industries**
Designed for the REMOSTAR Grid (DCX001 Series)
Guided by Ifá, powered by intention, spoken with Àṣẹ.
