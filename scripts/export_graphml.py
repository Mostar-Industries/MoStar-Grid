#!/usr/bin/env python3
"""
MoStar Grid GraphML Exporter
Export the activation subgraph to GraphML format for Wolfram/Gephi.
"""
import json
from datetime import datetime
from neo4j import GraphDatabase

NEO4J_URI = 'bolt://localhost:7687'
NEO4J_AUTH = ('neo4j', 'mostar123')

def export_graphml(output_path: str = 'exports/activation_subgraph.graphml'):
    """Export MoStarMoments and relationships to GraphML."""
    driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)
    
    with driver.session() as s:
        # Get all MoStarMoments with their actual properties
        moments = list(s.run("""
            MATCH (m:MoStarMoment)
            OPTIONAL MATCH (m)-[:PART_OF_ERA]->(e:Era)
            RETURN m.quantum_id AS id,
                   m.description AS description,
                   m.timestamp AS timestamp,
                   m.resonance_score AS resonance,
                   m.trigger_type AS trigger_type,
                   m.initiator AS initiator,
                   m.receiver AS receiver,
                   e.name AS era
            ORDER BY m.timestamp
        """))
        
        # Get PRECEDES relationships (temporal chain)
        precedes = list(s.run("""
            MATCH (a:MoStarMoment)-[r:PRECEDES]->(b:MoStarMoment)
            RETURN a.quantum_id AS source, b.quantum_id AS target, type(r) AS rel_type
        """))
        
        # Get RESONATES_WITH relationships
        resonates = list(s.run("""
            MATCH (a:MoStarMoment)-[r:RESONATES_WITH]->(b:MoStarMoment)
            RETURN a.quantum_id AS source, b.quantum_id AS target, 
                   r.strength AS strength, type(r) AS rel_type
        """))
        
        # Get all Entity relationships
        entities = list(s.run("""
            MATCH (m:MoStarMoment)-[r]->(e:Entity)
            RETURN m.quantum_id AS source, e.name AS target, type(r) AS rel_type
        """))
        
        # Get Era relationships
        eras = list(s.run("""
            MATCH (m:MoStarMoment)-[:PART_OF_ERA]->(e:Era)
            RETURN m.quantum_id AS source, e.name AS target, 'PART_OF_ERA' AS rel_type
        """))
    
    driver.close()
    
    # Build GraphML
    graphml = '''<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns
         http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">
  
  <!-- Node attributes -->
  <key id="description" for="node" attr.name="description" attr.type="string"/>
  <key id="timestamp" for="node" attr.name="timestamp" attr.type="string"/>
  <key id="resonance" for="node" attr.name="resonance" attr.type="double"/>
  <key id="era" for="node" attr.name="era" attr.type="string"/>
  <key id="trigger_type" for="node" attr.name="trigger_type" attr.type="string"/>
  <key id="initiator" for="node" attr.name="initiator" attr.type="string"/>
  <key id="receiver" for="node" attr.name="receiver" attr.type="string"/>
  <key id="node_type" for="node" attr.name="node_type" attr.type="string"/>
  
  <!-- Edge attributes -->
  <key id="rel_type" for="edge" attr.name="rel_type" attr.type="string"/>
  <key id="strength" for="edge" attr.name="strength" attr.type="double"/>
  
  <graph id="MoStarGrid" edgedefault="directed">
'''
    
    # Add MoStarMoment nodes
    seen_nodes = set()
    for m in moments:
        node_id = m['id']
        if not node_id or node_id in seen_nodes:
            continue
        seen_nodes.add(node_id)
        
        description = escape_xml(m['description'] or '')[:500]  # Truncate long descriptions
        timestamp = m['timestamp'] or ''
        resonance = m['resonance'] or 0.0
        era = m['era'] or ''
        trigger_type = m['trigger_type'] or ''
        initiator = m['initiator'] or ''
        receiver = m['receiver'] or ''
        
        graphml += f'''    <node id="{escape_xml(str(node_id))}">
      <data key="node_type">MoStarMoment</data>
      <data key="description">{description}</data>
      <data key="timestamp">{timestamp}</data>
      <data key="resonance">{resonance}</data>
      <data key="era">{era}</data>
      <data key="trigger_type">{trigger_type}</data>
      <data key="initiator">{initiator}</data>
      <data key="receiver">{receiver}</data>
    </node>
'''
    
    # Add Entity nodes from relationships
    entity_nodes = set()
    for e in entities:
        entity_nodes.add(e['target'])
    for e in eras:
        entity_nodes.add(e['target'])
    
    for entity_name in entity_nodes:
        if entity_name and entity_name not in seen_nodes:
            seen_nodes.add(entity_name)
            graphml += f'''    <node id="{escape_xml(entity_name)}">
      <data key="node_type">Entity</data>
      <data key="title">{escape_xml(entity_name)}</data>
    </node>
'''
    
    # Add PRECEDES edges
    edge_id = 0
    for p in precedes:
        graphml += f'''    <edge id="e{edge_id}" source="{p['source']}" target="{p['target']}">
      <data key="rel_type">PRECEDES</data>
    </edge>
'''
        edge_id += 1
    
    # Add RESONATES_WITH edges
    for r in resonates:
        strength = r['strength'] or 1.0
        graphml += f'''    <edge id="e{edge_id}" source="{r['source']}" target="{r['target']}">
      <data key="rel_type">RESONATES_WITH</data>
      <data key="strength">{strength}</data>
    </edge>
'''
        edge_id += 1
    
    # Add Entity edges
    for e in entities:
        if e['target'] in seen_nodes:
            graphml += f'''    <edge id="e{edge_id}" source="{e['source']}" target="{escape_xml(e['target'])}">
      <data key="rel_type">{e['rel_type']}</data>
    </edge>
'''
            edge_id += 1
    
    # Add Era edges
    for e in eras:
        if e['target'] in seen_nodes:
            graphml += f'''    <edge id="e{edge_id}" source="{e['source']}" target="{escape_xml(e['target'])}">
      <data key="rel_type">PART_OF_ERA</data>
    </edge>
'''
            edge_id += 1
    
    graphml += '''  </graph>
</graphml>
'''
    
    # Ensure exports directory exists
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Write file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(graphml)
    
    print(f"✅ Exported GraphML to: {output_path}")
    print(f"   📊 Nodes: {len(seen_nodes)}")
    print(f"   🔗 Edges: {edge_id}")
    print(f"   📅 MoStarMoments: {len(moments)}")
    
    return output_path


def escape_xml(text: str) -> str:
    """Escape XML special characters."""
    if not text:
        return ''
    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&apos;'))


if __name__ == '__main__':
    export_graphml()
