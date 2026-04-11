import os
import json
from neo4j import GraphDatabase

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "mostar123")

queries = [
    # --- PHASE 1: MOSTAR GRID - EXPANDED CODE MODULES ---
    """
    MERGE (m:CodeModule {id: "py_021"})
    SET m.filename = "cultural_engine.py",
        m.layer = "Soul",
        m.owner = "Flameborn",
        m.role = "African Cultural Knowledge Processor",
        m.security_level = "High",
        m.status = "ACTIVE";
    """,
    """
    MERGE (m:CodeModule {id: "py_022"})
    SET m.filename = "council_engine.py",
        m.layer = "Mind",
        m.owner = "TsaTse Fly",
        m.role = "Governance Council Simulation",
        m.security_level = "Medium",
        m.status = "ACTIVE";
    """,
    """
    MERGE (m:CodeModule {id: "py_023"})
    SET m.filename = "proverb_compiler.py",
        m.layer = "Soul",
        m.owner = "Flameborn",
        m.role = "African Proverb Compilation and Indexing",
        m.security_level = "High",
        m.status = "ACTIVE";
    """,
    """
    MERGE (m:CodeModule {id: "py_024"})
    SET m.filename = "resonance_score.py",
        m.layer = "Mind",
        m.owner = "Sigma",
        m.role = "System Resonance and Coherence Scoring",
        m.security_level = "Medium",
        m.status = "ACTIVE";
    """,
    """
    MERGE (m:CodeModule {id: "py_025"})
    SET m.filename = "divine_interface.py",
        m.layer = "Soul",
        m.owner = "Mo",
        m.role = "Sacred Logic Interface Layer",
        m.security_level = "High",
        m.status = "ACTIVE";
    """,
    """
    MERGE (m:CodeModule {id: "py_026"})
    SET m.filename = "audit_script.py",
        m.layer = "Body",
        m.owner = "Sigma",
        m.role = "System Audit and Integrity Verification",
        m.security_level = "Medium",
        m.status = "ACTIVE";
    """,
    """
    MERGE (m:CodeModule {id: "py_027"})
    SET m.filename = "covenant_keys.py",
        m.layer = "Body",
        m.owner = "Code Conduit",
        m.role = "Covenant Key Management and Encryption",
        m.security_level = "Medium",
        m.status = "ACTIVE";
    """,
    """
    MERGE (m:CodeModule {id: "py_028"})
    SET m.filename = "streamlit_ui_layout.py",
        m.layer = "Body",
        m.owner = "Mo",
        m.role = "Dashboard UI Layout Engine",
        m.security_level = "Medium",
        m.status = "ACTIVE";
    """,
    """
    MERGE (m:CodeModule {id: "py_029"})
    SET m.filename = "test_protocol.py",
        m.layer = "Body",
        m.owner = "Sigma",
        m.role = "Protocol Testing Framework",
        m.security_level = "Medium",
        m.status = "ACTIVE";
    """,
    """
    MERGE (m:CodeModule {id: "py_030"})
    SET m.filename = "moshock_integration.py",
        m.layer = "Body",
        m.owner = "RAD-X-FLB",
        m.role = "Emergency Response Integration",
        m.security_level = "Medium",
        m.status = "ACTIVE";
    """,
    """
    MERGE (m:CodeModule {id: "py_031"})
    SET m.filename = "poot_token.py",
        m.layer = "Body",
        m.owner = "Flameborn",
        m.role = "Token Generation and Distribution",
        m.security_level = "Medium",
        m.status = "ACTIVE";
    """,
    """
    MERGE (m:CodeModule {id: "py_032"})
    SET m.filename = "resonance_guard.py",
        m.layer = "Body",
        m.owner = "Sigma",
        m.role = "Resonance Integrity Guardian",
        m.security_level = "Medium",
        m.status = "ACTIVE";
    """,
    """
    MERGE (m:CodeModule {id: "py_033"})
    SET m.filename = "mo.py",
        m.layer = "Soul",
        m.owner = "Mo",
        m.role = "Core Executor Logic",
        m.security_level = "High",
        m.status = "ACTIVE";
    """,
    """
    MERGE (m:CodeModule {id: "py_034"})
    SET m.filename = "main.py",
        m.layer = "Body",
        m.owner = "Mo",
        m.role = "Scepter CLI Main Entry Point",
        m.security_level = "Medium",
        m.status = "ACTIVE";
    """,
    """
    MERGE (m:CodeModule {id: "py_035"})
    SET m.filename = "MoStar.py",
        m.layer = "Body",
        m.owner = "Mo",
        m.role = "MoStar Core Runtime Bootstrap",
        m.security_level = "Medium",
        m.status = "ACTIVE";
    """,
    """
    MERGE (m:CodeModule {id: "py_036"})
    SET m.filename = "mostar_moments_log.py",
        m.layer = "Mind",
        m.owner = "Mo",
        m.role = "MoStar Moments Event Logger",
        m.security_level = "Medium",
        m.status = "ACTIVE";
    """,
    """
    MERGE (m:CodeModule {id: "py_037"})
    SET m.filename = "mostar_philosophy.py",
        m.layer = "Soul",
        m.owner = "Mo",
        m.role = "African Philosophy Knowledge Engine",
        m.security_level = "High",
        m.status = "ACTIVE";
    """,
    """
    MERGE (m:CodeModule {id: "py_038"})
    SET m.filename = "register_mostar.py",
        m.layer = "Body",
        m.owner = "Code Conduit",
        m.role = "MoStar Registry and Origin Verification",
        m.security_level = "Medium",
        m.status = "ACTIVE";
    """,
    """
    MERGE (m:CodeModule {id: "py_039"})
    SET m.filename = "divine_command_deck.jsx",
        m.layer = "Body",
        m.owner = "Mo",
        m.role = "Sacred Command Dashboard UI",
        m.security_level = "Medium",
        m.status = "ACTIVE";
    """,
    """
    MERGE (m:CodeModule {id: "py_040"})
    SET m.filename = "tabs_content.jsx",
        m.layer = "Body",
        m.owner = "Mo",
        m.role = "Dashboard Tab Content Renderer",
        m.security_level = "Medium",
        m.status = "ACTIVE";
    """,
    """
    MERGE (m:CodeModule {id: "py_041"})
    SET m.filename = "kairo_logic.js",
        m.layer = "Body",
        m.owner = "Code Conduit",
        m.role = "Kairo Covenant Logic Engine",
        m.security_level = "Medium",
        m.status = "ACTIVE";
    """,
    """
    MERGE (m:CodeModule {id: "py_042"})
    SET m.filename = "land_scroll_validator.js",
        m.layer = "Body",
        m.owner = "TsaTse Fly",
        m.role = "Land Scroll Validation Interface",
        m.security_level = "Medium",
        m.status = "ACTIVE";
    """,

    # --- PHASE 2: ADD LAYER LABELS ---
    """
    MATCH (m:CodeModule) WHERE m.layer = "Soul" AND NOT m:SoulLayer SET m:SoulLayer;
    """,
    """
    MATCH (m:CodeModule) WHERE m.layer = "Mind" AND NOT m:MindLayer SET m:MindLayer;
    """,
    """
    MATCH (m:CodeModule) WHERE m.layer = "Body" AND NOT m:BodyLayer SET m:BodyLayer;
    """,

    # --- PHASE 3: EXECUTION WIRING ---
    """
    MATCH (g:GridCore {name: "MoStar Grid"})
    MATCH (m:CodeModule) WHERE NOT (g)-[:EXECUTES]->(m)
    MERGE (g)-[:EXECUTES]->(m);
    """,
    """
    MATCH (m:CodeModule), (e:Entity)
    WHERE m.owner = e.name AND NOT (e)-[:CONTROLS_MODULE]->(m)
    MERGE (e)-[:CONTROLS_MODULE]->(m);
    """,

    # --- PHASE 4: SEMANTIC WIRING ---
    """
    MATCH (m:CodeModule {filename: "cultural_engine.py"}), (p:Philosophy {name: "Ubuntu"}) MERGE (m)-[:PROCESSES]->(p);
    """,
    """
    MATCH (m:CodeModule {filename: "proverb_compiler.py"}), (p:Philosophy) WITH m, collect(p)[0..5] AS phils UNWIND phils AS p MERGE (m)-[:COMPILES_FROM]->(p);
    """,
    """
    MATCH (m:CodeModule {filename: "mostar_philosophy.py"}), (p:Philosophy) WITH m, collect(p)[0..5] AS phils UNWIND phils AS p MERGE (m)-[:ENCODES]->(p);
    """,
    """
    MATCH (m:CodeModule {filename: "council_engine.py"}), (g:Governance) WITH m, collect(g)[0..5] AS govs UNWIND govs AS g MERGE (m)-[:SIMULATES]->(g);
    """,
    """
    MATCH (m:CodeModule {filename: "mo.py"}), (d:Doctrine {name: "Flameborn Codex"}) MERGE (m)-[:EXECUTES_COVENANT]->(d);
    """,
    """
    MATCH (m:CodeModule {filename: "mostar_moments_log.py"}), (mm:MoStarMoment) MERGE (m)-[:LOGS]->(mm);
    """,

    # --- PHASE 5: RE-CALCULATE METRICS ---
    """
    MATCH (n) WITH count(n) AS total
    MATCH ()-[r]->() WITH total, count(r) AS rels
    MATCH (n) WHERE NOT (n)--() WITH total, rels, count(n) AS orphans
    MATCH (grid:GridCore {name: "MoStar Grid"})
    SET grid.total_nodes = total,
        grid.total_relationships = rels,
        grid.orphans = orphans,
        grid.total_code_modules = total - 696,
        grid.coherence = CASE WHEN orphans = 0 THEN 0.97 ELSE 0.95 END,
        grid.last_audit = timestamp();
    """
]

def run():
    print("Connecting to Neo4j to apply Code Modules...")
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    results = []
    
    with driver.session() as session:
        for i, q in enumerate(queries):
            try:
                res = session.run(q)
                summary = res.consume()
                stats = summary.counters
                results.append({
                    "query_index": i,
                    "status": "success",
                    "updates": {
                        "nodes_created": stats.nodes_created,
                        "nodes_deleted": stats.nodes_deleted,
                        "properties_set": stats.properties_set,
                        "relationships_created": stats.relationships_created,
                        "relationships_deleted": stats.relationships_deleted,
                        "labels_added": stats.labels_added,
                        "labels_removed": stats.labels_removed
                    }
                })
            except Exception as e:
                print(f"Error on query {i}: {e}")
                results.append({"query_index": i, "status": "error", "error": str(e)})

    # Fetch final verification
    verify_queries = [
        "MATCH (g:GridCore) RETURN properties(g) AS GridCore",
        "MATCH (e:Entity)-[:CONTROLS_MODULE]->(m:CodeModule) RETURN e.name AS Owner, count(m) AS Modules_Controlled ORDER BY count(m) DESC"
    ]
    
    verification = {}
    with driver.session() as session:
        for i, q in enumerate(verify_queries):
            try:
                res = session.run(q)
                verification[f"verify_{i}"] = [dict(record) for record in res]
            except Exception as e:
                verification[f"verify_{i}"] = {"error": str(e)}

    driver.close()
    
    out_data = {"execution": results, "verification": verification}
    with open("code_module_results.json", "w", encoding="utf-8") as f:
        json.dump(out_data, f, indent=2, ensure_ascii=False)
    print("Done. Saved to code_module_results.json")

if __name__ == "__main__":
    run()
