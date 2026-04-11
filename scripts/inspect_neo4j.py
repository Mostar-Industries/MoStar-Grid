"""Inspect Neo4j Agent data structure"""
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv('NEO4J_URI'),
    auth=(os.getenv('NEO4J_USER'), os.getenv('NEO4J_PASSWORD'))
)

with driver.session() as session:
    # Check agent properties
    result = session.run("""
        MATCH (a:Agent) 
        RETURN keys(a) AS props, 
               a.status AS status, 
               a.manifestationStrength AS strength,
               a.capabilities AS caps
        LIMIT 5
    """)
    print("=== Agent Properties ===")
    for rec in result:
        print(f"  Props: {rec['props']}")
        print(f"  Status: {rec['status']}, Strength: {rec['strength']}, Caps: {rec['caps']}")
        print()

    # Check MostarMoment properties
    result = session.run("""
        MATCH (m:MostarMoment)
        RETURN count(m) AS total, avg(m.resonance_score) AS avgRes
    """)
    rec = result.single()
    print(f"=== MostarMoments ===")
    print(f"  Total: {rec['total']}, Avg Resonance: {rec['avgRes']}")

    # Check distinct statuses
    result = session.run("""
        MATCH (a:Agent)
        RETURN DISTINCT a.status AS status, count(a) AS cnt
        ORDER BY cnt DESC
    """)
    print("\n=== Agent Status Distribution ===")
    for rec in result:
        print(f"  {rec['status']}: {rec['cnt']}")

driver.close()
