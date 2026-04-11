import os
from neo4j import GraphDatabase
import time

# Use the credentials provided by the user
URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "mostar123"

queries = [
    ("MATCH (n:IbibioWords) SET n:IbibioWord RETURN count(n) AS done", "IbibioWords"),
    ("MATCH (n:HealingPractices) SET n:HealingPractice RETURN count(n) AS done", "HealingPractices"),
    ("MATCH (n:Neo4jAgents) SET n:Agent RETURN count(n) AS done", "Neo4jAgents"),
    ("MATCH (n:MostarMoment) SET n:MoStarMoment RETURN count(n) AS done", "MostarMoment"),
    ("MATCH (n:IndigenousGovernance) SET n:Governance RETURN count(n) AS done", "IndigenousGovernance"),
    ("MATCH (n:EntityEcosystem) SET n:Entity RETURN count(n) AS done", "EntityEcosystem"),
    ("MATCH (n:Neo4jMetrics) SET n:Metric RETURN count(n) AS done", "Neo4jMetrics"),
    ("MATCH (n:Neo4jTasks) SET n:Task RETURN count(n) AS done", "Neo4jTasks"),
    ("MATCH (n:IbibioDictionaryEntry) SET n:IbibioEntry RETURN count(n) AS done", "IbibioDictionaryEntry")
]

def main():
    print(f"Connecting to {URI}...")
    try:
        driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
        with driver.session() as session:
            # Check for any data first
            count_res = session.run("MATCH (n) RETURN count(n) AS total").single()
            total = count_res["total"] if count_res else 0
            print(f"Total nodes in database: {total}")
            
            if total == 0:
                print("⚠️ Database appears empty. Please verify data ingestion.")
                return

            print("--- Executing Aliases ---")
            for q, label in queries:
                res = session.run(q).single()
                done = res["done"] if res else 0
                print(f"  {label}: {done}")
                time.sleep(6) # Paced execution to avoid lockout
                
            print("\n--- Final Counts ---")
            res = session.run("MATCH (n) UNWIND labels(n) AS lbl RETURN lbl, count(*) AS cnt ORDER BY cnt DESC").data()
            for r in res:
                print(f"  {r['lbl']}: {r['cnt']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'driver' in locals():
            driver.close()

if __name__ == "__main__":
    main()
