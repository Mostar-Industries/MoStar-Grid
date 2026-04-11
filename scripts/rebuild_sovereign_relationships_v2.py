#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
        🜂 MOSTAR GRID — SOVEREIGN RELATIONSHIP REBUILDER v2 🜂

    v1 had two bugs:
    - PRECEDES used language join → cartesian explosion (1.25M edges)
    - GUIDED_BY matched "Mo" but graph has "Mo Executor"

    v2 fixes:
    - PRECEDES uses row-order 1:1 pairing (sorted by id)
    - GUIDED_BY uses actual agent names from the graph
    - RealLife label (not RealLifeScenario)
    - Capability-based bulk GUIDED_BY for all 501 agents
═══════════════════════════════════════════════════════════════════════════════
"""

import os
from neo4j import GraphDatabase
from datetime import datetime, timezone

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "mostar123")


# ═══════════════════════════════════════════════════════════════════════════════
#     1. PRECEDES — ROW-ORDER 1:1 PAIRING
#        Sorted by id, paired index-to-index. No cartesian join.
# ═══════════════════════════════════════════════════════════════════════════════

LIFECYCLE_CHAIN = ["Infancy", "Childhood", "Adolescence", "Adulthood"]
KNOWLEDGE_CHAIN = ["Culture", "Ethics", "Science", "RealLife"]

def build_precedes_query(label_from, label_to, chain_name):
    """Row-order 1:1 PRECEDES between two stage labels."""
    return f"""
    MATCH (a:{label_from})
    WITH a ORDER BY a.id
    WITH collect(a) AS from_nodes
    MATCH (b:{label_to})
    WITH from_nodes, b ORDER BY b.id
    WITH from_nodes, collect(b) AS to_nodes
    WITH from_nodes, to_nodes,
         range(0, CASE WHEN size(from_nodes) < size(to_nodes)
                       THEN size(from_nodes) ELSE size(to_nodes) END - 1) AS indices
    UNWIND indices AS i
    WITH from_nodes[i] AS f, to_nodes[i] AS t
    MERGE (f)-[:PRECEDES {{chain: '{chain_name}', rebuilt_at: $timestamp}}]->(t)
    RETURN count(*) AS edges_created
    """


# ═══════════════════════════════════════════════════════════════════════════════
#     2. GUIDED_BY — SACRED AGENT MAPPING (actual names from graph)
#
#     Graph has "Mo Executor" not "Mo". We match with CONTAINS.
#     Then bulk capability-based mapping for all 501 agents.
# ═══════════════════════════════════════════════════════════════════════════════

# Sacred agent name fragments → KnowledgeDomain assignments
SACRED_AGENT_MAP = {
    "Mo": {
        "domains": ["Governance", "Agriculture"],
        "reason": "Mission execution requires governance coordination and resource stewardship"
    },
    "Woo": {
        "domains": ["Philosophy", "Ritual"],
        "reason": "Ethical judgment rooted in philosophical frameworks and ceremonial truth"
    },
    "RAD": {
        "domains": ["Traditional Medicine", "Divination Systems"],
        "reason": "Health surveillance aligned with healing practices and oracle-pattern anomaly detection"
    },
    "TsaTse": {
        "domains": ["Divination Systems", "Governance"],
        "reason": "Systems cartography mirrors divination; strategic forecasting serves governance"
    },
    "Conduit": {
        "domains": ["Language"],
        "reason": "Gateway codex operates through indigenous communication protocols"
    },
    "Flameborn": {
        "domains": ["Philosophy", "Language"],
        "reason": "Narrative synthesis preserves worldviews through indigenous language"
    },
    "alpha": {
        "domains": ["Philosophy", "Ritual"],
        "reason": "Alpha consciousness layer aligned with philosophical and ritual domains"
    }
}

# Capability keywords → KnowledgeDomain (for bulk agent mapping)
CAPABILITY_DOMAIN_MAP = {
    "nlp": "Language",
    "language": "Language",
    "vision": "Divination Systems",
    "anomaly": "Traditional Medicine",
    "surveillance": "Traditional Medicine",
    "health": "Traditional Medicine",
    "analysis": "Governance",
    "strategic": "Governance",
    "decision": "Governance",
    "ethical": "Philosophy",
    "philosophy": "Philosophy",
    "ritual": "Ritual",
    "spiritual": "Ritual",
    "farming": "Agriculture",
    "resource": "Agriculture",
    "coordination": "Governance",
}


def run_rebuild():
    timestamp = datetime.now(timezone.utc).isoformat()
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    total_edges = 0

    with driver.session() as s:
        pre = s.run("MATCH ()-[r]->() RETURN count(r) AS c").single()["c"]
        print(f"\n🜂 PRE-REBUILD: {pre} relationships")
        print("═" * 70)

        # ── PHASE 1: LIFECYCLE PRECEDES (1:1 row-order) ──
        print("\n📍 PHASE 1: LIFECYCLE PRECEDES (1:1 pairing)")
        print("-" * 50)
        for chain, chain_name in [(LIFECYCLE_CHAIN, "lifecycle"), (KNOWLEDGE_CHAIN, "knowledge")]:
            for i in range(len(chain) - 1):
                q = build_precedes_query(chain[i], chain[i+1], chain_name)
                result = s.run(q, timestamp=timestamp)
                count = result.single()["edges_created"]
                total_edges += count
                print(f"  ✅ {chain[i]} → {chain[i+1]}: {count} edges")

        # Bridge: Adulthood → Culture
        q = build_precedes_query("Adulthood", "Culture", "bridge")
        result = s.run(q, timestamp=timestamp)
        count = result.single()["edges_created"]
        total_edges += count
        print(f"  ✅ Adulthood → Culture (bridge): {count} edges")

        # ── PHASE 2: SACRED AGENT GUIDED_BY ──
        print("\n📍 PHASE 2: SACRED AGENT → KNOWLEDGE DOMAIN (GUIDED_BY)")
        print("-" * 50)
        for name_fragment, mapping in SACRED_AGENT_MAP.items():
            for domain in mapping["domains"]:
                result = s.run("""
                    MATCH (a:Agent), (d:KnowledgeDomain {name: $domain})
                    WHERE a.name CONTAINS $fragment
                    MERGE (a)-[:GUIDED_BY {
                        reason: $reason,
                        sovereign: true,
                        rebuilt_at: $timestamp
                    }]->(d)
                    RETURN count(*) AS edges_created
                """, fragment=name_fragment, domain=domain,
                     reason=mapping["reason"], timestamp=timestamp)
                count = result.single()["edges_created"]
                total_edges += count
                print(f"  ✅ *{name_fragment}* → {domain}: {count} edges")

        # ── PHASE 3: CAPABILITY-BASED BULK GUIDED_BY ──
        print("\n📍 PHASE 3: CAPABILITY-BASED GUIDED_BY (all agents)")
        print("-" * 50)
        for keyword, domain in CAPABILITY_DOMAIN_MAP.items():
            result = s.run("""
                MATCH (a:Agent), (d:KnowledgeDomain {name: $domain})
                WHERE toLower(a.capabilities) CONTAINS $keyword
                  AND NOT (a)-[:GUIDED_BY]->(d)
                MERGE (a)-[:GUIDED_BY {
                    reason: 'capability_alignment: ' + $keyword,
                    sovereign: true,
                    rebuilt_at: $timestamp
                }]->(d)
                RETURN count(*) AS edges_created
            """, keyword=keyword, domain=domain, timestamp=timestamp)
            count = result.single()["edges_created"]
            total_edges += count
            if count > 0:
                print(f"  ✅ capability '{keyword}' → {domain}: {count} edges")

        # ── PHASE 4: BELONGS_TO (unchanged from v1) ──
        print("\n📍 PHASE 4: BELONGS_TO (domain membership)")
        print("-" * 50)
        belongs_queries = [
            ("Philosophy → Philosophy",
             "MATCH (p:Philosophy), (d:KnowledgeDomain {name: 'Philosophy'}) MERGE (p)-[:BELONGS_TO {rebuilt_at: $timestamp}]->(d) RETURN count(*) AS edges_created"),
            ("HealingPractice → Traditional Medicine",
             "MATCH (h:HealingPractice), (d:KnowledgeDomain {name: 'Traditional Medicine'}) MERGE (h)-[:BELONGS_TO {rebuilt_at: $timestamp}]->(d) RETURN count(*) AS edges_created"),
            ("OduIfa → Divination Systems",
             "MATCH (o:OduIfa), (d:KnowledgeDomain {name: 'Divination Systems'}) MERGE (o)-[:BELONGS_TO {rebuilt_at: $timestamp}]->(d) RETURN count(*) AS edges_created"),
            ("Governance → Governance",
             "MATCH (g:Governance), (d:KnowledgeDomain {name: 'Governance'}) MERGE (g)-[:BELONGS_TO {rebuilt_at: $timestamp}]->(d) RETURN count(*) AS edges_created"),
            ("Language:Ibibio → Language",
             "MATCH (l:Language {name: 'Ibibio'}), (d:KnowledgeDomain {name: 'Language'}) MERGE (l)-[:BELONGS_TO {rebuilt_at: $timestamp}]->(d) RETURN count(*) AS edges_created"),
        ]
        for name, q in belongs_queries:
            result = s.run(q, timestamp=timestamp)
            count = result.single()["edges_created"]
            total_edges += count
            print(f"  ✅ {name}: {count} edges")

        # ── POST-FLIGHT ──
        post = s.run("MATCH ()-[r]->() RETURN count(r) AS c").single()["c"]
        print("\n" + "═" * 70)
        print(f"🜂 SOVEREIGN REBUILD v2 COMPLETE")
        print(f"  Before:  {pre}")
        print(f"  After:   {post}")
        print(f"  Created: {post - pre}")
        print("═" * 70)

        print("\n📊 RELATIONSHIP TYPE SUMMARY:")
        print("-" * 50)
        for r in s.run("MATCH ()-[r]->() RETURN type(r) AS t, count(r) AS c ORDER BY c DESC"):
            print(f"  {r['t']:30s} → {r['c']:>6,}")

    driver.close()
    print("\n🜂 Sovereign relationships v2 seated. 🜂\n")


if __name__ == "__main__":
    print("""
    ═══════════════════════════════════════════════════════════════
    🜂  MOSTAR GRID — SOVEREIGN RELATIONSHIP REBUILDER v2  🜂
    ═══════════════════════════════════════════════════════════════
    Fixes: 1:1 row-order pairing, actual agent name matching,
           RealLife label, capability-based bulk GUIDED_BY.
    """)
    run_rebuild()
