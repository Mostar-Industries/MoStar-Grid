# Create a quick Neo4j test script
from neo4j import GraphDatabase
import os

# Your Neo4j credentials
uri = "neo4j+s://1d55c1d3.databases.neo4j.io"
user = "neo4j"
password = "x5_aynxf3mKWxHIMOL3c7Rkjdtt2reYDhhkL4gJ3kO4"  # Replace with actual password

print("🔥 Testing Neo4j Soul Connection...")

try:
    driver = GraphDatabase.driver(uri, auth=(user, password))
    driver.verify_connectivity()
    print("✅ Soul (Neo4j) is ALIVE!")
    
    # Quick stats
    with driver.session() as session:
        # Total nodes
        result = session.run("MATCH (n) RETURN count(n) as total")
        total = result.single()["total"]
        print(f"📊 Total nodes in Grid: {total:,}")
        
        # Check for African Flame
        result = session.run("""
            MATCH (flame:AfricanFlame {id: 'african_flame_master'})
            RETURN flame.name as name, flame.essence as essence
        """)
        record = result.single()
        if record:
            print(f"🔥 African Flame exists: {record['name']}")
            print(f"   Essence: {record['essence']}")
        else:
            print("⚠️  African Flame node not found")
        
        # Check for MoStar Moments
        result = session.run("MATCH (m:MoStarMoment) RETURN count(m) as moments")
        moments = result.single()["moments"]
        print(f"🌍 MoStar Moments logged: {moments}")
        
        # Check for Ifá Kernels
        result = session.run("MATCH (i:IfaReasoningKernel) RETURN count(i) as kernels")
        kernels = result.single()["kernels"]
        print(f"🔮 Ifá Reasoning Kernels: {kernels}")
        
        # Check for Verdicts
        result = session.run("MATCH (v:Verdict) RETURN count(v) as verdicts")
        verdicts = result.single()["verdicts"]
        print(f"⚖️  Verdicts stored: {verdicts}")
    
    driver.close()
    print("\n✅ Neo4j Soul is fully operational!")
    
except Exception as e:
    print(f"❌ Soul connection failed: {e}")
    print("   Check your Neo4j password in the script!")

# Show the file so you can add your password (this line is a comment and not executable Python code)
# cat test_neo4j.py