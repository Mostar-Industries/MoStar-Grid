import os
from neo4j import GraphDatabase

# Attempting both IPv4 and IPv6 instances on port 7687
HOSTS = ['127.0.0.1', '::1']
USER = 'neo4j'
PASSWORD = 'mostar123'

queries = [
    ('MATCH (n:IbibioWords) SET n:IbibioWord RETURN count(n) AS done', 'IbibioWords -> IbibioWord'),
    ('MATCH (n:HealingPractices) SET n:HealingPractice RETURN count(n) AS done', 'HealingPractices -> HealingPractice'),
    ('MATCH (n:Neo4jAgents) SET n:Agent RETURN count(n) AS done', 'Neo4jAgents -> Agent'),
    ('MATCH (n:MostarMoment) SET n:MoStarMoment RETURN count(n) AS done', 'MostarMoment -> MoStarMoment'),
    ('MATCH (n:IndigenousGovernance) SET n:Governance RETURN count(n) AS done', 'IndigenousGovernance -> Governance'),
    ('MATCH (n:EntityEcosystem) SET n:Entity RETURN count(n) AS done', 'EntityEcosystem -> Entity'),
    ('MATCH (n:Neo4jMetrics) SET n:Metric RETURN count(n) AS done', 'Neo4jMetrics -> Metric'),
    ('MATCH (n:Neo4jTasks) SET n:Task RETURN count(n) AS done', 'Neo4jTasks -> Task'),
    ('MATCH (n:IbibioDictionaryEntry) SET n:IbibioEntry RETURN count(n) AS done', 'IbibioDictionaryEntry -> IbibioEntry')
]

def align_host(host):
    uri = f'bolt://{host}:7687'
    print(f'\n--- Connecting to {uri} ---')
    try:
        driver = GraphDatabase.driver(uri, auth=(USER, PASSWORD), connection_timeout=5)
        with driver.session() as session:
            # Check for any data first
            total = session.run('MATCH (n) RETURN count(n)').single()[0]
            print(f'  Total nodes found: {total}')
            if total == 0:
                print(f'  Skipping: No nodes found on {host}.')
                return

            # Apply Aliases
            for q, description in queries:
                res = session.run(q).single()
                count = res['done'] if res else 0
                print(f'  {description}: {count}')

            # Final check
            print('  --- Resulting Labels ---')
            labels = session.run('MATCH (n) UNWIND labels(n) AS lbl RETURN lbl, count(*) AS cnt ORDER BY cnt DESC').data()
            for r in labels:
                print(f'    {r["lbl"]}: {r["cnt"]}')
    except Exception as e:
        print(f'  Connection Error on {host}: {e}')
    finally:
        if 'driver' in locals(): driver.close()

if __name__ == '__main__':
    for h in HOSTS:
        align_host(h)
