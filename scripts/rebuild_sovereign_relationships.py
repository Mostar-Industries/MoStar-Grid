#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
            🜂 MOSTAR GRID — SOVEREIGN RELATIONSHIP REBUILDER 🜂

    The Aura export captured relationship types but not node references.
    The old relationships were MostlyAI synthetic — random placeholder edges.

    This script rebuilds REAL relationships from the 40k+ nodes
    already seated in the graph:

    1. PRECEDES — Deterministic lifecycle stage chain
    2. GUIDED_BY — Agent→KnowledgeDomain alignment (sovereign mapping)
    3. PRECEDES — Odú sequential progression (if missing)
    4. Cross-domain knowledge wiring

    SIMILAR_TO is already seated (5,000 edges) — untouched.
═══════════════════════════════════════════════════════════════════════════════
"""

import os
from neo4j import GraphDatabase
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════════════
#                           CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "mostar123")


# ═══════════════════════════════════════════════════════════════════════════════
#     1. PRECEDES — LIFECYCLE STAGE CHAIN (Deterministic)
#
#     Infancy → Childhood → Adolescence → Adulthood
#
#     These are human development stages. The PRECEDES relationship
#     connects representative nodes across stages using matching
#     activity_type or primary_language as alignment keys.
# ═══════════════════════════════════════════════════════════════════════════════

LIFECYCLE_CHAIN = ["Infancy", "Childhood", "Adolescence", "Adulthood"]

# Knowledge progression chain (parallel track)
KNOWLEDGE_CHAIN = ["Culture", "Ethics", "Science", "RealLifeScenario"]

LIFECYCLE_PRECEDES_QUERIES = []

# Build pairwise PRECEDES for lifecycle stages
for i in range(len(LIFECYCLE_CHAIN) - 1):
    stage_from = LIFECYCLE_CHAIN[i]
    stage_to = LIFECYCLE_CHAIN[i + 1]
    # Connect nodes that share the same primary_language (cultural thread)
    LIFECYCLE_PRECEDES_QUERIES.append({
        "name": f"{stage_from} → {stage_to} (by language)",
        "query": f"""
        MATCH (a:{stage_from}), (b:{stage_to})
        WHERE a.primary_language = b.primary_language
        MERGE (a)-[:PRECEDES {{
            chain: 'lifecycle',
            reason: 'shared_language_thread',
            rebuilt_at: $timestamp
        }}]->(b)
        RETURN count(*) AS edges_created
        """
    })

# Build pairwise PRECEDES for knowledge progression
for i in range(len(KNOWLEDGE_CHAIN) - 1):
    stage_from = KNOWLEDGE_CHAIN[i]
    stage_to = KNOWLEDGE_CHAIN[i + 1]
    LIFECYCLE_PRECEDES_QUERIES.append({
        "name": f"{stage_from} → {stage_to} (by language)",
        "query": f"""
        MATCH (a:{stage_from}), (b:{stage_to})
        WHERE a.primary_language = b.primary_language
        MERGE (a)-[:PRECEDES {{
            chain: 'knowledge',
            reason: 'shared_language_thread',
            rebuilt_at: $timestamp
        }}]->(b)
        RETURN count(*) AS edges_created
        """
    })

# Cross-bridge: Adulthood → Culture (lifecycle feeds knowledge)
LIFECYCLE_PRECEDES_QUERIES.append({
    "name": "Adulthood → Culture (lifecycle→knowledge bridge)",
    "query": """
    MATCH (a:Adulthood), (b:Culture)
    WHERE a.primary_language = b.primary_language
    MERGE (a)-[:PRECEDES {
        chain: 'bridge',
        reason: 'lifecycle_to_knowledge_transition',
        rebuilt_at: $timestamp
    }]->(b)
    RETURN count(*) AS edges_created
    """
})


# ═══════════════════════════════════════════════════════════════════════════════
#     2. GUIDED_BY — AGENT → KNOWLEDGE DOMAIN (Sovereign Alignment)
#
#     Each Agent is assigned to KnowledgeDomains based on their
#     capabilities and role — NOT randomly generated.
#
#     Mo (executor)         → Governance, Agriculture
#     Woo (judge)           → Philosophy, Ritual
#     RAD-X-FLB (sentinel)  → Traditional Medicine, Divination Systems
#     TsaTse Fly (analyst)  → Divination Systems, Governance
#     Code Conduit (gateway) → Language
#     Flameborn Writer (narrator) → Philosophy, Language
# ═══════════════════════════════════════════════════════════════════════════════

AGENT_DOMAIN_MAP = {
    "Mo": {
        "domains": ["Governance", "Agriculture"],
        "reason": "Mission execution requires governance coordination and resource stewardship"
    },
    "Woo": {
        "domains": ["Philosophy", "Ritual"],
        "reason": "Ethical judgment rooted in philosophical frameworks and ceremonial truth"
    },
    "RAD-X-FLB": {
        "domains": ["Traditional Medicine", "Divination Systems"],
        "reason": "Health surveillance aligned with healing practices and anomaly detection via oracle patterns"
    },
    "TsaTse Fly": {
        "domains": ["Divination Systems", "Governance"],
        "reason": "Systems cartography mirrors divination pattern analysis; strategic forecasting serves governance"
    },
    "Code Conduit": {
        "domains": ["Language"],
        "reason": "Gateway codex operates through indigenous communication protocols"
    },
    "Flameborn Writer": {
        "domains": ["Philosophy", "Language"],
        "reason": "Narrative synthesis preserves philosophical worldviews through indigenous language"
    }
}

GUIDED_BY_QUERIES = []
for agent_name, mapping in AGENT_DOMAIN_MAP.items():
    for domain in mapping["domains"]:
        GUIDED_BY_QUERIES.append({
            "name": f"{agent_name} ←GUIDED_BY→ {domain}",
            "query": """
            MATCH (a:Agent {name: $agent_name}), (d:KnowledgeDomain {name: $domain})
            MERGE (a)-[:GUIDED_BY {
                reason: $reason,
                sovereign: true,
                rebuilt_at: $timestamp
            }]->(d)
            RETURN count(*) AS edges_created
            """,
            "params": {
                "agent_name": agent_name,
                "domain": domain,
                "reason": mapping["reason"]
            }
        })


# ═══════════════════════════════════════════════════════════════════════════════
#     3. PRECEDES — ODÚ SEQUENTIAL CHAIN (Restore if missing)
#
#     Odú 0 → 1 → 2 → ... → 255
#     This was originally created in phase 1 import.
#     We MERGE to avoid duplicates.
# ═══════════════════════════════════════════════════════════════════════════════

ODU_PRECEDES_QUERY = {
    "name": "Odú sequential chain (0→255)",
    "query": """
    MATCH (o1:OduIfa), (o2:OduIfa)
    WHERE o2.odu_number = o1.odu_number + 1
    MERGE (o1)-[:PRECEDES {chain: 'odu_sequence', rebuilt_at: $timestamp}]->(o2)
    RETURN count(*) AS edges_created
    """
}


# ═══════════════════════════════════════════════════════════════════════════════
#     4. BELONGS_TO — RESTORE DOMAIN MEMBERSHIP (if missing)
# ═══════════════════════════════════════════════════════════════════════════════

BELONGS_TO_QUERIES = [
    {
        "name": "Philosophy → KnowledgeDomain:Philosophy",
        "query": """
        MATCH (p:Philosophy), (d:KnowledgeDomain {name: "Philosophy"})
        MERGE (p)-[:BELONGS_TO {rebuilt_at: $timestamp}]->(d)
        RETURN count(*) AS edges_created
        """
    },
    {
        "name": "HealingPractice → KnowledgeDomain:Traditional Medicine",
        "query": """
        MATCH (h:HealingPractice), (d:KnowledgeDomain {name: "Traditional Medicine"})
        MERGE (h)-[:BELONGS_TO {rebuilt_at: $timestamp}]->(d)
        RETURN count(*) AS edges_created
        """
    },
    {
        "name": "OduIfa → KnowledgeDomain:Divination Systems",
        "query": """
        MATCH (o:OduIfa), (d:KnowledgeDomain {name: "Divination Systems"})
        MERGE (o)-[:BELONGS_TO {rebuilt_at: $timestamp}]->(d)
        RETURN count(*) AS edges_created
        """
    },
    {
        "name": "Governance → KnowledgeDomain:Governance",
        "query": """
        MATCH (g:Governance), (d:KnowledgeDomain {name: "Governance"})
        MERGE (g)-[:BELONGS_TO {rebuilt_at: $timestamp}]->(d)
        RETURN count(*) AS edges_created
        """
    },
    {
        "name": "Language:Ibibio → KnowledgeDomain:Language",
        "query": """
        MATCH (lang:Language {name: "Ibibio"}), (d:KnowledgeDomain {name: "Language"})
        MERGE (lang)-[:BELONGS_TO {rebuilt_at: $timestamp}]->(d)
        RETURN count(*) AS edges_created
        """
    }
]


# ═══════════════════════════════════════════════════════════════════════════════
#                           EXECUTION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

def run_rebuild():
    timestamp = datetime.utcnow().isoformat()
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    total_edges = 0
    results_log = []

    with driver.session() as session:
        # ── Pre-flight: count existing relationships ──
        pre_count = session.run("MATCH ()-[r]->() RETURN count(r) AS total").single()["total"]
        print(f"\n🜂 PRE-REBUILD RELATIONSHIP COUNT: {pre_count}")
        print("═" * 70)

        # ── Phase 1: Lifecycle PRECEDES ──
        print("\n📍 PHASE 1: LIFECYCLE PRECEDES CHAIN")
        print("-" * 50)
        for q in LIFECYCLE_PRECEDES_QUERIES:
            result = session.run(q["query"], timestamp=timestamp)
            count = result.single()["edges_created"]
            total_edges += count
            results_log.append((q["name"], count))
            print(f"  ✅ {q['name']}: {count} edges")

        # ── Phase 2: GUIDED_BY ──
        print("\n📍 PHASE 2: AGENT → KNOWLEDGE DOMAIN (GUIDED_BY)")
        print("-" * 50)
        for q in GUIDED_BY_QUERIES:
            params = q.get("params", {})
            params["timestamp"] = timestamp
            result = session.run(q["query"], **params)
            count = result.single()["edges_created"]
            total_edges += count
            results_log.append((q["name"], count))
            print(f"  ✅ {q['name']}: {count} edges")

        # ── Phase 3: Odú PRECEDES ──
        print("\n📍 PHASE 3: ODÚ SEQUENTIAL PRECEDES")
        print("-" * 50)
        result = session.run(ODU_PRECEDES_QUERY["query"], timestamp=timestamp)
        count = result.single()["edges_created"]
        total_edges += count
        results_log.append((ODU_PRECEDES_QUERY["name"], count))
        print(f"  ✅ {ODU_PRECEDES_QUERY['name']}: {count} edges")

        # ── Phase 4: BELONGS_TO ──
        print("\n📍 PHASE 4: BELONGS_TO (Domain Membership)")
        print("-" * 50)
        for q in BELONGS_TO_QUERIES:
            result = session.run(q["query"], timestamp=timestamp)
            count = result.single()["edges_created"]
            total_edges += count
            results_log.append((q["name"], count))
            print(f"  ✅ {q['name']}: {count} edges")

        # ── Post-flight ──
        post_count = session.run("MATCH ()-[r]->() RETURN count(r) AS total").single()["total"]

        print("\n" + "═" * 70)
        print(f"🜂 SOVEREIGN REBUILD COMPLETE")
        print(f"  Relationships before: {pre_count}")
        print(f"  Relationships after:  {post_count}")
        print(f"  New edges created:    {post_count - pre_count}")
        print(f"  MERGE operations:     {total_edges}")
        print("═" * 70)

        # ── Verification ──
        print("\n📊 RELATIONSHIP TYPE SUMMARY:")
        print("-" * 50)
        type_counts = session.run("""
            MATCH ()-[r]->()
            RETURN type(r) AS rel_type, count(r) AS count
            ORDER BY count DESC
        """)
        for record in type_counts:
            print(f"  {record['rel_type']:30s} → {record['count']:>6,}")

    driver.close()
    print("\n🜂 Driver closed. Sovereign relationships seated. 🜂\n")


if __name__ == "__main__":
    print("""
    ═══════════════════════════════════════════════════════════════
    🜂  MOSTAR GRID — SOVEREIGN RELATIONSHIP REBUILDER  🜂
    ═══════════════════════════════════════════════════════════════
    
    Rebuilding from 40k+ nodes already in the graph.
    Old MostlyAI synthetic edges are dead. These are REAL.
    
    PRECEDES  — Lifecycle stages + Odú sequence
    GUIDED_BY — Agent→KnowledgeDomain sovereign alignment
    BELONGS_TO — Domain membership restoration
    SIMILAR_TO — Already seated (5,000 edges, untouched)
    """)
    run_rebuild()
