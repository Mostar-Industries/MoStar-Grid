import os
import re
from neo4j import GraphDatabase

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "mostar123"

def fix_query(query):
    # Match datetime(row.xyz), replace it with datetime(replace(row.xyz, ' ', 'T'))
    query = re.sub(r"datetime\((row\.[a-zA-Z0-9_]+)\)", r"datetime(replace(\1, ' ', 'T'))", query)
    # Remove USING PERIODIC COMMIT as it is not supported in this context for python driver auto-commit sometimes, or can cause issues
    query = re.sub(r"USING PERIODIC COMMIT \d+", "", query)
    query = re.sub(r"USING PERIODIC COMMIT", "", query)
    return query

def main():
    print("🔥 Connecting to Neo4j...")
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    cypher_file = r"c:\Users\idona\OneDrive - World Health Organization\Documents\Dev\MoStar-Grid\backend\neo4j-mostar-industries\import\UNIFIED_NEO4J_IMPORT_2026.cypher"
    
    with open(cypher_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    blocks = content.split(';')
    statements = []
    
    for b in blocks:
        s = b.strip()
        if not s: continue
        statements.append(s)

    with driver.session() as session:
        for i, stmt in enumerate(statements):
            stmt = fix_query(stmt)
            lines = stmt.split('\n')
            comment_line = [l for l in lines if l.startswith('//')]
            desc = comment_line[-1] if comment_line else f"Block {i+1}"
            print(f"Executing: {desc}")
            
            try:
                session.run(stmt)
                print("  ✅ Success")
            except Exception as e:
                print(f"  ❌ Failed: {str(e)}")
                
    driver.close()
    print("🔥 Import Complete.")

if __name__ == '__main__':
    main()
