from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "mostar123"))

with driver.session() as s:
    print("----------")
    print("2️⃣ Covenant Kernel Verification")
    ret2 = s.run("MATCH (c:CovenantKernel {id:'covenant-kernel-001'}) RETURN c").data()
    for row in ret2:
        print(row)
        
    print("----------")
    print("3️⃣ Executor Identity Provenance")
    ret3 = s.run("MATCH (m:MoStarMoment) WHERE m.processedBy IS NOT NULL RETURN m.processedBy, m.processedAt LIMIT 5").data()
    for row in ret3:
        print(row)

driver.close()
