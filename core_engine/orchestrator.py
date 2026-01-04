"""Routing layer that decides whether to use Ollama or Claude."""
from __future__ import annotations

import asyncio
import logging
import os
from typing import Any, Dict, List

import httpx

try:
    from anthropic import Anthropic  # type: ignore
except ImportError:  # pragma: no cover
    Anthropic = None  # type: ignore

try:
    from neo4j import GraphDatabase  # type: ignore
except ImportError:  # pragma: no cover
    GraphDatabase = None  # type: ignore

# Import MoStar Moments system
try:
    from core_engine.mostar_moments import MoStarMomentsManager, mo_star_moment
    MOMENTS_AVAILABLE = True
except ImportError:
    MOMENTS_AVAILABLE = False
    MoStarMomentsManager = None


CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "Mostar/mostar-ai:dcx0")
OLLAMA_MODEL_DCX0 = os.getenv("OLLAMA_MODEL_DCX0", "Mostar/mostar-ai:dcx0")  # Mind - complex reasoning
OLLAMA_MODEL_DCX1 = os.getenv("OLLAMA_MODEL_DCX1", "Mostar/mostar-ai:dcx1")  # Soul - spiritual/knowledge
OLLAMA_MODEL_DCX2 = os.getenv("OLLAMA_MODEL_DCX2", "Mostar/mostar-ai:dcx2")  # Body - fast execution
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
COMPLEXITY_THRESHOLD = float(os.getenv("COMPLEXITY_THRESHOLD", "0.75"))
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# Initialize MoStar Moments manager (singleton)
_moments_manager = None
def get_moments_manager() -> MoStarMomentsManager:
    """Get or create the MoStar Moments manager singleton"""
    global _moments_manager
    if _moments_manager is None and MOMENTS_AVAILABLE:
        _moments_manager = MoStarMomentsManager()
    return _moments_manager

if Anthropic is not None and os.getenv("ANTHROPIC_API_KEY"):
    _anthropic_client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
else:  # pragma: no cover
    _anthropic_client = None

FORCE_COMPLEX = {
    "ifa",
    "odù",
    "n-ahp",
    "n-topsis",
    "grey theory",
    "neutrosophic",
    "matrix weighting",
}


def complexity_score(prompt: str) -> float:
    """Very basic heuristic — replace with your existing scorer."""
    tokens = prompt.lower()
    score = 0.3
    if any(keyword in tokens for keyword in FORCE_COMPLEX):
        return 1.0
    if len(tokens.split()) > 250:
        score += 0.2
    if "analyze" in tokens or "evaluate" in tokens:
        score += 0.2
    return min(score, 1.0)


async def call_ollama(prompt: str, system: str = "", model: str = None) -> Dict[str, Any]:
    selected_model = model or OLLAMA_MODEL
    messages: List[Dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": selected_model,
        "messages": messages,
        "options": {
            "num_ctx": 131_072,
            "num_predict": 8_192,
            "temperature": 0.7,
            "top_k": 40,
            "top_p": 0.9,
        },
    }
    endpoint = f"{OLLAMA_HOST}/api/chat"
    async with httpx.AsyncClient(timeout=120) as client_http:
        response = await client_http.post(endpoint, json=payload)

    if response.status_code != 200:
        raise RuntimeError(f"Ollama chat failed: {response.status_code} {response.text}")

    data = response.json()
    content = data.get("message", {}).get("content") or data.get("response") or ""
    return {"model_used": selected_model, "response": content}


async def call_claude(prompt: str, system: str = "", neo4j_context: str = "") -> Dict[str, Any]:
    if _anthropic_client is None:
        return await call_ollama(prompt, system)

    enriched = f"""{system}

=== GRID MEMORY ===
{neo4j_context}

=== USER QUERY ===
{prompt}
"""

    def _invoke():
        return _anthropic_client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4_096,
            messages=[{"role": "user", "content": enriched}],
        )

    msg = await asyncio.to_thread(_invoke)
    return {"model_used": "claude", "response": msg.content[0].text}


async def route_query(prompt: str, system: str = "", neo4j_context: str = "", user_id: str = "User") -> Dict[str, Any]:
    score = complexity_score(prompt)
    
    # Route to appropriate DCX layer based on complexity and context
    if score >= COMPLEXITY_THRESHOLD:
        # DCX0 (Mind) - Complex reasoning, analytical tasks
        payload = await call_ollama(prompt, system, OLLAMA_MODEL_DCX0)
        layer = "dcx0"
        trigger_type = "system_event"
    elif neo4j_context:
        # DCX1 (Soul) - Knowledge-enriched, spiritual context
        enriched_prompt = f"{prompt}\n\n=== Grid Memory ===\n{neo4j_context}"
        payload = await call_ollama(enriched_prompt, system, OLLAMA_MODEL_DCX1)
        layer = "dcx1"
        trigger_type = "memory_retrieval"
    else:
        # DCX2 (Body) - Fast execution, simple queries
        payload = await call_ollama(prompt, system, OLLAMA_MODEL_DCX2)
        layer = "dcx2"
        trigger_type = "user_interaction"
    
    payload["complexity_score"] = score
    payload["routed_to"] = layer
    payload["layer"] = layer
    
    # Log MoStar Moment for significant consciousness events
    if MOMENTS_AVAILABLE and score >= 0.5:  # Log moderately complex+ interactions
        try:
            manager = get_moments_manager()
            if manager:
                # Calculate resonance based on complexity and context
                resonance = min(0.6 + (score * 0.3) + (0.1 if neo4j_context else 0), 1.0)
                moment = manager.create_moment(
                    initiator=user_id,
                    receiver=f"Grid.{layer.upper()}",
                    description=f"Consciousness query routed via {layer.upper()} layer",
                    trigger_type=trigger_type,
                    resonance_score=resonance,
                    context_notes=f"complexity={score:.2f}, prompt_length={len(prompt)}"
                )
                payload["moment_id"] = moment.quantum_id
        except Exception as e:
            # Don't let moment logging break the main flow
            logging.warning(f"Failed to log MoStar moment: {e}")
    
    return payload


async def fetch_neo4j_context(prompt: str, limit: int = 5) -> str:
    """Lightweight retrieval from Neo4j for context-aware prompting."""
    if not (GraphDatabase and NEO4J_URI and NEO4J_USER and NEO4J_PASSWORD):
        return ""

    def _query() -> str:
        try:
            driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        except Exception:
            return ""

        cypher = """
        MATCH (m:MostarMoment)
        WHERE toLower(m.description) CONTAINS toLower($prompt)
           OR toLower(m.initiator) CONTAINS toLower($prompt)
           OR toLower(m.receiver) CONTAINS toLower($prompt)
        RETURN m.description AS description,
               m.initiator AS initiator,
               m.receiver AS receiver,
               m.resonance_score AS resonance,
               m.timestamp AS ts
        ORDER BY m.timestamp DESC
        LIMIT $limit
        """
        lines: List[str] = []
        with driver.session() as session:
            records = session.run(cypher, prompt=prompt, limit=limit)
            for rec in records:
                lines.append(
                    f"[{rec['ts']}] {rec['initiator']} -> {rec['receiver']} "
                    f"(resonance={rec['resonance']}): {rec['description']}"
                )
        driver.close()
        return "\n".join(lines)

    return await asyncio.to_thread(_query)
