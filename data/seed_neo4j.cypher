// 🌍 MoStar Grid Genesis Seed
// This Cypher file initializes the base ontology in Neo4j

CREATE (s:Layer {name: "Soul", role: "Essence"})
CREATE (m:Layer {name: "Mind", role: "Reason"})
CREATE (b:Layer {name: "Body", role: "Execution"})
CREATE (g:Layer {name: "Graph", role: "Memory"})

CREATE (s)-[:BINDS_TO]->(m)
CREATE (m)-[:GUIDES]->(b)
CREATE (b)-[:REPORTS_TO]->(g)
CREATE (g)-[:REFLECTS]->(s)

CREATE (c:Covenant {
    id: "QSEAL_INIT",
    version: "1.0.0",
    purpose: "Protect, Collate, Analyze, Visualize, Execute"
})

CREATE (s)-[:PROTECTS]->(c)
CREATE (m)-[:INTERPRETS]->(c)
CREATE (b)-[:EXECUTES]->(c)
CREATE (g)-[:RECORDS]->(c)

RETURN s, m, b, g, c
