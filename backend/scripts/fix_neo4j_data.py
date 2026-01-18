"""Fix and seed Neo4j Agent data with proper structure"""
import os
import random
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv('NEO4J_URI'),
    auth=(os.getenv('NEO4J_USER'), os.getenv('NEO4J_PASSWORD'))
)

VALID_STATUSES = ['MONITORING', 'IDLE', 'ACTIVE', 'STANDBY', 'OFFLINE']
VALID_CAPABILITIES = ['vision', 'nlp', 'reasoning', 'voice', 'memory', 'planning', 'execution']

def fix_agent_data():
    with driver.session() as session:
        # Fix status values
        result = session.run("""
            MATCH (a:Agent)
            WITH a, 
                CASE 
                    WHEN toLower(a.status) = 'online' THEN 'MONITORING'
                    WHEN toLower(a.status) = '_rare_' THEN 'IDLE'
                    WHEN a.status IS NULL THEN 'UNKNOWN'
                    ELSE toUpper(a.status)
                END AS newStatus
            SET a.status = newStatus
            RETURN count(a) AS updated
        """)
        print(f"Fixed status values: {result.single()['updated']} agents")

        # Add manifestationStrength where missing
        result = session.run("""
            MATCH (a:Agent) WHERE a.manifestationStrength IS NULL
            SET a.manifestationStrength = rand() * 0.6 + 0.4
            RETURN count(a) AS updated
        """)
        print(f"Added manifestationStrength: {result.single()['updated']} agents")

        # Fix capabilities - convert to proper array
        result = session.run("""
            MATCH (a:Agent)
            WITH a, 
                CASE 
                    WHEN a.capabilities IS NULL THEN ['general']
                    WHEN size(a.capabilities) = 0 THEN ['general']
                    ELSE a.capabilities
                END AS caps
            SET a.capabilities = caps
            RETURN count(a) AS updated
        """)
        print(f"Fixed capabilities: {result.single()['updated']} agents")

def seed_moments():
    """Create sample MostarMoment nodes if none exist"""
    with driver.session() as session:
        # Check if moments exist
        result = session.run("MATCH (m:MostarMoment) RETURN count(m) AS cnt")
        count = result.single()['cnt']
        
        if count > 0:
            print(f"MostarMoment nodes already exist: {count}")
            return
        
        # Create sample moments
        moments = [
            {
                'quantum_id': f'moment_{i}',
                'initiator': random.choice(['Soul Layer', 'Mind Layer', 'Body Layer', 'Ifá Oracle', 'Voice Layer']),
                'receiver': random.choice(['Grid Core', 'Agent Lattice', 'Memory Store', 'Verdict Engine']),
                'description': random.choice([
                    'Processed ancestral query',
                    'Executed ritual seal_covenant',
                    'Synchronized voice manifest',
                    'Updated grid coherence',
                    'Validated oracle response'
                ]),
                'trigger_type': random.choice(['ritual', 'query', 'sync', 'validation']),
                'resonance_score': random.uniform(0.65, 0.99),
                'timestamp': f'2026-01-04T0{random.randint(1,9)}:{random.randint(10,59)}:{random.randint(10,59)}.000Z'
            }
            for i in range(20)
        ]
        
        for m in moments:
            session.run("""
                CREATE (m:MostarMoment {
                    quantum_id: $quantum_id,
                    initiator: $initiator,
                    receiver: $receiver,
                    description: $description,
                    trigger_type: $trigger_type,
                    resonance_score: $resonance_score,
                    timestamp: $timestamp
                })
            """, m)
        
        print(f"Created {len(moments)} MostarMoment nodes")

def verify():
    with driver.session() as session:
        # Check status distribution
        result = session.run("""
            MATCH (a:Agent)
            RETURN a.status AS status, count(a) AS cnt, avg(a.manifestationStrength) AS avgStrength
            ORDER BY cnt DESC
        """)
        print("\n=== Agent Status Distribution ===")
        for rec in result:
            print(f"  {rec['status']}: {rec['cnt']} agents, avg strength: {rec['avgStrength']:.2f}")
        
        # Check moments
        result = session.run("""
            MATCH (m:MostarMoment)
            RETURN count(m) AS total, avg(m.resonance_score) AS avgRes
        """)
        rec = result.single()
        print(f"\n=== MostarMoments ===")
        print(f"  Total: {rec['total']}, Avg Resonance: {rec['avgRes']:.4f if rec['avgRes'] else 'N/A'}")

if __name__ == "__main__":
    print("=== Fixing Agent Data ===")
    fix_agent_data()
    
    print("\n=== Seeding Moments ===")
    seed_moments()
    
    print("\n=== Verification ===")
    verify()
    
    driver.close()
    print("\n✓ Done!")
