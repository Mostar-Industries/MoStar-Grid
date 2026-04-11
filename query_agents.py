from neo4j import GraphDatabase
import json

driver = GraphDatabase.driver('bolt://127.0.0.1:7687', auth=('neo4j', 'Mostar123'))
records, _, _ = driver.execute_query('MATCH (a:Agent) RETURN a.id as id, a.name as name, a.type as type, a.capabilities as capabilities, a.status as status, a.manifestationStrength as manifestationStrength LIMIT 5')

print("\n--- AGENT QUERY RESULTS ---")
for r in records:
    print(json.dumps(dict(r), indent=2))
print("---------------------------\n")
