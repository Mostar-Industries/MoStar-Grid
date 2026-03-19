#!/usr/bin/env python3
from neo4j import GraphDatabase
import os

uri = "neo4j+s://371530ba.databases.neo4j.io"
user = "neo4j"
password = "mostar123"

print(f"Testing Neo4j Aura connection...")
print(f"URI: {uri}")
print(f"User: {user}")

try:
    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as session:
        result = session.run("RETURN 'Connected!' AS message")
        for record in result:
            print(f"✅ {record['message']}")
    driver.close()
except Exception as e:
    print(f"❌ Error: {e}")
