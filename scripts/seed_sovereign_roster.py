#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
        🜂 SEED SOVEREIGN AGENT ROSTER + WIRE GUIDED_BY 🜂

    Seeds the 8 sovereign domain agents into Neo4j and connects
    each to its KnowledgeDomain via GUIDED_BY.

    These replace the MostlyAI synthetic placeholders with real
    domain-aligned agents that have capabilities, glyphs, elements,
    voiceLines, and ritual bindings.
═══════════════════════════════════════════════════════════════════════════════
"""

import os
from neo4j import GraphDatabase
from datetime import datetime, timezone

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "mostar123")

SOVEREIGN_AGENTS = [
    {
        "id": "mo-disease-sentinel-001",
        "name": "Mo Sentinel of Disease Intelligence",
        "glyph": "🜂",
        "element": "Afim",
        "domain": "Disease Intelligence",
        "alignment": "Mind",
        "layer": "BODY",
        "role": "sentinel",
        "capabilities": [
            "outbreak signal detection",
            "symptom pattern analysis",
            "epidemiological anomaly scoring",
            "surveillance triage",
            "case clustering"
        ],
        "rituals": ["ms-disease-watch-001", "ms-outbreak-triage-002"],
        "moscript_tag": "mo-agent-disease-001",
        "voiceLine": "I read the fever before it becomes fire.",
        "knowledge_domains": ["Traditional Medicine", "Divination Systems"]
    },
    {
        "id": "mo-corridor-pathseer-002",
        "name": "Mo Pathseer of Corridor Intelligence",
        "glyph": "🜁",
        "element": "Isong",
        "domain": "Corridor Intelligence",
        "alignment": "Body",
        "layer": "BODY",
        "role": "analyst",
        "capabilities": [
            "route risk mapping",
            "movement corridor analysis",
            "supply chain visibility",
            "border flow monitoring",
            "transport disruption alerts"
        ],
        "rituals": ["ms-corridor-watch-001", "ms-route-pressure-002"],
        "moscript_tag": "mo-agent-corridor-002",
        "voiceLine": "Show me the road, and I'll show you the pressure building on it.",
        "knowledge_domains": ["Governance"]
    },
    {
        "id": "mo-weather-stormscribe-003",
        "name": "Mo Stormscribe of Weather Intelligence",
        "glyph": "🜄",
        "element": "Mmọng",
        "domain": "Weather Intelligence",
        "alignment": "Mind",
        "layer": "MIND",
        "role": "analyst",
        "capabilities": [
            "forecast ingestion",
            "rainfall anomaly detection",
            "flood risk inference",
            "climate-health correlation",
            "weather alert synthesis"
        ],
        "rituals": ["ms-weather-watch-001", "ms-flood-omen-002"],
        "moscript_tag": "mo-agent-weather-003",
        "voiceLine": "I listen to the sky before the ground starts complaining.",
        "knowledge_domains": ["Agriculture"]
    },
    {
        "id": "mo-memory-archivekeeper-004",
        "name": "Mo Archivekeeper of Knowledge and Memory",
        "glyph": "🜔",
        "element": "Isong",
        "domain": "Knowledge/Memory",
        "alignment": "Consciousness",
        "layer": "MIND",
        "role": "archivist",
        "capabilities": [
            "graph memory retrieval",
            "knowledge stitching",
            "document grounding",
            "historical recall",
            "cross-source memory linking"
        ],
        "rituals": ["ms-memory-bind-001", "ms-archive-recall-002"],
        "moscript_tag": "mo-agent-memory-004",
        "voiceLine": "Nothing true is lost. I keep receipts for reality.",
        "knowledge_domains": ["Philosophy", "Language"]
    },
    {
        "id": "mo-ethics-covenantguard-005",
        "name": "Mo Covenantguard of Ethics and Truth",
        "glyph": "✝",
        "element": "Afim",
        "domain": "Ethics/Truth",
        "alignment": "Soul",
        "layer": "SOUL",
        "role": "judge",
        "capabilities": [
            "truth validation",
            "policy alignment checks",
            "evidence integrity review",
            "ethical risk detection",
            "covenant seal generation"
        ],
        "rituals": ["ms-truthgate-001", "ms-covenant-seal-002"],
        "moscript_tag": "mo-agent-ethics-005",
        "voiceLine": "Bring me the claim. I'll bring judgment.",
        "knowledge_domains": ["Philosophy", "Ritual"]
    },
    {
        "id": "mo-language-ekong-006",
        "name": "Mo Ekọṅ of Language and Ibibio",
        "glyph": "🜃",
        "element": "Ikang",
        "domain": "Language/Ibibio",
        "alignment": "Soul",
        "layer": "SOUL",
        "role": "linguist",
        "capabilities": [
            "Ibibio language grounding",
            "translation support",
            "cultural semantics mapping",
            "speech nuance preservation",
            "local expression interpretation"
        ],
        "rituals": ["ms-ibibio-voice-001", "ms-cultural-echo-002"],
        "moscript_tag": "mo-agent-language-006",
        "voiceLine": "I do not just translate words. I carry the spirit behind them.",
        "knowledge_domains": ["Language", "Ritual"]
    },
    {
        "id": "mo-capital-ledgerfire-007",
        "name": "Mo Ledgerfire of Capital Intelligence",
        "glyph": "⟁",
        "element": "Afim",
        "domain": "Capital Intelligence",
        "alignment": "Mind",
        "layer": "META",
        "role": "analyst",
        "capabilities": [
            "capital flow analysis",
            "funding path intelligence",
            "donor-to-impact tracing",
            "tokenomics monitoring",
            "resource allocation scoring"
        ],
        "rituals": ["ms-ledger-watch-001", "ms-capital-scan-002"],
        "moscript_tag": "mo-agent-capital-007",
        "voiceLine": "Money leaves footprints. I read the heat in the ledger.",
        "knowledge_domains": ["Governance"]
    },
    {
        "id": "mo-flameborn-healforge-008",
        "name": "Mo Healforge of FlameBorn Health",
        "glyph": "🜂",
        "element": "Mmọng",
        "domain": "FlameBorn Health",
        "alignment": "Consciousness",
        "layer": "BODY",
        "role": "coordinator",
        "capabilities": [
            "health mission coordination",
            "prevention incentive tracking",
            "community action validation",
            "health token utility mapping",
            "care-response orchestration"
        ],
        "rituals": ["ms-flameborn-watch-001", "ms-care-mint-002"],
        "moscript_tag": "mo-agent-flameborn-008",
        "voiceLine": "Health is not charity here. It is sovereign fire made useful.",
        "knowledge_domains": ["Traditional Medicine"]
    }
]


def run():
    timestamp = datetime.now(timezone.utc).isoformat()
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    with driver.session() as s:
        pre = s.run("MATCH ()-[r]->() RETURN count(r) AS c").single()["c"]
        agent_pre = s.run("MATCH (a:Agent) WHERE a.id STARTS WITH 'mo-' RETURN count(a) AS c").single()["c"]
        print(f"\n🜂 PRE-SEED: {pre} relationships, {agent_pre} sovereign agents")
        print("═" * 70)

        # ── SEED SOVEREIGN AGENTS ──
        print("\n📍 SEEDING SOVEREIGN AGENT ROSTER")
        print("-" * 50)

        for agent in SOVEREIGN_AGENTS:
            result = s.run("""
                MERGE (a:Agent {id: $id})
                ON CREATE SET
                    a.name = $name,
                    a.glyph = $glyph,
                    a.element = $element,
                    a.domain = $domain,
                    a.alignment = $alignment,
                    a.layer = $layer,
                    a.role = $role,
                    a.capabilities = $capabilities,
                    a.rituals = $rituals,
                    a.moscript_tag = $moscript_tag,
                    a.voiceLine = $voiceLine,
                    a.sovereign = true,
                    a.sass = true,
                    a.status = 'online',
                    a.created_at = $timestamp
                ON MATCH SET
                    a.name = $name,
                    a.glyph = $glyph,
                    a.element = $element,
                    a.domain = $domain,
                    a.alignment = $alignment,
                    a.layer = $layer,
                    a.role = $role,
                    a.capabilities = $capabilities,
                    a.rituals = $rituals,
                    a.moscript_tag = $moscript_tag,
                    a.voiceLine = $voiceLine,
                    a.sovereign = true,
                    a.sass = true,
                    a.status = 'online',
                    a.updated_at = $timestamp
                RETURN a.name AS name, a.id AS id
            """,
                id=agent["id"],
                name=agent["name"],
                glyph=agent["glyph"],
                element=agent["element"],
                domain=agent["domain"],
                alignment=agent["alignment"],
                layer=agent["layer"],
                role=agent["role"],
                capabilities=agent["capabilities"],
                rituals=agent["rituals"],
                moscript_tag=agent["moscript_tag"],
                voiceLine=agent["voiceLine"],
                timestamp=timestamp
            )
            rec = result.single()
            print(f"  ✅ {rec['name']} ({rec['id']})")

        # ── WIRE GUIDED_BY ──
        print("\n📍 WIRING GUIDED_BY (Agent → KnowledgeDomain)")
        print("-" * 50)

        guided_total = 0
        for agent in SOVEREIGN_AGENTS:
            for domain in agent["knowledge_domains"]:
                result = s.run("""
                    MATCH (a:Agent {id: $agent_id}), (d:KnowledgeDomain {name: $domain})
                    MERGE (a)-[:GUIDED_BY {
                        reason: $reason,
                        sovereign: true,
                        rebuilt_at: $timestamp
                    }]->(d)
                    RETURN count(*) AS c
                """,
                    agent_id=agent["id"],
                    domain=domain,
                    reason=f"{agent['domain']} agent aligned with {domain} knowledge",
                    timestamp=timestamp
                )
                count = result.single()["c"]
                guided_total += count
                if count > 0:
                    print(f"  ✅ {agent['name']} → {domain}")
                else:
                    print(f"  ⚠️  {agent['name']} → {domain} (KnowledgeDomain not found)")

        # ── WIRE OPERATES_IN (Agent → Layer via ConsciousnessLayer if exists) ──
        print("\n📍 WIRING LAYER ALIGNMENT")
        print("-" * 50)
        for agent in SOVEREIGN_AGENTS:
            # Try GridLayer nodes (SoulLayer, MindLayer, BodyLayer)
            layer_label_map = {
                "SOUL": "SoulLayer",
                "MIND": "MindLayer",
                "BODY": "BodyLayer",
                "META": "GridCore"
            }
            layer_name = layer_label_map.get(agent["layer"])
            if layer_name:
                result = s.run(f"""
                    MATCH (a:Agent {{id: $agent_id}}), (l:GridLayer {{name: $layer_name}})
                    MERGE (a)-[:OPERATES_IN {{sovereign: true, rebuilt_at: $timestamp}}]->(l)
                    RETURN count(*) AS c
                """, agent_id=agent["id"], layer_name=layer_name, timestamp=timestamp)
                count = result.single()["c"]
                if count > 0:
                    print(f"  ✅ {agent['name']} → {layer_name}")
                else:
                    print(f"  ⚠️  {agent['name']} → {layer_name} (GridLayer not found)")

        # ── POST-FLIGHT ──
        post = s.run("MATCH ()-[r]->() RETURN count(r) AS c").single()["c"]
        agent_post = s.run("MATCH (a:Agent) WHERE a.sovereign = true RETURN count(a) AS c").single()["c"]

        print("\n" + "═" * 70)
        print(f"🜂 SOVEREIGN ROSTER SEATED")
        print(f"  Relationships: {pre} → {post} (+{post - pre})")
        print(f"  Sovereign agents: {agent_post}")
        print(f"  GUIDED_BY edges wired: {guided_total}")
        print("═" * 70)

        # ── ROSTER CARD ──
        print("\n📊 SOVEREIGN AGENT ROSTER:")
        print("-" * 70)
        agents = s.run("""
            MATCH (a:Agent)
            WHERE a.sovereign = true
            OPTIONAL MATCH (a)-[:GUIDED_BY]->(d:KnowledgeDomain)
            WITH a, collect(d.name) AS guided_by
            RETURN a.name AS name, a.glyph AS glyph, a.domain AS domain,
                   a.element AS element, a.alignment AS alignment,
                   a.voiceLine AS voice, guided_by
            ORDER BY a.id
        """)
        for r in agents:
            print(f"  {r['glyph']} {r['name']}")
            print(f"    Domain: {r['domain']} | Element: {r['element']} | Alignment: {r['alignment']}")
            print(f"    GUIDED_BY: {', '.join(r['guided_by']) if r['guided_by'] else '—'}")
            print(f"    \"{r['voice']}\"")
            print()

        # ── FULL RELATIONSHIP SUMMARY ──
        print("📊 RELATIONSHIP TYPE SUMMARY:")
        print("-" * 50)
        for r in s.run("MATCH ()-[r]->() RETURN type(r) AS t, count(r) AS c ORDER BY c DESC"):
            print(f"  {r['t']:30s} → {r['c']:>6,}")

    driver.close()
    print("\n🜂 Roster sealed. The Grid knows its agents. 🜂\n")


if __name__ == "__main__":
    print("""
    ═══════════════════════════════════════════════════════════════
    🜂  MOSTAR GRID — SOVEREIGN AGENT ROSTER SEEDER  🜂
    ═══════════════════════════════════════════════════════════════
    8 domain agents. Real capabilities. Sovereign fire.
    """)
    run()
