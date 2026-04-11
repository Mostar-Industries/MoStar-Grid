#!/usr/bin/env python3
"""MoStar Grid Status Check"""
from neo4j import GraphDatabase

driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'mostar123'))

with driver.session() as s:
    # APOC Export check using SHOW PROCEDURES
    exports = [r['name'] for r in s.run("SHOW PROCEDURES YIELD name WHERE name STARTS WITH 'apoc.export' RETURN name")]
    print('✅ APOC Export Procedures:', len(exports))
    for e in exports[:5]:
        print(f'   - {e}')
    
    # MoStarMoment count
    count = s.run('MATCH (m:MoStarMoment) RETURN count(m) AS c').single()['c']
    print(f'\n🧠 MoStarMoments: {count}')
    
    # Era distribution
    eras = list(s.run('MATCH (m:MoStarMoment)-[:PART_OF_ERA]->(e:Era) RETURN e.name AS era, count(m) AS c ORDER BY e.name'))
    print('📅 By Era:')
    for e in eras:
        print(f'   {e["era"]}: {e["c"]}')
    
    # Resonance stats
    stats = s.run('MATCH (m:MoStarMoment) RETURN avg(toFloat(m.resonance_score)) AS avg, max(toFloat(m.resonance_score)) AS peak').single()
    print(f'\n⚡ Resonance: avg={stats["avg"]:.3f}, peak={stats["peak"]}')

driver.close()
print('\n✅ Grid Status: ONLINE')
