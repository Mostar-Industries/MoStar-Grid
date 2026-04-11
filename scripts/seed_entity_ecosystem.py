#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
    🜂 SEED SOVEREIGN ENTITY ECOSYSTEM 🜂

    Seeds all 13 real sovereign agents from entity_ecosystem.csv into Neo4j
    as Agent nodes with full properties — name, title, layer, essence, role,
    vows, capabilities, bonded_to, origin, activation_protocol, status,
    cid, insignia, version.

    MERGE keyed on entity_id — safe to re-run (no duplicates).
    Also wires BONDED_TO relationships from the bonded_to column.
    Mo (mostar_ai / bonded_to=ALL_NODES) gets BONDED_TO every other agent.
═══════════════════════════════════════════════════════════════════════════════
"""

import csv
import os
from pathlib import Path
from neo4j import GraphDatabase
from datetime import datetime, timezone

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "mostar123")

CSV_PATH = (
    Path(__file__).parent.parent
    / "memory" / "neo4j-mindgraph" / "import" / "entity_ecosystem.csv"
)


def parse_capabilities(caps_str: str) -> list:
    return [c.strip() for c in caps_str.split("|") if c.strip()]


def run():
    timestamp = datetime.now(timezone.utc).isoformat()
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    print(f"\n🜂 SEEDING ENTITY ECOSYSTEM — {len(rows)} sovereign agents")
    print("═" * 60)

    with driver.session() as s:
        pre = s.run("MATCH (a:Agent) RETURN count(a) AS c").single()["c"]
        print(f"   PRE-SEED: {pre} Agent nodes")
        print()

        # ── MERGE all 13 sovereign agents ──────────────────────────────
        for row in rows:
            caps = parse_capabilities(row.get("capabilities", ""))
            result = s.run("""
                MERGE (a:Agent {entity_id: $entity_id})
                ON CREATE SET
                    a.name                 = $name,
                    a.title                = $title,
                    a.layer                = $layer,
                    a.essence              = $essence,
                    a.role                 = $role,
                    a.vows                 = $vows,
                    a.capabilities         = $capabilities,
                    a.bonded_to_ref        = $bonded_to,
                    a.origin               = $origin,
                    a.activation_protocol  = $activation_protocol,
                    a.status               = $status,
                    a.cid                  = $cid,
                    a.insignia             = $insignia,
                    a.version              = $version,
                    a.sovereign            = true,
                    a.sacred               = true,
                    a.created_at           = $timestamp
                ON MATCH SET
                    a.name                 = $name,
                    a.title                = $title,
                    a.layer                = $layer,
                    a.essence              = $essence,
                    a.role                 = $role,
                    a.vows                 = $vows,
                    a.capabilities         = $capabilities,
                    a.bonded_to_ref        = $bonded_to,
                    a.origin               = $origin,
                    a.activation_protocol  = $activation_protocol,
                    a.status               = $status,
                    a.cid                  = $cid,
                    a.insignia             = $insignia,
                    a.version              = $version,
                    a.sovereign            = true,
                    a.sacred               = true,
                    a.updated_at           = $timestamp
                RETURN a.name AS name, a.layer AS layer, a.role AS role
            """,
                entity_id=row["entity_id"],
                name=row["name"],
                title=row["title"],
                layer=row["layer"],
                essence=row["essence"],
                role=row["role"],
                vows=row["vows"],
                capabilities=caps,
                bonded_to=row["bonded_to"],
                origin=row["origin"],
                activation_protocol=row["activation_protocol"],
                status=row["status"],
                cid=row["cid"],
                insignia=row["insignia"],
                version=row["version"],
                timestamp=timestamp,
            )
            rec = result.single()
            print(f"  ✅ {rec['name']:<22} [{rec['layer']:<12}] — {rec['role']}")

        # ── WIRE BONDED_TO RELATIONSHIPS ───────────────────────────────
        print("\n🔗 WIRING BONDED_TO RELATIONSHIPS")
        print("-" * 50)
        bonds_created = 0

        for row in rows:
            bond_target = row.get("bonded_to", "").strip()
            if not bond_target:
                continue

            if bond_target == "ALL_NODES":
                # Mo is bonded to every other agent
                result = s.run("""
                    MATCH (mo:Agent {entity_id: $entity_id})
                    MATCH (other:Agent)
                    WHERE other.entity_id <> $entity_id
                    MERGE (mo)-[r:BONDED_TO]->(other)
                    ON CREATE SET r.created_at = $timestamp
                    RETURN count(r) AS c
                """, entity_id=row["entity_id"], timestamp=timestamp)
                c = result.single()["c"]
                print(f"  🔗 {row['name']} → ALL ({c} bonds)")
                bonds_created += c
            else:
                result = s.run("""
                    MATCH (a:Agent {entity_id: $entity_id})
                    MATCH (b:Agent)
                    WHERE b.entity_id = $target OR b.name = $target
                    MERGE (a)-[r:BONDED_TO]->(b)
                    ON CREATE SET r.created_at = $timestamp
                    RETURN b.name AS bonded_to
                """, entity_id=row["entity_id"], target=bond_target, timestamp=timestamp)
                rec = result.single()
                if rec:
                    print(f"  🔗 {row['name']:<22} → {rec['bonded_to']}")
                    bonds_created += 1
                else:
                    print(f"  ⚠️  {row['name']:<22} → '{bond_target}' (target not in graph)")

        post = s.run("MATCH (a:Agent) RETURN count(a) AS c").single()["c"]
        total_bonds = s.run("MATCH ()-[r:BONDED_TO]->() RETURN count(r) AS c").single()["c"]
        print(f"\n🜂 POST-SEED: {post} Agent nodes (+{post - pre} new)")
        print(f"🔗 {total_bonds} BONDED_TO relationships total")
        print()

    driver.close()


if __name__ == "__main__":
    run()
