"""Fix Agent nodes with null IDs in Neo4j"""
import os
import uuid
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

uri = os.getenv('NEO4J_URI')
user = os.getenv('NEO4J_USER')
password = os.getenv('NEO4J_PASSWORD')

driver = GraphDatabase.driver(uri, auth=(user, password))

def inspect_agents():
    """Check what properties agents with null IDs have"""
    with driver.session() as session:
        # Get sample of agent properties
        result = session.run("""
            MATCH (a:Agent) WHERE a.id IS NULL 
            RETURN keys(a) AS props LIMIT 5
        """)
        print("Agent properties for nodes with null id:")
        for record in result:
            print(f"  {record['props']}")
        
        # Get sample agent names
        result = session.run("""
            MATCH (a:Agent) WHERE a.id IS NULL 
            RETURN a.name AS name LIMIT 10
        """)
        print("\nSample agent names:")
        for record in result:
            print(f"  {record['name']}")

def fix_null_ids():
    """Assign unique IDs to agents with null IDs"""
    with driver.session() as session:
        # Count agents needing fix
        result = session.run("MATCH (a:Agent) WHERE a.id IS NULL RETURN count(a) AS cnt")
        count = result.single()["cnt"]
        print(f"\nAgents with null ID: {count}")
        
        if count == 0:
            print("No agents need fixing!")
            return
        
        # Option 1: Use name + UUID suffix if name exists
        # Option 2: Generate fully random UUID
        result = session.run("""
            MATCH (a:Agent) WHERE a.id IS NULL
            WITH a, CASE 
                WHEN a.name IS NOT NULL THEN a.name + '_' + toString(id(a))
                ELSE 'agent_' + toString(id(a))
            END AS newId
            SET a.id = newId
            RETURN count(a) AS updated
        """)
        updated = result.single()["updated"]
        print(f"Updated {updated} agents with unique IDs")

def verify_fix():
    """Verify no more duplicate IDs"""
    with driver.session() as session:
        result = session.run("""
            MATCH (a:Agent)
            WITH a.id AS agentId, COLLECT(a) AS agents
            WHERE SIZE(agents) > 1
            RETURN agentId, SIZE(agents) AS count
        """)
        duplicates = list(result)
        if duplicates:
            print("\nRemaining duplicates:")
            for record in duplicates:
                print(f"  {record['agentId']}: {record['count']} nodes")
        else:
            print("\n✓ No duplicate agent IDs found!")

if __name__ == "__main__":
    print("=== Inspecting Agent Nodes ===")
    inspect_agents()
    
    print("\n=== Fixing Null IDs ===")
    response = input("Proceed with fixing null IDs? (y/n): ")
    if response.lower() == 'y':
        fix_null_ids()
        verify_fix()
    else:
        print("Skipped fixing.")
    
    driver.close()
