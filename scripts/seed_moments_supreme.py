#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
    🜂 SEED MOSTAR MOMENTS SUPREME 🜂

    Seeds all MoStarMoment nodes from Mostar_Moment_Supreme.py into Neo4j
    as the Grid's genesis historical memory — from the 2023 covenant
    inception through 2026.

    Handles all three entry formats in the source file:
      1. Simple dicts    — {timestamp, initiator, receiver, description, ...}
      2. mo_star_moment  — kwargs calls (patched to return dicts at load time)
      3. Nested dicts    — {"moments": [...], "relations": [...]}

    MERGE keyed on event_id = SHA256(ts|initiator|receiver|description)[:16]
    Safe to re-run — no duplicates.

    Also wires PRECEDES between chronologically consecutive moments (same source).
═══════════════════════════════════════════════════════════════════════════════
"""

import hashlib
import os
from pathlib import Path
from neo4j import GraphDatabase
from datetime import datetime, timezone

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "mostar123")

MOMENTS_FILE = (
    Path(__file__).parent.parent
    / "memory" / "neo4j-mindgraph" / "memory_layer" / "Mostar_Moment_Supreme.py"
)

# Synthetic timestamp for mo_star_moment() entries that carry no date
WOLFEE_SESSION_TS = "2026-01-04T00:00:00Z"


def load_moments() -> list:
    """
    Exec Mostar_Moment_Supreme.py with mo_star_moment() patched to return dicts.
    Flattens nested {'moments': [...]} entries into the same structure.
    """
    src = MOMENTS_FILE.read_text(encoding="utf-8")
    # Patch the stub so mo_star_moment() returns a usable dict rather than raising
    src = src.replace("raise NotImplementedError", "return dict(**kwargs)")
    ns = {}
    exec(compile(src, str(MOMENTS_FILE), "exec"), ns)
    raw: list = ns.get("MostarMoments", [])

    flat = []
    wolfee_counter = 0  # give distinct pseudo-timestamps to undated entries

    for entry in raw:
        if not isinstance(entry, dict):
            continue  # guard — shouldn't occur after patch

        if "moments" in entry:
            # Nested format: {"moments": [...], "relations": [...]}
            for m in entry.get("moments", []):
                flat.append({
                    "timestamp":   m.get("date", "2026-01-04") + "T00:00:00Z",
                    "initiator":   (m.get("actors", "unknown") or "unknown").split("|")[0],
                    "receiver":    m.get("projects", "MoStar Grid"),
                    "description": m.get("title", ""),
                    "narrative":   m.get("narrative", ""),
                    "trigger":     m.get("kind", ""),
                    "resonance":   float(m.get("impact", "3")) / 5.0,
                    "source_id":   m.get("id", ""),
                    "tags":        m.get("tags", ""),
                    "kind":        m.get("kind", "moment"),
                })
        elif "description" in entry or "initiator" in entry:
            # Simple / mo_star_moment() dict
            resonance_raw = float(
                entry.get("resonance") or entry.get("resonance_score") or 0.0
            )
            # mo_star_moment uses 0-5 scale; simple dicts use 0-1
            resonance = resonance_raw / 5.0 if resonance_raw > 1.0 else resonance_raw

            ts = entry.get("timestamp", "")
            if not ts:
                # Undated Wolfee session entries — space them 1 second apart
                wolfee_counter += 1
                ts = f"2026-01-04T00:{wolfee_counter:02d}:00Z"

            context = entry.get("context_notes", [])
            context_str = " | ".join(context) if isinstance(context, list) else str(context)

            flat.append({
                "timestamp":   ts,
                "initiator":   str(entry.get("initiator", "")),
                "receiver":    str(entry.get("receiver", "")),
                "description": entry.get("description", ""),
                "narrative":   context_str,
                "trigger":     str(entry.get("trigger") or entry.get("trigger_type") or ""),
                "resonance":   resonance,
                "source_id":   "",
                "tags":        "",
                "kind":        "moment",
            })

    return flat


def make_event_id(m: dict) -> str:
    payload = f"{m['timestamp']}|{m['initiator']}|{m['receiver']}|{m['description']}"
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def run():
    seed_timestamp = datetime.now(timezone.utc).isoformat()

    print("\n🜂 LOADING MOSTAR MOMENTS SUPREME …")
    moments = load_moments()
    print(f"   Loaded {len(moments)} moments from source file")
    print("═" * 60)

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    with driver.session() as s:
        pre = s.run("MATCH (m:MoStarMoment) RETURN count(m) AS c").single()["c"]
        print(f"   PRE-SEED: {pre} MoStarMoment nodes")
        print()

        # ── MERGE all moments ──────────────────────────────────────────
        seeded = 0
        for m in moments:
            event_id = make_event_id(m)
            s.run("""
                MERGE (mo:MoStarMoment {event_id: $event_id})
                ON CREATE SET
                    mo.timestamp    = $timestamp,
                    mo.initiator    = $initiator,
                    mo.receiver     = $receiver,
                    mo.description  = $description,
                    mo.narrative    = $narrative,
                    mo.trigger      = $trigger,
                    mo.resonance    = $resonance,
                    mo.source_id    = $source_id,
                    mo.tags         = $tags,
                    mo.kind         = $kind,
                    mo.source       = 'MostarMomentSupreme',
                    mo.created_at   = $seed_timestamp
                ON MATCH SET
                    mo.timestamp    = $timestamp,
                    mo.initiator    = $initiator,
                    mo.receiver     = $receiver,
                    mo.description  = $description,
                    mo.narrative    = $narrative,
                    mo.trigger      = $trigger,
                    mo.resonance    = $resonance,
                    mo.source       = 'MostarMomentSupreme',
                    mo.updated_at   = $seed_timestamp
            """,
                event_id=event_id,
                timestamp=m["timestamp"],
                initiator=m["initiator"],
                receiver=m["receiver"],
                description=m["description"],
                narrative=m["narrative"],
                trigger=m["trigger"],
                resonance=m["resonance"],
                source_id=m["source_id"],
                tags=m["tags"],
                kind=m["kind"],
                seed_timestamp=seed_timestamp,
            )
            ts_short = m["timestamp"][:10]
            desc_preview = m["description"][:40] + ("…" if len(m["description"]) > 40 else "")
            print(f"  ✅ [{ts_short}] {m['initiator'][:12]:12s} → {m['receiver'][:18]:18s}  {desc_preview}")
            seeded += 1

        # ── WIRE PRECEDES (chronological consecutive pairs) ────────────
        print("\n⏱  WIRING PRECEDES (chronological order)")
        s.run("""
            MATCH (m:MoStarMoment {source: 'MostarMomentSupreme'})
            WITH m ORDER BY m.timestamp
            WITH collect(m) AS moments
            UNWIND range(0, size(moments) - 2) AS i
            WITH moments[i] AS a, moments[i + 1] AS b
            MERGE (a)-[:PRECEDES]->(b)
        """)

        post = s.run("MATCH (m:MoStarMoment) RETURN count(m) AS c").single()["c"]
        prec = s.run(
            "MATCH (:MoStarMoment)-[r:PRECEDES]->(:MoStarMoment) RETURN count(r) AS c"
        ).single()["c"]
        print(f"\n🜂 POST-SEED: {post} MoStarMoment nodes (+{post - pre} new)")
        print(f"⏱  {prec} PRECEDES relationships wired")
        print()

    driver.close()


if __name__ == "__main__":
    run()
