#!/usr/bin/env python3
from neo4j import GraphDatabase

def test_neo4j_aura():
    uri = "neo4j+s://371530ba.databases.neo4j.io"
    user = "neo4j" 
    password = "mostar123"
    
    print("Testing Neo4j Aura with correct configuration...")
    print(f"URI: {uri}")
    print(f"User: {user}")
    
    try:
        # For neo4j+s:// URIs, don't specify SSL config - it's built into the scheme
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        print("Driver created successfully, testing session...")
        
        with driver.session() as session:
            # Simple connectivity test
            result = session.run("RETURN 1 AS test")
            record = result.single()
            
            if record and record["test"] == 1:
                print("✅ Basic connection successful!")
                
                # Check total nodes
                result = session.run("MATCH (n) RETURN count(n) AS total")
                record = result.single()
                total = record["total"] if record else 0
                print(f"📊 Total nodes in database: {total}")
                
                # Check MoStarMoment nodes specifically
                result = session.run("MATCH (m:MoStarMoment) RETURN count(m) AS moments")
                record = result.single() 
                moments = record["moments"] if record else 0
                print(f"⭐ MoStarMoment nodes: {moments}")
                
                if moments > 0:
                    # Get a sample moment
                    result = session.run("MATCH (m:MoStarMoment) RETURN m LIMIT 1")
                    record = result.single()
                    if record:
                        moment = dict(record["m"])
                        print(f"📝 Sample moment keys: {list(moment.keys())}")
                
                driver.close()
                return True
            else:
                print("❌ Test query failed")
                
        driver.close()
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        
        # Check if it's an authentication vs connectivity issue
        if "unauthorized" in str(e).lower() or "authentication" in str(e).lower():
            print("🔐 This appears to be an authentication/credentials issue")
        elif "routing" in str(e).lower():
            print("🌐 This appears to be a network/routing issue - instance might be paused")
        
        return False

if __name__ == "__main__":
    success = test_neo4j_aura()
    
    if success:
        print("\n🎉 Neo4j Aura is working! The issue is resolved.")
        print("Next: Update Vercel Neo4j driver configuration if needed.")
    else:
        print("\n❌ Neo4j Aura connection still failing.")
        print("Possible solutions:")
        print("- Check if Neo4j Aura instance is paused (resume it)")
        print("- Verify password is still 'mostar123'")  
        print("- Check Neo4j Aura dashboard for instance status")
