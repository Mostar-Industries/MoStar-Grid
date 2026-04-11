"""Fix null agent IDs and verify connection"""
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

uri = os.getenv('NEO4J_URI')
user = os.getenv('NEO4J_USER')
password = os.getenv('NEO4J_PASSWORD')

print(f"Connecting to: {uri}")

driver = GraphDatabase.driver(uri, auth=(user, password))

with driver.session() as session:
    # Fix null IDs
    result = session.run("""
        MATCH (a:Agent) WHERE a.id IS NULL
        WITH a, coalesce(a.name, 'agent') + '_' + toString(id(a)) AS newId
        SET a.id = newId
        RETURN count(a) AS fixed
    """)
    print(f"Fixed agents with null ID: {result.single()['fixed']}")
    
    # Verify
    result = session.run("""
        MATCH (a:Agent)
        WITH a.id AS aid, count(a) AS c
        WHERE c > 1 OR aid IS NULL
        RETURN aid, c
    """)
    dups = list(result)
    print(f"Duplicates/nulls remaining: {len(dups)}")
    
    # Check for MoStarMoment (with capital S)
    result = session.run("MATCH (m:MoStarMoment) RETURN count(m) AS cnt")
    print(f"MoStarMoments: {result.single()['cnt']}")
    
    # Check for MostarMoment (lowercase s)
    result = session.run("MATCH (m:MostarMoment) RETURN count(m) AS cnt")
    print(f"MostarMoments: {result.single()['cnt']}")

driver.close()
print("Done!")
