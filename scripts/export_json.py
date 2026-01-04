#!/usr/bin/env python3
"""
MoStar Grid JSON Exporter
Export the activation subgraph to JSON format for lightweight usage.
"""
import json
import os
import datetime
from neo4j import GraphDatabase

NEO4J_URI = 'bolt://localhost:7687'
NEO4J_AUTH = ('neo4j', 'mostar123')

def export_json(output_path: str = 'exports/activation_subgraph.json'):
    """Export MoStarMoments and relationships to JSON."""
    driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)
    
    data = {
        "nodes": [],
        "edges": [],
        "metadata": {
            "generated_at": None,
            "stats": {}
        }
    }
    
    with driver.session() as s:
        # Get all MoStarMoments
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
                   e.name AS era,
                   labels(m) as labels
            ORDER BY m.timestamp
        """))

        # Get connected Entities and Eras to ensure graph completeness
        others = list(s.run("""
            MATCH (m:MoStarMoment)-[r]->(o)
            WHERE NOT 'MoStarMoment' IN labels(o) AND type(r) <> 'IGNITES'
            RETURN DISTINCT 
                   CASE WHEN o.quantum_id IS NOT NULL THEN o.quantum_id ELSE o.name END AS id,
                   labels(o) AS labels,
                   o.name AS name,
                   o.description AS description
        """))
        
        # Get relationships (excluding high-volume IGNITES for lightweight export)
        rels = list(s.run("""
            MATCH (a:MoStarMoment)-[r]->(b)
            WHERE type(r) <> 'IGNITES'
            RETURN a.quantum_id AS source, 
                   CASE WHEN b.quantum_id IS NOT NULL THEN b.quantum_id ELSE b.name END AS target,
                   type(r) AS type,
                   properties(r) AS props,
                   labels(b) AS target_labels
        """))

    driver.close()
    
    # Process Nodes
    for m in moments:
        node = {
            "id": m['id'],
            "type": "MoStarMoment",
            "data": {
                "description": m['description'],
                "timestamp": str(m['timestamp']),
                "resonance": m['resonance'],
                "era": m['era'],
                "trigger": m['trigger_type'],
                "initiator": m['initiator'],
                "receiver": m['receiver']
            }
        }
        data["nodes"].append(node)

    for o in others:
        node = {
            "id": o['id'],
            "type": o['labels'][0] if o['labels'] else "Unknown",
            "data": {
                "name": o['name'],
                "description": o.get('description', '')
            }
        }
        data["nodes"].append(node)
        
    # Process Edges
    for r in rels:
        edge = {
            "source": r['source'],
            "target": r['target'],
            "type": r['type'],
            "properties": r['props']
        }
        data["edges"].append(edge)

    # Metadata
    data["metadata"]["generated_at"] = datetime.datetime.now().isoformat()
    data["metadata"]["stats"] = {
        "node_count": len(data["nodes"]),
        "edge_count": len(data["edges"])
    }
    
    # Ensure exports directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=str)
        
    print(f"✅ Exported JSON to: {output_path}")
    print(f"   📊 Nodes: {len(data['nodes'])}")
    print(f"   🔗 Edges: {len(data['edges'])}")
    
    return output_path

if __name__ == '__main__':
    export_json()
