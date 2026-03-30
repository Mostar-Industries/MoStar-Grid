#!/usr/bin/env python3
from neo4j import GraphDatabase

def test_passwords():
    uri = "neo4j+s://371530ba.databases.neo4j.io"
    user = "neo4j"
    
    # Common password variations
    passwords = [
        "mostar123",
        "MoStar123",
        "mostar",
        "password",
        "neo4j",
        "123456",
        "admin",
        "mostar_grid",
        "grid123"
    ]
    
    print("Testing Neo4j password variations...")
    print(f"Instance: {uri}")
    
    for i, password in enumerate(passwords, 1):
        try:
            print(f"\n{i}. Testing password: {'*' * len(password)}")
            
            driver = GraphDatabase.driver(uri, auth=(user, password))
            with driver.session() as session:
                result = session.run("RETURN 1 AS test")
                record = result.single()
                
                if record and record["test"] == 1:
                    print(f"   ✅ SUCCESS! Password found: {password}")
                    
                    # Get node counts
                    result = session.run("MATCH (n) RETURN count(n) AS total")
                    total = result.single()["total"]
                    
                    result = session.run("MATCH (m:MoStarMoment) RETURN count(m) AS moments")
                    moments = result.single()["moments"] 
                    
                    print(f"   📊 Total nodes: {total}")
                    print(f"   ⭐ MoStarMoments: {moments}")
                    
                    driver.close()
                    return password
                    
            driver.close()
            
        except Exception as e:
            error_msg = str(e)
            if "unauthorized" in error_msg.lower():
                print(f"   ❌ Unauthorized")
            elif "routing" in error_msg.lower():
                print(f"   ❌ Network/routing issue")
            else:
                print(f"   ❌ Error: {error_msg[:50]}")
    
    return None

if __name__ == "__main__":
    correct_password = test_passwords()
    
    if correct_password:
        print(f"\n🎉 Found working password: {correct_password}")
        print("Next: Update Vercel env var with correct password")
    else:
        print("\n❌ None of the tested passwords worked.")
        print("You may need to:")
        print("- Check Neo4j Console for actual password")
        print("- Reset password in Neo4j Console")
        print("- Verify the username (might not be 'neo4j')")
