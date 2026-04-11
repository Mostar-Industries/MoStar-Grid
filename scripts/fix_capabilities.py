"""Fix corrupted capabilities in Neo4j"""
import os
import random
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv('NEO4J_URI'),
    auth=(os.getenv('NEO4J_USER'), os.getenv('NEO4J_PASSWORD'))
)

CAPABILITIES = ['vision', 'nlp', 'reasoning', 'voice', 'memory', 'planning', 'execution']

with driver.session() as session:
    # Get all agents
    result = session.run('MATCH (a:Agent) RETURN a.id AS id, a.name AS name')
    agents = list(result)
    
    for agent in agents:
        name = (agent['name'] or '').lower()
        
        # Assign capabilities based on agent type
        if 'vision' in name:
            caps = ['vision', 'reasoning']
        elif 'nlp' in name:
            caps = ['nlp', 'voice', 'reasoning']
        elif 'alpha' in name:
            caps = ['planning', 'execution', 'memory']
        else:
            caps = random.sample(CAPABILITIES, k=random.randint(1, 3))
        
        session.run(
            'MATCH (a:Agent {id: $id}) SET a.capabilities = $caps',
            id=agent['id'], 
            caps=caps
        )
    
    print(f'Fixed capabilities for {len(agents)} agents')
    
    # Verify
    result = session.run('MATCH (a:Agent) RETURN a.name AS name, a.capabilities AS caps LIMIT 5')
    print('\nSample capabilities:')
    for rec in result:
        print(f'  {rec["name"]}: {rec["caps"]}')

driver.close()
print('\n✓ Done!')
