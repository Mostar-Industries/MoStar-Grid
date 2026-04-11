#!/usr/bin/env python3
"""Clean bad PRECEDES, diagnose GUIDED_BY miss."""
import os
from neo4j import GraphDatabase

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "mostar123")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

with driver.session() as s:
    # ── STEP 1: Count before ──
    total = s.run("MATCH ()-[r]->() RETURN count(r) AS c").single()["c"]
    precedes = s.run("MATCH ()-[r:PRECEDES]->() RETURN count(r) AS c").single()["c"]
    print(f"BEFORE: {total} total rels, {precedes} PRECEDES")

    # ── STEP 2: Delete bad PRECEDES (keep Odú chain with chain='odu_sequence') ──
    result = s.run("""
        MATCH ()-[r:PRECEDES]->()
        WHERE r.chain <> 'odu_sequence'
        DELETE r
        RETURN count(r) AS deleted
    """)
    deleted = result.single()["deleted"]
    print(f"DELETED: {deleted} bad PRECEDES edges")

    remaining = s.run("MATCH ()-[r:PRECEDES]->() RETURN count(r) AS c").single()["c"]
    total2 = s.run("MATCH ()-[r]->() RETURN count(r) AS c").single()["c"]
    print(f"AFTER: {total2} total rels, {remaining} PRECEDES remaining (Odú chain)")

    # ── STEP 3: Diagnose Agent nodes ──
    print("\n── AGENT NODES ──")
    agents = s.run("MATCH (a:Agent) RETURN a.name AS name, a.id AS id, keys(a) AS props LIMIT 10")
    agent_count = 0
    for r in agents:
        agent_count += 1
        print(f"  name={r['name']}, id={r['id']}, props={r['props']}")
    if agent_count == 0:
        print("  ** NO Agent NODES FOUND **")
        # Try Entity label
        print("\n  Trying Entity label instead...")
        entities = s.run("MATCH (e:Entity) RETURN e.name AS name, e.id AS id, labels(e) AS labels, keys(e) AS props LIMIT 10")
        for r in entities:
            print(f"  name={r['name']}, id={r['id']}, labels={r['labels']}, props={r['props']}")

    # ── STEP 4: Diagnose KnowledgeDomain nodes ──
    print("\n── KNOWLEDGE DOMAIN NODES ──")
    domains = s.run("MATCH (k:KnowledgeDomain) RETURN k.name AS name, k.id AS id, keys(k) AS props LIMIT 10")
    domain_count = 0
    for r in domains:
        domain_count += 1
        print(f"  name={r['name']}, id={r['id']}, props={r['props']}")
    if domain_count == 0:
        print("  ** NO KnowledgeDomain NODES FOUND **")

    # ── STEP 5: Show all labels in graph ──
    print("\n── ALL NODE LABELS (with counts) ──")
    labels = s.run("MATCH (n) RETURN labels(n) AS lbl, count(n) AS cnt ORDER BY cnt DESC")
    for r in labels:
        print(f"  {str(r['lbl']):50s} → {r['cnt']:>6,}")

    # ── STEP 6: Lifecycle stage sample ──
    print("\n── LIFECYCLE STAGE SAMPLE (id field check) ──")
    for label in ["Infancy", "Childhood", "Adolescence", "Adulthood"]:
        sample = s.run(f"MATCH (n:{label}) RETURN n.id AS id, keys(n) AS props LIMIT 2")
        records = list(sample)
        if records:
            print(f"  {label}: id={records[0]['id']}, props={records[0]['props']}")
        else:
            print(f"  {label}: ** NONE **")

driver.close()
print("\nDone.")
