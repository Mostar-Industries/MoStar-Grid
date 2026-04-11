import os
from neo4j import GraphDatabase

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "mostar123")

def main():
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    with driver.session() as session:
        # Total
        total = session.run("MATCH (n) RETURN count(n)").single()[0]
        print(f"Total nodes: {total}")
        
        # Labels and counts
        res = session.run("MATCH (n) UNWIND labels(n) AS label RETURN label, count(n) AS count").data()
        print("Labels and counts:")
        for r in res:
            print(f"  {r['label']}: {r['count']}")
            
        # Specific labels the user mentioned
        to_check = ["IbibioWords", "HealingPractices", "Neo4jAgents", "Neo4jMetrics", "Culture"]
        for lbl in to_check:
            count = session.run(f"MATCH (n:{lbl}) RETURN count(n)").single()[0]
            print(f"  {lbl}: {count}")

    driver.close()

if __name__ == "__main__":
    main()
