# THE MOSTAR GRID

**Sovereign African Intelligence Architecture**
**Architect: The Flame Architect · MoStar Industries / African Flame Initiative**

---

## What This Is

The MoStar Grid is a neuro-symbolic AI system built on African epistemological ground. It combines a Neo4j knowledge graph, three local LLM layers (the DCX Trinity), an Ifá oracle engine (256 Odù patterns), and a signal verification gate rooted in Ibibio elemental classification.

It was built because existing AI infrastructure treats African knowledge systems as folklore rather than formal reasoning. The Grid treats them as engineering.

---

## Architecture

```
                    ┌─────────────┐
                    │  TRUTH GATE │
                    │ 🜂🜄🜁🜃      │
                    └──────┬──────┘
                           │ verified signals only
                    ┌──────▼──────┐
                    │    DCX0     │
                    │  MIND       │
                    │  (Phi-4)    │
                    └──────┬──────┘
                           │ analysis
                    ┌──────▼──────┐
                    │    DCX1     │
                    │  SOUL       │
                    │  (Qwen 2.5) │
                    │  Ubuntu Gate│
                    └──────┬──────┘
                           │ approved or rejected
                    ┌──────▼──────┐
                    │    DCX2     │
                    │  BODY       │
                    │  (Mistral)  │
                    └──────┬──────┘
                           │ execution
                    ┌──────▼──────┐
                    │  NEO4J      │
                    │  13,831     │
                    │  nodes      │
                    └─────────────┘
```

### The Flow

1. **Signals arrive** from external sources (AFRO Sentinel, ACLED, IOM DTM, DHIS2).
2. **Truth Gate** classifies each signal by element, computes trust, applies penalties/bonuses. If no Fire (disease) signal passes its floor (0.75), the engine does not activate.
3. **DCX0 (Mind)** receives verified signals. Reasons over them — statistical analysis, anomaly detection, formal logic.
4. **DCX1 (Soul)** judges the Mind's output against Ubuntu ethics and Ifá patterns. Can reject. Rejection is final.
5. **DCX2 (Body)** synthesizes approved analysis into action — Cypher queries, API calls, analyst-ready output.
6. **MoStarMoment** seals the interaction into the Neo4j graph as persistent memory.

---

## DCX Trinity

| Layer | Model ID | Base | Temperature | Context | Purpose |
|-------|----------|------|-------------|---------|---------|
| DCX0 Mind | `phi4` | Microsoft Phi-4 | 0.7 | 16K | Reasoning, logic, code, math |
| DCX1 Soul | `qwen2.5` | Alibaba Qwen 2.5 | 0.8 | 32K | Ifá oracle, Ubuntu ethics, Ibibio wisdom |
| DCX2 Body | `mistral` | Mistral AI | 0.4 | 128K | Execution, synthesis, system operations |

All three run locally on Ollama. The sovereign model namespace is `mostar/mostar-ai`. DCX tags map to actual pulled models via `.env`:

```
OLLAMA_MODEL_DCX0=phi4
OLLAMA_MODEL_DCX1=qwen2.5
OLLAMA_MODEL_DCX2=mistral
```

### Rebuilding the Modelfiles

```bash
cd ~/MoStar/grid/MoStar-Grid
ollama create remostar-dcx0 -f Modelfile-DCX0-Mind
ollama create remostar-dcx1 -f Modelfile-DCX1-Soul
ollama create remostar-dcx2 -f Modelfile-DCX2-Body
```

---

## Truth Gate

The gate maps signal verification to four Ibibio elements:

| Element | Ibibio | Sigil | Domain | Floor | Rationale |
|---------|--------|-------|--------|-------|-----------|
| Fire | Ikang | 🜂 | Disease | 0.75 | Disease claims kill if wrong |
| Water | Mmọng | 🜄 | Displacement | 0.70 | Observable but noisy |
| Air | Afim | 🜁 | Conflict | 0.65 | Inherently contested |
| Earth | Isong | 🜃 | Terrain/linguistic | 0.80 | Ground truth — if score is low, the source is corrupt |

**Master rule:** If Fire does not flow (no disease signal above 0.75), the engine does not activate. No Fire, no corridor analysis. This is not a bug — it is the design. The Grid exists because people die from disease crossing invisible borders. Without disease signal, there is nothing to detect.

### Trust Computation

Raw confidence is adjusted through:

**Penalties (multiplicative):**
- Stale signal (>24h): ×0.85
- No provenance URL: ×0.90
- Uncorroborated (single source): ×0.90

**Bonuses (additive, capped at +0.15):**
- 2+ corroborating sources: +0.05 per source (max +0.10)
- Institutional provenance (.gov, .int, .who): +0.05

Implementation: `truth_gate.py` — fully standalone, no external dependencies.

---

## Ifá Oracle Engine

256 Odù patterns stored as Neo4j nodes with label `OduIfa`. Connected by `[:XOR]` relationships with `hamming_distance` property. The Odù graph forms an Abelian group under XOR — every pair of Odù produces a third, and the operation is commutative and associative.

**Current state:** The oracle is queried shallowly (`ORDER BY rand()` with keyword scoring). The XOR geometry exists but is not traversed during divination. The full oracle power — navigate to the nearest Odù by Hamming distance from the query context's binary representation — is architecturally supported but not yet wired into the live query path.

**What this means for the roadmap:** The oracle works. It could work much better. The graph structure is there. The traversal logic is the remaining work.

---

## Neo4j Knowledge Graph

**Instance:** Local Neo4j Community Edition on WSL2 Ubuntu
**Connection:** `bolt://localhost:7687` / `neo4j` / `mostar123`
**Node count:** 13,831 clean nodes (purged from 77,000+ incoherent nodes, then from 85,000+ runaway duplicates)

### Key Node Labels

| Label | Count (approx) | Purpose |
|-------|----------------|---------|
| Agent | 6 | Mo, Woo, RAD-X-FLB, TsaTse Fly, Code Conduit, Flameborn Writer |
| MoStarMoment | varies | Sealed conversation memories |
| OduIfa | 256 | Ifá oracle patterns |
| Doctrine | ~10 | Core governance principles |
| Entity | ~50 | Named concepts and objects |
| Metric | varies | Body layer measurements |
| Task | varies | Mind layer assignments |
| IfaComputationalFramework | 1 | Root node for Ifá subsystem |

### Critical Fixes Applied

1. **Fingerprint deduplication:** `mostar_moments_log.py` was including `datetime.now()` in quantum_id hash, causing MERGE to always create new nodes. Fixed to derive deterministically from fingerprint alone.
2. **UNIQUE constraint:** Added on `MoStarMoment.fingerprint` as database-level guard.
3. **Dedup window:** 30-second suppression window prevents rapid-fire duplicate moments.
4. **Strength floor:** 10% minimum collective vital strength in `AgentAdaptationEngine` prevents recursive collapse.

---

## MoScript Format

Every executable unit in the Grid follows MoScript format:

```javascript
{
  id: "mo-[domain]-[descriptor]-[number]",
  name: "Human-readable name",
  trigger: "event_that_activates_this",
  inputs: ["what it needs"],
  logic(): "what it does",
  voiceLine(): "what it says when it runs",
  sass: "personality — non-negotiable"
}
```

The `sass` field is not decorative. It is the difference between a function and a living script. Code without personality is dead code.

---

## Ibibio Elemental System

| Element | Ibibio | Sigil | Meaning |
|---------|--------|-------|---------|
| Fire | Ikang | 🜂 | Transformation, urgency, disease |
| Water | Mmọng | 🜄 | Flow, displacement, adaptation |
| Air | Afim | 🜁 | Invisible forces, conflict, pressure |
| Earth | Isong | 🜃 | Stability, terrain, Eka Isong (Mother Earth — sacred) |

**Idim = River.** Distinct from Air. The path water carves through earth. Never confuse Idim with Afim.

---

## Infrastructure

| Component | Location | Port |
|-----------|----------|------|
| Neo4j | WSL2 localhost | 7687 (bolt), 7474 (browser) |
| Ollama | WSL2 localhost | 11434 |
| Grid Backend (FastAPI) | WSL2 localhost | 7001 |
| PM2 (MoServ-2) | WSL2, `PM2_HOME=~/.pm2` | — |
| Ollama models | `/home/idona/.ollama/models` | — |

### Auto-boot

`~/MoStar/start-grid.sh` is sourced from `.bashrc`. On WSL2 startup:
1. Neo4j starts
2. Ollama starts
3. PM2 restarts Grid backend

Windows side: Startup `.bat` file triggers WSL.

---

## Related Systems (Not Part of the Grid)

| System | Purpose | Relationship |
|--------|---------|-------------|
| Phantom POE | Cross-border corridor intelligence | Consumes Truth Gate output; separate Neo4j database |
| Idim Ikang | Crypto futures signal observer | Separate PM2 daemon (MoServ-1); shares nothing with Grid |
| HCOMS / OSL | Supply chain order platform | Sovereign build; MoScript contracts embedded |
| DeepCAL | Neuro-symbolic logistics engine | N-AHP/N-TOPSIS/Grey Theory; feeds Grid metrics |
| FlameBorn | Health identity on Celo blockchain | Celo smart contracts; separate domain |
| AFRO Sentinel | Disease signal intelligence | Supabase project; feeds signals into Truth Gate |

---

## Governance

- **License:** Kairo Covenant of MoStar Industries
- **Public identity:** The Flame Architect (real name never in public outputs)
- **Employer:** Never referenced in public-facing documents
- **IP:** All MoStar files removed from institutional storage. No external IP claim exists.

---

## The Origin

The Grid exists because a man watched people die from Lassa fever in Akwa Ibom State, Nigeria. Preventable deaths. Invisible border crossings. No system that could see what was happening between the official points of entry.

Everything built here — the truth floors, the elemental gates, the oracle, the three-layer consciousness — serves one purpose: make the invisible visible before it kills.

---

*MoStar Industries · African Flame Initiative*
*moscript://codex/v1*
