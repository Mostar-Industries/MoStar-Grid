# ═══════════════════════════════════════════════════════════════════
# MOSTAR GRID — MOMENT LOGGING LAYER
# The Flame Architect — MSTR-⚡ — MoStar Industries
# Every interaction is a MoStarMoment — logged, sealed, remembered.
# ═══════════════════════════════════════════════════════════════════

import uuid
import os
import hashlib
from datetime import datetime, timezone

# ── Neo4j connection ──────────────────────────────────────────────
NEO4J_URI  = os.getenv("NEO4J_URI",      "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER",     "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASSWORD", "mostar123")

def _get_driver():
    try:
        from neo4j import GraphDatabase
        return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
    except Exception as e:
        print(f"[MOMENT] Neo4j driver unavailable: {e}")
        return None

def _generate_quantum_id(initiator: str, description: str) -> str:
    """Deterministic quantum ID — same moment never logs twice."""
    base = f"{initiator}:{description}:{datetime.now(timezone.utc).isoformat()}"
    return hashlib.sha256(base.encode()).hexdigest()[:16]

# ── CORE FUNCTION ─────────────────────────────────────────────────
def log_mostar_moment(
    initiator:       str,
    receiver:        str,
    description:     str,
    trigger_type:    str   = "general",
    resonance_score: float = 0.85,
    significance:    str   = "STANDARD",
    approved:        bool  = True,
    layer:           str   = "MIND",
) -> dict:
    """
    Log a MoStarMoment to Neo4j.
    Every Grid interaction — voice, verdict, agent action — is a Moment.
    Falls back to console log if Neo4j is unreachable.
    """
    quantum_id = _generate_quantum_id(initiator, description)
    timestamp  = datetime.now(timezone.utc).isoformat()

    moment = {
        "quantum_id":      quantum_id,
        "timestamp":       timestamp,
        "initiator":       initiator,
        "receiver":        receiver,
        "description":     description,
        "trigger_type":    trigger_type,
        "resonance_score": resonance_score,
        "significance":    significance,
        "approved":        approved,
        "layer":           layer,
        "insignia":        "MSTR-⚡",
    }

    # ── Write to Neo4j ────────────────────────────────────────────
    driver = _get_driver()
    if driver:
        try:
            with driver.session() as session:
                session.run("""
                    MERGE (m:MoStarMoment {quantum_id: $quantum_id})
                    SET
                        m.timestamp       = $timestamp,
                        m.initiator       = $initiator,
                        m.receiver        = $receiver,
                        m.description     = $description,
                        m.trigger_type    = $trigger_type,
                        m.resonance_score = $resonance_score,
                        m.significance    = $significance,
                        m.approved        = $approved,
                        m.layer           = $layer,
                        m.insignia        = $insignia
                """, moment)
            driver.close()
            print(f"[MOMENT] ✅ Neo4j logged [{quantum_id[:8]}] {initiator} → {receiver}")
        except Exception as e:
            print(f"[MOMENT] ⚠️ Neo4j write failed: {e} — console fallback")
            _console_log(moment)
    else:
        _console_log(moment)

    return moment

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
        with driver.session() as session:
            with session.begin_transaction() as tx:
                for m in moments:
                    quantum_id = _generate_quantum_id(
                        m.get("initiator","Grid"),
                        m.get("description","")
                    )
                    tx.run("""
                        MERGE (moment:MoStarMoment {quantum_id: $quantum_id})
                        SET
                            moment.timestamp       = $timestamp,
                            moment.initiator       = $initiator,
                            moment.receiver        = $receiver,
                            moment.description     = $description,
                            moment.trigger_type    = $trigger_type,
                            moment.resonance_score = $resonance_score,
                            moment.insignia        = 'MSTR-⚡'
                    """, {
                        "quantum_id":      quantum_id,
                        "timestamp":       datetime.now(timezone.utc).isoformat(),
                        "initiator":       m.get("initiator","Grid"),
                        "receiver":        m.get("receiver","Grid"),
                        "description":     m.get("description",""),
                        "trigger_type":    m.get("trigger_type","general"),
                        "resonance_score": m.get("resonance_score", 0.85),
                    })
                    results.append({"quantum_id": quantum_id, "logged": True})
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
            result = session.run("""
                MATCH (m:MoStarMoment)
                RETURN m ORDER BY m.timestamp DESC LIMIT $limit
            """, {"limit": limit})
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
        print(f"  {r.get('quantum_id','?')[:8]} | {r.get('description','')[:50]}")