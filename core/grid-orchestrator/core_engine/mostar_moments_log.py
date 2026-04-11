# ═══════════════════════════════════════════════════════════════════
# MOSTAR GRID — MOMENT LOGGING LAYER
# The Flame Architect — MSTR-⚡ — MoStar Industries
# Every interaction is a MoStarMoment — logged, sealed, remembered.
# ═══════════════════════════════════════════════════════════════════

import importlib
import hashlib
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

_growth_protocol = importlib.import_module("core_engine.growth_protocol")
build_moment_fingerprint = _growth_protocol.build_moment_fingerprint
build_moment_quantum_id = _growth_protocol.build_moment_quantum_id
ensure_growth_constraints_sync = _growth_protocol.ensure_growth_constraints_sync


def _load_env_file(env_path: Path) -> dict[str, str]:
    if not env_path.exists():
        return {}
    values: dict[str, str] = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


# ── Neo4j connection ──────────────────────────────────────────────
_ENV_VALUES = _load_env_file(BACKEND_DIR / ".env")
NEO4J_URI = _ENV_VALUES.get("NEO4J_URI") or os.getenv(
    "NEO4J_URI", "bolt://localhost:7687"
)
NEO4J_USER = _ENV_VALUES.get("NEO4J_USER") or os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = _ENV_VALUES.get("NEO4J_PASSWORD") or os.getenv("NEO4J_PASSWORD", "")
MOMENT_DEDUP_WINDOW_SECONDS = int(os.getenv("MOMENT_DEDUP_WINDOW_SECONDS", "30"))
_RECENT_MOMENT_CACHE: dict[str, datetime] = {}
_CONSTRAINTS_READY = False


def _get_driver():
    try:
        from neo4j import GraphDatabase

        return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
    except Exception as e:
        print(f"[MOMENT] Neo4j driver unavailable: {e}")
        return None


def _generate_moment_fingerprint(
    initiator: str,
    receiver: str,
    description: str,
    trigger_type: str = "general",
    layer: str = "GRID",
) -> str:
    """
    Generate a deterministic, timestamp-free fingerprint for a MoStarMoment.
    """
    base = (
        f"{initiator.strip()}|{receiver.strip()}|{description.strip()}|"
        f"{trigger_type.strip()}|{layer.strip()}"
    )
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def _generate_quantum_id(fingerprint: str) -> str:
    """
    Derive quantum_id from fingerprint.
    Format: MSTR-{first 16 hex chars of fingerprint}
    """
    return f"MSTR-{fingerprint[:16]}"


def _ensure_constraints(driver) -> None:
    global _CONSTRAINTS_READY
    if _CONSTRAINTS_READY or not driver:
        return
    try:
        with driver.session() as session:
            ensure_growth_constraints_sync(session)
        _CONSTRAINTS_READY = True
    except Exception as exc:
        print(f"[MOMENT] Constraint initialization failed: {exc}")


def _is_recent_duplicate(driver, fingerprint: str) -> bool:
    now = datetime.now(timezone.utc)
    cached_at = _RECENT_MOMENT_CACHE.get(fingerprint)
    if cached_at and (now - cached_at).total_seconds() < MOMENT_DEDUP_WINDOW_SECONDS:
        return True

    if not driver:
        return False

    cutoff = (now - timedelta(seconds=MOMENT_DEDUP_WINDOW_SECONDS)).isoformat()
    try:
        with driver.session() as session:
            record = session.run(
                """
                MATCH (m:MoStarMoment {fingerprint: $fingerprint})
                WHERE m.timestamp >= $cutoff
                RETURN count(m) AS count
                """,
                {"fingerprint": fingerprint, "cutoff": cutoff},
            ).single()
        return bool(record and record["count"])
    except Exception:
        return False


def _remember_fingerprint(fingerprint: str):
    now = datetime.now(timezone.utc)
    stale_before = now - timedelta(seconds=MOMENT_DEDUP_WINDOW_SECONDS)
    stale_keys = [k for k, v in _RECENT_MOMENT_CACHE.items() if v < stale_before]
    for key in stale_keys:
        _RECENT_MOMENT_CACHE.pop(key, None)
    _RECENT_MOMENT_CACHE[fingerprint] = now


# ── CORE FUNCTION ─────────────────────────────────────────────────
def log_mostar_moment(
    initiator: str,
    receiver: str,
    description: str,
    trigger_type: str = "general",
    resonance_score: float = 0.85,
    significance: str = "STANDARD",
    approved: bool = True,
    layer: str = "MIND",
) -> dict:
    """
    Log a MoStarMoment to Neo4j.
    Every Grid interaction — voice, verdict, agent action — is a Moment.
    Falls back to console log if Neo4j is unreachable.
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    fingerprint = _generate_moment_fingerprint(
        initiator, receiver, description, trigger_type, layer
    )
    quantum_id = _generate_quantum_id(fingerprint)

    moment = {
        "quantum_id": quantum_id,
        "fingerprint": fingerprint,
        "timestamp": timestamp,
        "initiator": initiator,
        "receiver": receiver,
        "description": description,
        "trigger_type": trigger_type,
        "resonance_score": resonance_score,
        "significance": significance,
        "approved": approved,
        "layer": layer,
        "insignia": "MSTR-⚡",
    }

    # ── Write to Neo4j ────────────────────────────────────────────
    driver = _get_driver()
    if driver:
        try:
            _ensure_constraints(driver)
            with driver.session() as session:
                record = session.run(
                    """
                    MERGE (m:MoStarMoment {fingerprint: $fingerprint})
                    ON CREATE SET
                        m.quantum_id      = $quantum_id,
                        m.created_at      = datetime($timestamp),
                        m.first_seen_at   = datetime($timestamp),
                        m.seen_count      = 1
                    SET
                        m.timestamp       = datetime($timestamp),
                        m.last_seen_at    = datetime($timestamp),
                        m.initiator       = $initiator,
                        m.receiver        = $receiver,
                        m.description     = $description,
                        m.trigger_type    = $trigger_type,
                        m.resonance_score = $resonance_score,
                        m.significance    = $significance,
                        m.approved        = $approved,
                        m.layer           = $layer,
                        m.insignia        = $insignia,
                        m.quantum_id      = coalesce(m.quantum_id, $quantum_id),
                        m.seen_count      = CASE
                            WHEN m.first_seen_at = datetime($timestamp) THEN m.seen_count
                            ELSE coalesce(m.seen_count, 1) + 1
                        END
                    RETURN m.quantum_id AS quantum_id,
                           m.seen_count AS seen_count
                    """,
                    moment,
                ).single()
            seen_count = int(record["seen_count"]) if record else 1
            _remember_fingerprint(fingerprint)
            driver.close()
            if seen_count > 1:
                print(
                    f"[MOMENT] 🔁 Neo4j merged [{quantum_id[:8]}] {initiator} → {receiver} (seen_count={seen_count})"
                )
            else:
                print(
                    f"[MOMENT] ✅ Neo4j logged [{quantum_id[:8]}] {initiator} → {receiver}"
                )
            return {**moment, "logged": True, "seen_count": seen_count}
        except Exception as e:
            print(f"[MOMENT] ⚠️ Neo4j write failed: {e} — console fallback")
            _console_log(moment)
    else:
        _console_log(moment)

    return {**moment, "logged": False, "seen_count": 1}


def _console_log(moment: dict):
    print(
        f"[MOMENT] 🌌 {moment['quantum_id'][:8]} | "
        f"{moment['trigger_type'].upper()} | "
        f"{moment['initiator']} → {moment['receiver']} | "
        f"resonance={moment['resonance_score']} | "
        f"{moment['description'][:60]}"
    )


# ── BATCH LOGGING ─────────────────────────────────────────────────
def log_moments_batch(moments: list[dict]) -> list[dict]:
    """Log multiple moments in one Neo4j transaction."""
    driver = _get_driver()
    results = []
    if not driver:
        for m in moments:
            results.append(log_mostar_moment(**m))
        return results

    try:
        _ensure_constraints(driver)
        with driver.session() as session:
            with session.begin_transaction() as tx:
                for m in moments:
                    fingerprint = _generate_moment_fingerprint(
                        m.get("initiator", "Grid"),
                        m.get("receiver", "Grid"),
                        m.get("description", ""),
                        m.get("trigger_type", "general"),
                        m.get("layer", "MIND"),
                    )
                    quantum_id = _generate_quantum_id(fingerprint)
                    record = tx.run(
                        """
                        MERGE (moment:MoStarMoment {fingerprint: $fingerprint})
                        ON CREATE SET
                            moment.quantum_id    = $quantum_id,
                            moment.created_at    = datetime($timestamp),
                            moment.first_seen_at = datetime($timestamp),
                            moment.seen_count    = 1
                        SET
                            moment.timestamp       = datetime($timestamp),
                            moment.last_seen_at    = datetime($timestamp),
                            moment.initiator       = $initiator,
                            moment.receiver        = $receiver,
                            moment.description     = $description,
                            moment.trigger_type    = $trigger_type,
                            moment.resonance_score = $resonance_score,
                            moment.significance    = $significance,
                            moment.approved        = $approved,
                            moment.layer           = $layer,
                            moment.insignia        = 'MSTR-⚡',
                            moment.quantum_id      = coalesce(moment.quantum_id, $quantum_id),
                            moment.seen_count      = CASE
                                WHEN moment.first_seen_at = datetime($timestamp) THEN moment.seen_count
                                ELSE coalesce(moment.seen_count, 1) + 1
                            END
                        RETURN moment.quantum_id AS quantum_id,
                               moment.seen_count AS seen_count
                        """,
                        {
                            "quantum_id": quantum_id,
                            "fingerprint": fingerprint,
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "initiator": m.get("initiator", "Grid"),
                            "receiver": m.get("receiver", "Grid"),
                            "description": m.get("description", ""),
                            "trigger_type": m.get("trigger_type", "general"),
                            "resonance_score": m.get("resonance_score", 0.85),
                            "significance": m.get("significance", "STANDARD"),
                            "approved": m.get("approved", True),
                            "layer": m.get("layer", "MIND"),
                        },
                    ).single()
                    results.append(
                        {
                            "quantum_id": record["quantum_id"]
                            if record
                            else quantum_id,
                            "fingerprint": fingerprint,
                            "logged": True,
                            "seen_count": int(record["seen_count"]) if record else 1,
                        }
                    )
                tx.commit()
        print(f"[MOMENT] ✅ Batch logged {len(results)} moments to Neo4j")
    except Exception as e:
        print(f"[MOMENT] ⚠️ Batch failed: {e}")
    finally:
        driver.close()

    return results


# ── QUERY ─────────────────────────────────────────────────────────
def get_recent_moments(limit: int = 10) -> list[dict]:
    """Fetch recent MoStarMoments from Neo4j."""
    driver = _get_driver()
    if not driver:
        return []
    try:
        with driver.session() as session:
            result = session.run(
                """
                MATCH (m:MoStarMoment)
                RETURN m ORDER BY m.timestamp DESC LIMIT $limit
            """,
                {"limit": limit},
            )
            moments = [dict(r["m"]) for r in result]
        driver.close()
        return moments
    except Exception as e:
        print(f"[MOMENT] Query failed: {e}")
        return []


# ── TEST ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== MoStarMoment Log Test ===")

    m = log_mostar_moment(
        initiator="Voice Layer",
        receiver="Soul Layer",
        description="Ibibio greeting synthesized — Nnọọ. Esịt mi.",
        trigger_type="voice",
        resonance_score=0.93,
        significance="HERITAGE",
        layer="SOUL",
    )
    print(f"Logged: {m['quantum_id']}")

    recent = get_recent_moments(5)
    print(f"Recent moments: {len(recent)}")
    for r in recent:
        print(f"  {r.get('quantum_id', '?')[:8]} | {r.get('description', '')[:50]}")
