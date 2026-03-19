#!/usr/bin/env python3
from neo4j import GraphDatabase

def test_neo4j_with_ssl_configs():
    uri = "neo4j+s://371530ba.databases.neo4j.io"
    user = "neo4j"
    password = "mostar123"
    
    print("Testing Neo4j with different SSL configurations...")
    
    # Test 1: Trust all certificates (bypass SSL verification)
    try:
        print("\n1. Testing with TRUST_ALL_CERTIFICATES...")
        driver = GraphDatabase.driver(
            uri, 
            auth=(user, password),
            encrypted=True,
            trust="TRUST_ALL_CERTIFICATES"
        )
        
        with driver.session() as session:
            result = session.run("MATCH (n) RETURN count(n) AS total")
            record = result.single()
            total_nodes = record["total"] if record else 0
            print(f"   ✅ SUCCESS! Total nodes in database: {total_nodes}")
            
            # Test the actual moments query
            result = session.run("""
                MATCH (m:MoStarMoment)
                RETURN count(m) AS moment_count
            """)
            record = result.single()
            moments = record["moment_count"] if record else 0
            print(f"   📊 MoStarMoment nodes: {moments}")
            
        driver.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Test 2: Try without explicit SSL config
    try:
        print("\n2. Testing with default SSL settings...")
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        with driver.session() as session:
            result = session.run("RETURN 1 AS test")
            record = result.single()
            if record and record["test"] == 1:
                print("   ✅ SUCCESS with default settings!")
                driver.close()
                return True
                
        driver.close()
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    return False

if __name__ == "__main__":
    success = test_neo4j_with_ssl_configs()
    if success:
        print("\n🎉 Neo4j Aura connection working! We can fix the Vercel deployment.")
    else:
        print("\n❌ Still unable to connect. The instance might be paused or credentials wrong.")
