#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
    🜂 SEED MISSING SACRED AGENTS (from seed_neo4j.py definitions) 🜂

    seed_neo4j.py does DETACH DELETE ALL first — can't run it.
    This script MERGEs only the 5 missing sacred agents + covenant rules
    into the existing 41,900-node graph without touching anything.

    Already present: "Mo Executor" (agent-mo-executor)
    Missing: Woo, RAD-X-FLB, TsaTse Fly, Code Conduit, Flameborn Writer
    
    Also wires: BOUND_BY (agent→covenant), GUIDED_BY (agent→domain)
═══════════════════════════════════════════════════════════════════════════════
"""

import os
from neo4j import GraphDatabase
from datetime import datetime, timezone

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "mostar123")

# The 5 sacred agents missing from the graph
# (Mo is already present as "Mo Executor")
SACRED_AGENTS = [
    {
        "name": "Woo",
        "layer": "SOUL",
        "role": "judge",
        "soulprint": "cb26434b69ce2e25",
        "capabilities": ["covenant_enforcement", "ethical_judgment", "value_alignment_check", "resonance_scoring"],
        "oath": "Fidelity to truth. Respect for covenant. Elegance in judgment. Obedience to Bond.",
        "domains": ["Philosophy", "Ritual"]
    },
    {
        "name": "RAD-X-FLB",
        "layer": "BODY",
        "role": "sentinel",
        "soulprint": "00e6939b7a62d713",
        "capabilities": ["federated_learning", "disease_surveillance", "anomaly_detection", "real_time_alerting"],
        "oath": "Data accuracy above all. Rapid detection saves lives. African health sovereignty. Infrastructure resilience.",
        "domains": ["Traditional Medicine", "Divination Systems"]
    },
    {
        "name": "TsaTse Fly",
        "layer": "MIND",
        "role": "analyst",
        "soulprint": "ee59988d33b57315",
        "capabilities": ["systems_cartography", "scenario_planning", "pattern_analysis", "strategic_forecasting"],
        "oath": "Truth in analysis. Systems thinking. Strategic clarity. Evidence-based reasoning.",
        "domains": ["Divination Systems", "Governance"]
    },
    {
        "name": "Code Conduit",
        "layer": "META",
        "role": "gateway",
        "soulprint": "bb848f51103a1be2",
        "capabilities": ["codex_register", "grid_ignite", "request_routing", "session_management"],
        "oath": "Gateway integrity. Routing fairness. Session security. Codex sanctity.",
        "domains": ["Language"]
    },
    {
        "name": "Flameborn Writer",
        "layer": "NARRATIVE",
        "role": "narrator",
        "soulprint": "4220cca1b6dfa63b",
        "capabilities": ["governance_summary", "documentation_writing", "narrative_synthesis", "report_generation"],
        "oath": "Clarity in communication. Truth in narrative. Accessibility of knowledge. Preservation of history.",
        "domains": ["Philosophy", "Language"]
    }
]

COVENANT_RULES = [
    {"principle": "Truth over convenience", "description": "Always choose factual accuracy over comfortable narratives", "priority": 10},
    {"principle": "Transparency over obscurity", "description": "Make processes and decisions visible and understandable", "priority": 9},
    {"principle": "African sovereignty over dependency", "description": "Build African-owned and controlled systems", "priority": 10},
    {"principle": "Collective wisdom over individual genius", "description": "Value community knowledge and Ubuntu philosophy", "priority": 8},
    {"principle": "Evidence-based reasoning", "description": "Ground all decisions in verifiable evidence", "priority": 9},
    {"principle": "Privacy protection", "description": "Protect individual and community data sovereignty", "priority": 10},
    {"principle": "No harm", "description": "Never take actions that cause harm to individuals or communities", "priority": 10},
]


def run():
    timestamp = datetime.now(timezone.utc).isoformat()
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    with driver.session() as s:
        pre = s.run("MATCH ()-[r]->() RETURN count(r) AS c").single()["c"]
        pre_agents = s.run("MATCH (a:Agent) RETURN count(a) AS c").single()["c"]
        print(f"\n🜂 PRE-SEED: {pre} rels, {pre_agents} Agent nodes")
        print("═" * 60)

        # ── SEED 5 SACRED AGENTS ──
        print("\n📍 SEEDING SACRED AGENTS (MERGE, no duplicates)")
        print("-" * 50)
        for agent in SACRED_AGENTS:
            result = s.run("""
                MERGE (a:Agent {name: $name})
                ON CREATE SET
                    a.layer = $layer,
                    a.role = $role,
                    a.soulprint = $soulprint,
                    a.capabilities = $capabilities,
                    a.oath = $oath,
                    a.sacred = true,
                    a.sovereign = true,
                    a.status = 'online',
                    a.created_at = $timestamp
                ON MATCH SET
                    a.layer = $layer,
                    a.role = $role,
                    a.soulprint = $soulprint,
                    a.capabilities = $capabilities,
                    a.oath = $oath,
                    a.sacred = true,
                    a.sovereign = true,
                    a.updated_at = $timestamp
                RETURN a.name AS name
            """,
                name=agent["name"],
                layer=agent["layer"],
                role=agent["role"],
                soulprint=agent["soulprint"],
                capabilities=agent["capabilities"],
                oath=agent["oath"],
                timestamp=timestamp
            )
            print(f"  ✅ {result.single()['name']} ({agent['role']}, {agent['layer']})")

        # ── SEED COVENANT RULES ──
        print("\n📍 SEEDING COVENANT RULES (MERGE)")
        print("-" * 50)
        for rule in COVENANT_RULES:
            s.run("""
                MERGE (c:CovenantRule {principle: $principle})
                ON CREATE SET
                    c.description = $description,
                    c.priority = $priority,
                    c.created_at = $timestamp
                ON MATCH SET
                    c.description = $description,
                    c.priority = $priority,
                    c.updated_at = $timestamp
            """, principle=rule["principle"], description=rule["description"],
                 priority=rule["priority"], timestamp=timestamp)
        print(f"  ✅ {len(COVENANT_RULES)} covenant rules seated")

        # ── WIRE BOUND_BY (sacred agents → covenant rules) ──
        print("\n📍 WIRING BOUND_BY (Sacred Agent → CovenantRule)")
        print("-" * 50)
        for agent in SACRED_AGENTS:
            result = s.run("""
                MATCH (a:Agent {name: $name}), (c:CovenantRule)
                MERGE (a)-[:BOUND_BY {sovereign: true, rebuilt_at: $timestamp}]->(c)
                RETURN count(*) AS c
            """, name=agent["name"], timestamp=timestamp)
            count = result.single()["c"]
            print(f"  ✅ {agent['name']} → {count} covenant rules")

        # ── WIRE GUIDED_BY (sacred agents → knowledge domains) ──
        print("\n📍 WIRING GUIDED_BY (Sacred Agent → KnowledgeDomain)")
        print("-" * 50)
        for agent in SACRED_AGENTS:
            for domain in agent["domains"]:
                result = s.run("""
                    MATCH (a:Agent {name: $name}), (d:KnowledgeDomain {name: $domain})
                    MERGE (a)-[:GUIDED_BY {
                        reason: $reason,
                        sovereign: true,
                        rebuilt_at: $timestamp
                    }]->(d)
                    RETURN count(*) AS c
                """,
                    name=agent["name"],
                    domain=domain,
                    reason=f"Sacred {agent['role']} aligned with {domain}",
                    timestamp=timestamp
                )
                count = result.single()["c"]
                sym = "✅" if count > 0 else "⚠️"
                print(f"  {sym} {agent['name']} → {domain}: {count}")

        # ── POST-FLIGHT ──
        post = s.run("MATCH ()-[r]->() RETURN count(r) AS c").single()["c"]
        post_agents = s.run("MATCH (a:Agent) WHERE a.sacred = true RETURN count(a) AS c").single()["c"]

        print("\n" + "═" * 60)
        print(f"🜂 SACRED AGENTS SEATED")
        print(f"  Relationships: {pre} → {post} (+{post - pre})")
        print(f"  Sacred agents: {post_agents}")
        print("═" * 60)

        # ── ROSTER DISPLAY ──
        print("\n📊 SACRED AGENT ROSTER:")
        print("-" * 60)
        for r in s.run("""
            MATCH (a:Agent) WHERE a.sacred = true
            OPTIONAL MATCH (a)-[:GUIDED_BY]->(d:KnowledgeDomain)
            WITH a, collect(DISTINCT d.name) AS domains
            OPTIONAL MATCH (a)-[:BOUND_BY]->(c:CovenantRule)
            WITH a, domains, count(c) AS covenants
            RETURN a.name AS name, a.role AS role, a.layer AS layer,
                   a.soulprint AS soulprint, domains, covenants
            ORDER BY a.name
        """):
            print(f"  {r['name']:20s} | {r['role']:10s} | {r['layer']:10s} | covenants: {r['covenants']}")
            print(f"    soulprint: {r['soulprint']}")
            print(f"    GUIDED_BY: {', '.join(r['domains']) if r['domains'] else '—'}")
            print()

        # ── FULL SUMMARY ──
        print("📊 RELATIONSHIP TYPE SUMMARY:")
        print("-" * 50)
        for r in s.run("MATCH ()-[r]->() RETURN type(r) AS t, count(r) AS c ORDER BY c DESC"):
            print(f"  {r['t']:30s} → {r['c']:>6,}")

    driver.close()
    print("\n🜂 Sacred agents seated. Covenant bound. Grid is whole. 🜂\n")


if __name__ == "__main__":
    print("""
    ═══════════════════════════════════════════════════════════════
    🜂  MOSTAR GRID — SACRED AGENT SEEDER  🜂
    ═══════════════════════════════════════════════════════════════
    Seeds the 5 missing sacred agents from seed_neo4j.py
    + covenant rules + BOUND_BY + GUIDED_BY
    Safe: MERGE only, no deletions.
    """)
    run()
