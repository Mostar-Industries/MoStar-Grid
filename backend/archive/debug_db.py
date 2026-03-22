import os
from neo4j import GraphDatabase

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "mostar123")

def debug():
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    try:
        with driver.session() as session:
            db_name = session.run("CALL dbms.showCurrentUser()").data()
            print(f"User: {db_name}")
            
            databases = session.run("SHOW DATABASES").data()
            print(f"Databases: {databases}")
            
            # Check default database specifically
            with driver.session(database="neo4j") as s2:
                count = s2.run("MATCH (n) RETURN count(n) AS c").single()["c"]
                print(f"Nodes in 'neo4j' db: {count}")
                
            with driver.session(database="system") as s3:
                count = s3.run("MATCH (n) RETURN count(n) AS c").single()["c"]
                print(f"Nodes in 'system' db: {count}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    debug()
