from __future__ import annotations

import hashlib
from typing import Any

GROWTH_CONSTRAINT_QUERIES = [
    "CREATE CONSTRAINT IF NOT EXISTS FOR (m:MoStarMoment) REQUIRE m.fingerprint IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (p:MomentPattern) REQUIRE p.key IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (p:TrustProfile) REQUIRE p.id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (r:LearningRule) REQUIRE r.id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (q:CuriosityQuery) REQUIRE q.id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (v:IntegrityViolation) REQUIRE v.id IS UNIQUE",
]

DEFAULT_GROWTH_BUDGETS = {
    "derive_links_candidates": 5000,
    "create_patterns_candidates": 500,
    "update_weights_candidates": 10000,
}


def _normalize_component(value: Any) -> str:
    return " ".join(str(value or "").strip().lower().split())


def build_moment_fingerprint(
    initiator: str,
    receiver: str,
    description: str,
    trigger_type: str,
    layer: str,
) -> str:
    base = "|".join(
        [
            _normalize_component(initiator),
            _normalize_component(receiver),
            _normalize_component(description),
            _normalize_component(trigger_type),
            _normalize_component(layer),
        ]
    )
    return hashlib.sha256(base.encode("utf-8", errors="ignore")).hexdigest()[:24]


def build_moment_quantum_id(fingerprint: str) -> str:
    return f"MSTR-{fingerprint[:16].upper()}"


def resolve_growth_budget(config: dict[str, Any], key: str, default: int) -> int:
    raw_value = config.get(key, default)
    try:
        budget = int(raw_value)
    except (TypeError, ValueError):
        budget = default
    return max(budget, 0)


def enforce_growth_budget(candidate_count: int, max_allowed: int, label: str) -> None:
    if candidate_count > max_allowed:
        raise ValueError(
            f"Growth budget exceeded for {label}: candidate_count={candidate_count}, max_allowed={max_allowed}"
        )


def ensure_growth_constraints_sync(session: Any) -> None:
    for query in GROWTH_CONSTRAINT_QUERIES:
        result = session.run(query)
        consume = getattr(result, "consume", None)
        if callable(consume):
            consume()


async def ensure_growth_constraints_async(session: Any) -> None:
    for query in GROWTH_CONSTRAINT_QUERIES:
        result = await session.run(query)
        consume = getattr(result, "consume", None)
        if callable(consume):
            await consume()
