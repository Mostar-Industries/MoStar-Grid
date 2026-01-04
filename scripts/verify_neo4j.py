"""Quick verification of Neo4j data"""
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv('NEO4J_URI'),
    auth=(os.getenv('NEO4J_USER'), os.getenv('NEO4J_PASSWORD'))
)

with driver.session() as session:
    # Check moments
    r = session.run('MATCH (m:MostarMoment) RETURN count(m) AS total, avg(m.resonance_score) AS avgRes')
    rec = r.single()
    print(f"MostarMoments: {rec['total']}, Avg Resonance: {rec['avgRes']:.4f}")
    
    # Check agents
    r = session.run('MATCH (a:Agent) RETURN a.status AS s, count(a) AS c, avg(a.manifestationStrength) AS str ORDER BY c DESC')
    print("\nAgents by Status:")
    for rec in r:
        print(f"  {rec['s']}: {rec['c']} (avg strength: {rec['str']:.2f})")
    
    # Sample agent
    r = session.run('MATCH (a:Agent) RETURN a LIMIT 1')
    agent = r.single()['a']
    print(f"\nSample Agent: {dict(agent)}")

driver.close()
