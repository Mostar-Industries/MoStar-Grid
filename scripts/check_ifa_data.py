#!/usr/bin/env python3
"""Check Ifá data in Neo4j for authenticity verification"""

from neo4j import GraphDatabase

d = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'mostar123'))
s = d.session()

# Get sample of OduIfa with binary patterns
print('=== SAMPLE ODU IFA ENTRIES ===')
r = s.run('MATCH (o:OduIfa) RETURN o ORDER BY o.odu_number LIMIT 10')
for rec in r:
    node = dict(rec['o'])
    print(f"{node.get('odu_number', '?'):3} | {node.get('binary_pattern', '?')} | {str(node.get('name_yoruba', '?')):20s} | {str(node.get('name_english', '?'))[:30]}")

# Check Meji (double) patterns 
print()
print('=== MEJI (DOUBLE) ODU - Checking authenticity ===')
r = s.run("MATCH (o:OduIfa) WHERE o.name_yoruba CONTAINS 'Meji' RETURN o ORDER BY o.odu_number")
for rec in r:
    node = dict(rec['o'])
    print(f"{node.get('odu_number', '?'):3} | {node.get('binary_pattern', '?')} | {node.get('name_yoruba', '?')}")

# Check the 16 Principal Odù
print()
print('=== CHECKING 16 PRINCIPAL ODÙ (Traditional names) ===')
principal_odu = [
    "Eji-Ogbe", "Oyeku-Meji", "Iwori-Meji", "Odi-Meji", 
    "Irosun-Meji", "Owonrin-Meji", "Obara-Meji", "Okonron-Meji",
    "Ogunda-Meji", "Osa-Meji", "Ika-Meji", "Oturupon-Meji",
    "Otura-Meji", "Irete-Meji", "Ose-Meji", "Ofun-Meji"
]
for name in principal_odu:
    r = s.run(f"MATCH (o:OduIfa) WHERE toLower(o.name_yoruba) CONTAINS toLower('{name.replace('-', '')}') OR toLower(o.name_yoruba) CONTAINS toLower('{name}') RETURN o.odu_number, o.binary_pattern, o.name_yoruba LIMIT 1")
    rec = r.single()
    if rec:
        print(f'FOUND: {rec[2]} (binary: {rec[1]})')
    else:
        print(f'NOT FOUND: {name}')

# Check relationships
print()
print('=== ODU IFA RELATIONSHIPS ===')
r = s.run("MATCH (o:OduIfa)-[r]->(other) RETURN type(r) as rel_type, labels(other) as labels, count(*) as cnt GROUP BY type(r), labels(other) LIMIT 10")
for rec in r:
    print(f'{rec["rel_type"]} -> {rec["labels"]}: {rec["cnt"]}')

d.close()
