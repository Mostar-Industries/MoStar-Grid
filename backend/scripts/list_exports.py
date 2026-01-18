#!/usr/bin/env python3
"""List all APOC export procedures."""
from neo4j import GraphDatabase

driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'mostar123'))

with driver.session() as s:
    # List ALL export procedures
    exports = list(s.run("SHOW PROCEDURES YIELD name WHERE name CONTAINS 'export' RETURN name ORDER BY name"))
    print(f"Export Procedures ({len(exports)}):")
    for e in exports:
        print(f"  {e['name']}")
    
    # Also check for graphml specifically
    graphml = list(s.run("SHOW PROCEDURES YIELD name WHERE name CONTAINS 'graphml' RETURN name"))
    print(f"\nGraphML Procedures ({len(graphml)}):")
    for g in graphml:
        print(f"  {g['name']}")
    
    # Check JSON export
    json_procs = list(s.run("SHOW PROCEDURES YIELD name WHERE name CONTAINS 'json' AND name CONTAINS 'export' RETURN name"))
    print(f"\nJSON Export Procedures ({len(json_procs)}):")
    for j in json_procs:
        print(f"  {j['name']}")

driver.close()
