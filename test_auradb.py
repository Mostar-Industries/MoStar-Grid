#!/usr/bin/env python3
"""
Test AuraDB connection for MoStar Grid deployment
"""

import os

from neo4j import GraphDatabase, TrustAll


def test_auradb():
    # Test AuraDB connection
    uri = "neo4j+s://371530ba.databases.neo4j.io"
    user = "neo4j"
    password = "mostar123"

    print(f"Testing AuraDB connection to: {uri}")
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            record = result.single()
            print(f"✅ AuraDB connection successful: {record['test']}")

            # Check if database has any data
            count_result = session.run("MATCH (n) RETURN count(n) as node_count")
            node_count = count_result.single()["node_count"]
            print(f"📊 Current nodes in AuraDB: {node_count}")

            if node_count == 0:
                print("🆕 AuraDB is empty - ready for fresh Grid deployment")
            else:
                print("⚠️  AuraDB has existing data - will append to current schema")

    except Exception as e:
        print(f"❌ AuraDB connection failed: {e}")
        print(f"🔍 Debug info - URI: {uri}, User: {user}")
        if "routing" in str(e).lower():
            print(
                "💡 This often means: wrong password, instance not running, or network blocked"
            )
    finally:
        if "driver" in locals():
            driver.close()


if __name__ == "__main__":
    test_auradb()
