#!/usr/bin/env python3
"""Check APOC procedures in Neo4j."""
from neo4j import GraphDatabase

driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'mostar123'))

with driver.session() as s:
    # List ALL procedures that start with 'apoc'
    procs = list(s.run("SHOW PROCEDURES YIELD name WHERE name STARTS WITH 'apoc' RETURN name"))
    print(f"Total APOC Procedures loaded: {len(procs)}")
    
    if len(procs) > 0:
        print("\nFirst 20 APOC procedures:")
        for p in procs[:20]:
            print(f"  {p['name']}")
    else:
        print("\n❌ NO APOC PROCEDURES LOADED!")
        print("Check:")
        print("  1. apoc-*.jar is in plugins folder")
        print("  2. neo4j.conf has: dbms.security.procedures.allowlist=apoc.*")
        print("  3. APOC version matches Neo4j version")

    # Also check moment count
    count = s.run('MATCH (m:MoStarMoment) RETURN count(m) AS c').single()['c']
    print(f"\n📊 MoStarMoments in database: {count}")

driver.close()
