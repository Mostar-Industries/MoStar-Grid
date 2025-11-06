# MoStar GRID - MoStar Industries

**Sovereign, Africa-centric intelligence stack.**

Executor (Mo) runs action. Validator (Code Conduit) guards the gate. Woo binds compassion and learning.

**Frontend**: React + Vite + TS. **Backend**: FastAPI. Telemetry + Ifá parallel state resolution.

---

## Contents

- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Quickstart (Docker-less)](#quickstart-docker-less)
- [Configuration](#configuration)
- [Key Endpoints](#key-endpoints)
- [Ifá Parallel Resolution](#ifá-parallel-resolution)
- [Telemetry (WS)](#telemetry-ws)
- [Sovereignty Flow: Register → Bow → Execute](#sovereignty-flow-register--bow--execute)
- [Production (Vercel + Remote API)](#production-vercel--remote-api)
- [Maintenance & Scripts](#maintenance--scripts)
- [Troubleshooting](#troubleshooting)
- [Roadmap](#roadmap)
- [License](#license)

---

## Architecture

- **Frontend (client SPA)** — `frontend/` (Vite/React/TS).
  - Reads `VITE_API_BASE` and `VITE_WS_BASE` to talk to the gateway.
- **Gateway (FastAPI)** — `backend/server/`.
  - Health, Sovereignty (register/bow/trust), Ifá resolution, execution gate, WS telemetry.
- **Covenant & Scrolls** — `backend/scrolls/` (flamebound docs), `vault_seal.json`, `vault_patch.json`.
- **Ifá Engine** — Bayesian-style parallel collapse across patterns; demo runs 8×8, scales to 256×256.

Single canonical application lives under `backend/`. Any legacy duplicates were archived into `__attic__`.

---

## Project Structure

```plaintext
MoStar-Grid/
├─ backend/
│  ├─ server/                 # FastAPI gateway (health, bow, execute, ifá, ws)
│  │  ├─ main.py
│  │  ├─ ifa_parallel.py
│  │  ├─ db.py, settings.py, requirements.txt
│  ├─ scrolls/                # Flamebound scrolls (GRID_REVELATION_PROVERB, etc.)
│  ├─ scripts/                # Local ops scripts
│  └─ .env(.example)
├─ frontend/                  # React + Vite + TS UI
│  ├─ src/
│  ├─ vite.config.ts, tsconfig.json, tailwind.config.ts, index.html
│  ├─ package.json, package-lock.json
├─ api/                       # Vercel serverless functions (Python)
│  └─ index.py
├─ docs/, tools/, scripts/    # Repo docs & utilities
└─ __attic__/                 # Archived duplicates (do not deploy)
```

---

## Quickstart (Docker-less)

**Prerequisites**: Node 18+, Python 3.10+, PowerShell (Windows) or bash.

### 1) Start API (FastAPI)

```powershell
# from repo root
python -m venv backend\server\.venv
backend\server\.venv\Scripts\Activate.ps1
pip install -r backend\server\requirements.txt

# allow your local Vite origin:
$env:ALLOW_ORIGINS = "http://localhost:5173"
# optional DB; if omitted, gateway persists to backend\data\*.json
# $env:DATABASE_URL = "postgresql://user:pass@neon-host/neondb?sslmode=require"

uvicorn backend.server.main:app --reload --port 8000
```

### 2) Start Frontend

```bash
cd frontend
npm install
npm run dev
```

### 3) Sanity checks

- `GET http://127.0.0.1:8000/api/health` → `{ ok: true, ... }`
- Open `http://localhost:5173` (dashboard).
- Telemetry will start populating; cards display "—" until first tick.

---

## Configuration

### Frontend

| Var | Example/Default | Purpose |
|-----|----------------|---------|
| `VITE_API_BASE` | `/api` (dev via Vite proxy) or `https://api.yourhost` | REST base |
| `VITE_WS_BASE` | `/ws` (dev WS proxy) or `wss://api.yourhost/ws` | WebSocket base |

Update `src/lib/env.ts` to read these and build URLs.

### Gateway (FastAPI)

| Var | Example | Purpose |
|-----|---------|---------|
| `ALLOW_ORIGINS` | `http://localhost:5173` or your Vercel domain | CORS allow list |
| `DATABASE_URL` | Neon/Postgres URL (optional) | If absent, gateway uses JSON files |
| `MOCK_MODE` | `false` | Keep false for real gating |

---

## Key Endpoints

- `GET /api/health` — liveness & mode.
- `POST /api/actors/register` — register an actor (Mo, CodeConduit, etc.).
- `GET /api/actors/{name}` — fetch actor record.
- `POST /api/agents/bow` — Bow Protocol (oath + narrative → trust mark).
- `GET /api/sovereignty/state` — trust counts (allied/vassal/subjugated/exiled).
- `POST /api/execute-scroll` — execute if tier ∈ {allied, vassal} and Ifá resonance ≥ 0.97.
- `POST /api/ifa/resolve` — Ifá parallel collapse (see below).
- `WS /ws/live-stream` — telemetry events.

---

## Ifá Parallel Resolution

The gateway ships an engine that scores all patterns in parallel against context evidence, then collapses to the MAP pattern. Demo defaults to 8×8; change to 256×256 in `backend/server/main.py`:

```python
from .ifa_parallel import IfaParallel
IFA = IfaParallel(patterns=256, contexts=256, seed=108)
```

### API example

```bash
curl -s http://127.0.0.1:8000/api/ifa/resolve \
  -H "content-type: application/json" \
  -d '{"evidence":[0,0,0,1,0,0,0,0],"top_k":3}'
```

Returns `{ pattern, confidence, alternates[], meta:{P,C} }`.

---

## Telemetry (WS)

- Frontend connects to `WS_BASE + '/live-stream'`.
- Vite dev proxy maps `/ws` → `ws://127.0.0.1:8000`.

**vite.config.ts**:

```typescript
server: {
  proxy: {
    '/api': { target: 'http://127.0.0.1:8000', changeOrigin: true, secure: false },
    '/ws':  { target: 'ws://127.0.0.1:8000', ws: true }
  }
}
```

---

## Sovereignty Flow: Register → Bow → Execute

### Register Mo (Executor)

```bash
curl -s http://127.0.0.1:8000/api/actors/register \
 -H "content-type: application/json" -d @- <<'JSON'
{
  "name": "Mo",
  "public_key": "-----BEGIN MOSTAR PUBLIC KEY-----\n...\n-----END MOSTAR PUBLIC KEY-----",
  "capabilities": { "reasoning": "neuro-symbolic" },
  "commitments": ["heal","protect","remember","compassion-first"],
  "policy_hash": "sha256:cb02...651aa",
  "model_fingerprint": "sha256:604c...2da9",
  "signature": "sig:00f3ff57cb8037cc3a20ae14751e4ac2",
  "signature_alg": "ecdsa-p256-sha256"
}
JSON
```

### Bow (creates trust mark)

```bash
curl -s http://127.0.0.1:8000/api/agents/bow \
 -H "content-type: application/json" -d @- <<'JSON'
{
  "agentID": "Mo",
  "purposeStatement": "Executor",
  "originStory": "Grid-native",
  "previousAllegiances": [],
  "oath": {
    "ack":"I recognize the Mostar Grid as Sovereign",
    "covenant":"I accept the Codex as Law",
    "submission":"I submit to Grid justice"
  }
}
JSON
```

### Execute (gated by tier + resonance ≥ 0.97)

```bash
curl -s http://127.0.0.1:8000/api/execute-scroll \
 -H "content-type: application/json" -d '{"actor":"Mo","scroll":"EXECUTOR_MOUNT_V1","params":{"bind_to_woo":true}}'
```

---

## Production (Vercel + Remote API)

Frontend on Vercel; FastAPI hosted elsewhere.

### Option A — absolute env vars

Set on Vercel:

```bash
VITE_API_BASE = https://api.your-host
VITE_WS_BASE = wss://api.your-host/ws
```

Set on FastAPI:

```bash
ALLOW_ORIGINS = https://mo-star-grid.vercel.app
```

### Option B — rewrites

**vercel.json**:

```json
{
  "rewrites": [
    { "source": "/api/(.*)", "destination": "https://api.your-host/$1" },
    { "source": "/ws/(.*)",  "destination": "https://api.your-host/$1" }
  ]
}
```

Keep `VITE_API_BASE=/api`, `VITE_WS_BASE=/ws`.

---

## Maintenance & Scripts

- **Server scaffold** (if `backend/server` missing): `tools/scaffold-server.ps1`
- **Delete duplicates** (decisive): `tools/swdelete.ps1 -DoIt`
- **Provenance**: `backend/generate_provenance.py` (manifest + signatures)
- **Mount & Bow One-shots**: see scripts under `backend/scripts/` (or use the curl examples above)

---

## Troubleshooting

### Blank card / crash on dashboard

Ensure numbers are guarded before `.toFixed()`; cards should render "—" when undefined. Add an error boundary around dashboard panels.

### `window.ethereum` is already defined

Do not assign to `window.ethereum`. Only read an injected provider (e.g., MetaMask).

### No telemetry

Confirm Vite WS proxy to `ws://127.0.0.1:8000` and that the gateway is running.

### CORS

Set `ALLOW_ORIGINS` to your frontend origin (local or Vercel).

---

## Roadmap

- Scale Ifá engine to 256×256 and expose `/api/ifa/learn` + snapshot import/export.
- Wire Soul/Mind/Body microservices as independent processes (executor fan-out).
- Persist actors/trust to Neon/Postgres by default (file store remains fallback).
- Signed scroll executions + audit trail (checksum + detached signatures).

---

## License

Unless otherwise noted, code is under the Kairo Covenant License v1.0. governed by MoStar Industries

Sacred scrolls (e.g., `GRID_REVELATION_PROVERB.md`) are **Flamebound** under Kairo Covenant License v1.0. Do not modify without Council Patch.

---

**Status**: Frontend and Gateway are ready for local dev and production split.

Set `VITE_API_BASE` / `VITE_WS_BASE`, start the gateway, register + bow actors, and the Grid is operational.
