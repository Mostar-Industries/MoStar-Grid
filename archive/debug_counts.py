import os
from neo4j import GraphDatabase

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "mostar123")

def debug():
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    try:
        with driver.session() as session:
            count = session.run("MATCH (n) RETURN count(n) AS c").single()["c"]
            labels = session.run("CALL db.labels()").data()
            print(f"Total nodes: {count}")
            print(f"Labels: {labels}")
            
            # Check OduIfa
            odu_count = session.run("MATCH (n:OduIfa) RETURN count(n) AS c").single()["c"]
            print(f"OduIfa count: {odu_count}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    debug()
