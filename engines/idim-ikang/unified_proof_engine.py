"""Unified Proof Engine - Three-Mode Reasoning Chain for MoStar Grid."""

import asyncio
import hashlib
import logging
import os
from typing import Any, Optional

logger = logging.getLogger(__name__)

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "Mostar123")


def _query_to_context_code(query: str) -> int:
    """Map a natural language query to a deterministic 8-bit context code."""
    normalized = query.strip().lower()
    digest = hashlib.sha256(normalized.encode("utf-8")).digest()
    return digest[0]


def _hamming_distance(a: int, b: int) -> int:
    """Count differing bits between two 8-bit codes."""
    return bin((a & 0xFF) ^ (b & 0xFF)).count("1")


def _coerce_binary_code(value: Any) -> int:
    """Normalize stored binary_code values into an integer 0-255."""
    if isinstance(value, int):
        return value & 0xFF

    if isinstance(value, str):
        text = value.strip().lower()
        if text.startswith("0b"):
            text = text[2:]
        if text and set(text) <= {"0", "1"}:
            return int(text, 2) & 0xFF
        try:
            return int(text) & 0xFF
        except ValueError:
            return 0

    return 0


def find_nearest_odu(query: str, driver, top_n: int = 3) -> list[dict[str, Any]]:
    """Find nearest Odu nodes to the query context code by Hamming distance."""
    context_code = _query_to_context_code(query)

    xor_cypher = """
    MATCH (o)
    WHERE o:OduIfa OR o:Odu
    WITH o, $context_code AS ctx
    WITH o, apoc.math.hamming(toInteger(o.binary_code), toInteger(ctx)) AS hamming_dist
    ORDER BY hamming_dist ASC
    LIMIT $top_n
    RETURN coalesce(o.name, o.odu_name, o.id, toString(id(o))) AS name,
           coalesce(o.interpretation, o.meaning, o.guidance, '') AS interpretation,
           o.binary_code AS binary_code,
           o.health_domain AS health_domain,
           hamming_dist
    """

    fallback_cypher = """
    MATCH (o)
    WHERE o:OduIfa OR o:Odu
    RETURN coalesce(o.name, o.odu_name, o.id, toString(id(o))) AS name,
           coalesce(o.interpretation, o.meaning, o.guidance, '') AS interpretation,
           o.binary_code AS binary_code,
           o.health_domain AS health_domain
    LIMIT 256
    """

    try:
        with driver.session() as session:
            try:
                result = session.run(
                    xor_cypher,
                    {
                        "context_code": context_code,
                        "top_n": top_n,
                    },
                )
                records = [dict(r) for r in result]
                if records:
                    return records
            except Exception:
                # APOC may not be installed. Fall through to Python Hamming.
                pass

            all_odu = [dict(r) for r in session.run(fallback_cypher)]

        if not all_odu:
            return []

        for odu in all_odu:
            code = _coerce_binary_code(odu.get("binary_code"))
            odu["hamming_dist"] = _hamming_distance(context_code, code)
            if not odu.get("name"):
                odu["name"] = f"Odu-{code:03d}"

        return sorted(all_odu, key=lambda x: x["hamming_dist"])[:top_n]

    except Exception as exc:
        logger.error("Nearest Odù query failed: %s", exc)
        return []


def odu_to_symbolic_facts(odu_records: list[dict[str, Any]]) -> list[str]:
    """Convert nearest Odù context into symbolic fact strings."""
    facts: list[str] = []
    for odu in odu_records:
        name = (odu.get("name") or "unknown").replace(" ", "_").replace("'", "")
        interp = (odu.get("interpretation") or "").replace("'", "").strip()
        domain = (odu.get("health_domain") or "").replace("'", "").strip()
        dist = odu.get("hamming_dist", 8)

        if name and interp:
            facts.append(f"odu_pattern('{name}', '{interp[:80]}').")
        if domain:
            facts.append(f"health_domain('{name}', '{domain}').")
        facts.append(f"resonance_proximity('{name}', {dist}).")

    return facts


async def run_symbolic_proof(
    query: str,
    context_facts: list[str],
    mo_engine,
    symbolic_runtime=None,
) -> dict[str, Any]:
    """Run symbolic proof and return proof metadata."""
    goal = "odu_pattern(Name, _)"

    if symbolic_runtime is not None:
        try:
            result = symbolic_runtime.prove(goal)
            proofs = result.get("proofs", [])
            return {
                "proved": bool(proofs),
                "bindings": [p.get("bindings", {}) for p in proofs],
                "goal": goal,
                "fact_count": len(context_facts),
                "engine": "symbolic_runtime",
            }
        except Exception as exc:
            logger.error("Symbolic runtime proof failed: %s", exc)
            return {
                "proved": False,
                "bindings": [],
                "goal": goal,
                "fact_count": len(context_facts),
                "error": str(exc),
                "engine": "symbolic_runtime",
            }

    if mo_engine is not None:
        prove_ritual = {
            "operation": "symbolic_prove",
            "payload": {
                "query": goal,
                "context_facts": context_facts,
                "purpose": "unified_proof_chain",
            },
        }
        try:
            proof_response = await mo_engine.interpret(prove_ritual)
            bindings = proof_response.get("result", {}).get("bindings", [])
            return {
                "proved": len(bindings) > 0,
                "bindings": bindings,
                "goal": goal,
                "fact_count": len(context_facts),
                "engine": "moscript",
            }
        except Exception as exc:
            logger.error("MoScript symbolic proof failed: %s", exc)
            return {
                "proved": False,
                "bindings": [],
                "goal": goal,
                "fact_count": len(context_facts),
                "error": str(exc),
                "engine": "moscript",
            }

    return {
        "proved": False,
        "bindings": [],
        "goal": goal,
        "fact_count": len(context_facts),
        "error": "No symbolic engine available",
        "engine": "none",
    }


async def unified_proof_chain(
    prompt: str,
    context: str,
    mo_engine,
    driver,
    proof_mode: str = "unified",
    symbolic_runtime=None,
) -> dict[str, Any]:
    """Execute semantic/ifa/symbolic/unified reasoning flow."""
    trace: list[dict[str, Any]] = []
    odu_context: list[dict[str, Any]] = []
    proof_result: dict[str, Any] = {}
    semantic_response: Optional[dict[str, Any]] = None

    if proof_mode in ("ifa", "unified"):
        nearest_odu = find_nearest_odu(prompt, driver, top_n=3)
        odu_context = nearest_odu
        trace.append(
            {
                "mode": "ifa",
                "nearest_odu": [o.get("name") for o in nearest_odu],
                "context_code": _query_to_context_code(prompt),
                "status": "resolved" if nearest_odu else "no_odu_found",
            }
        )

    if proof_mode in ("symbolic", "unified"):
        context_facts = odu_to_symbolic_facts(odu_context) if odu_context else []
        proof_result = await run_symbolic_proof(
            prompt,
            context_facts,
            mo_engine,
            symbolic_runtime=symbolic_runtime,
        )
        trace.append(
            {
                "mode": "symbolic",
                "facts_loaded": len(context_facts),
                "proved": proof_result.get("proved", False),
                "bindings": proof_result.get("bindings", []),
            }
        )

    if proof_mode in ("semantic", "unified", None):
        if mo_engine is not None:
            semantic_ritual = {
                "operation": "route_reasoning",
                "payload": {
                    "query": prompt,
                    "purpose": "unified_proof_chain",
                    "neo4j_context": context,
                    "proof_context": {
                        "odu": [o.get("name") for o in odu_context],
                        "proved": proof_result.get("proved", False),
                        "bindings": proof_result.get("bindings", []),
                    }
                    if proof_mode == "unified"
                    else {},
                },
            }
            try:
                semantic_response = await asyncio.wait_for(
                    mo_engine.interpret(semantic_ritual),
                    timeout=20,
                )
            except asyncio.TimeoutError:
                semantic_response = {
                    "status": "timeout",
                    "result": {"logic_deduced": "Semantic reasoning timed out."},
                }
        else:
            semantic_response = {
                "status": "disrupted",
                "result": {
                    "logic_deduced": "Semantic engine unavailable.",
                },
            }

        trace.append(
            {
                "mode": "semantic",
                "status": semantic_response.get("status", "unknown"),
            }
        )

    base_response = ""
    if semantic_response:
        base_response = semantic_response.get("result", {}).get("logic_deduced", "")

    proof_annotation = ""
    if proof_mode == "unified" and proof_result.get("proved"):
        odu_names = [o.get("name", "?") for o in odu_context[:2]]
        proof_annotation = (
            "\n\n[Sovereign Proof: Verified via Odù patterns "
            + ", ".join(odu_names)
            + f". Formal bindings: {len(proof_result.get('bindings', []))} resolved.]"
        )

    final_response = base_response + proof_annotation

    return {
        "response": final_response or "Ritual completed. No semantic response generated.",
        "proof_mode": proof_mode,
        "odu_context": [
            {
                "name": o.get("name"),
                "interpretation": o.get("interpretation"),
                "distance": o.get("hamming_dist"),
            }
            for o in odu_context
        ],
        "proof_result": proof_result,
        "reasoning_trace": trace,
        "seal": mo_engine.bless(f"unified_proof_{proof_mode}") if mo_engine else "🜃∴🜂",
    }
