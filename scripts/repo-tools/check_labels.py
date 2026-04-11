import os
import asyncio
from backend.core_engine.moscript_engine import MoScriptEngine

async def check():
    from neo4j import TrustAll
    engine = MoScriptEngine()
    ritual = {
        'operation': 'neo4j_traverse',
        'payload': {'cypher': 'MATCH (n) RETURN labels(n) as labels, count(*) as count ORDER BY count DESC', 'purpose': 'check_labels'}
    }
    # Using TrustAll() instance for Neo4j 6.0
    res = await engine.interpret(ritual)
    print(res)

asyncio.run(check())
