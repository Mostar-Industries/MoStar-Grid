import os
import time
from neo4j import GraphDatabase

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "mostar123")

def run_query(session, query, description):
    print(f"Executing: {description}...")
    try:
        start = time.time()
        result = session.run(query).single()
        duration = time.time() - start
        count = result["labeled"] if result and "labeled" in result else "N/A"
        print(f"  Result: {count} nodes updated in {duration:.2f}s")
        return count
    except Exception as e:
        print(f"  Error: {e}")
        return None

def main():
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD), connection_timeout=60)
    
    aliasing_queries = [
        ("MATCH (n:IbibioWords) SET n:IbibioWord RETURN count(n) AS labeled", "IbibioWords -> IbibioWord"),
        ("MATCH (n:HealingPractices) SET n:HealingPractice RETURN count(n) AS labeled", "HealingPractices -> HealingPractice"),
        ("MATCH (n:Neo4jAgents) SET n:Agent RETURN count(n) AS labeled", "Neo4jAgents -> Agent"),
        ("MATCH (n:MostarMoment) SET n:MoStarMoment RETURN count(n) AS labeled", "MostarMoment -> MoStarMoment"),
        ("MATCH (n:IndigenousGovernance) SET n:Governance RETURN count(n) AS labeled", "IndigenousGovernance -> Governance"),
        ("MATCH (n:EntityEcosystem) SET n:Entity RETURN count(n) AS labeled", "EntityEcosystem -> Entity"),
        ("MATCH (n:Neo4jMetrics) SET n:Metric RETURN count(n) AS labeled", "Neo4jMetrics -> Metric (60k)"),
        ("MATCH (n:Neo4jTasks) SET n:Task RETURN count(n) AS labeled", "Neo4jTasks -> Task"),
        ("MATCH (n:IbibioDictionaryEntry) SET n:IbibioEntry RETURN count(n) AS labeled", "IbibioDictionaryEntry -> IbibioEntry")
    ]

    verification_queries = [
        "MATCH (n:IbibioWord) RETURN count(n) AS count",
        "MATCH (n:Agent) RETURN count(n) AS count",
        "MATCH (n:HealingPractice) RETURN count(n) AS count",
        "MATCH (n:Governance) RETURN count(n) AS count",
        "MATCH (n:Metric) RETURN count(n) AS count"
    ]

    inspect_queries = [
        ("MATCH (n:Neo4jMetrics) RETURN keys(n) LIMIT 1", "Neo4jMetrics Keys"),
        ("MATCH (n:Neo4jTasks) RETURN keys(n) LIMIT 1", "Neo4jTasks Keys")
    ]

    try:
        with driver.session() as session:
            print("--- ALIASING PHASES ---")
            for q, desc in aliasing_queries:
                run_query(session, q, desc)
            
            print("\n--- VERIFICATION PHASES ---")
            for q in verification_queries:
                label = q.split(":")[1].split(")")[0]
                res = session.run(q).single()
                print(f"  {label}: {res['count']}")

            print("\n--- SCHEMA INSPECTION ---")
            for q, desc in inspect_queries:
                res = session.run(q).data()
                keys = res[0]["keys(n)"] if res else "No data"
                print(f"  {desc}: {keys}")

    finally:
        driver.close()

if __name__ == "__main__":
    main()
