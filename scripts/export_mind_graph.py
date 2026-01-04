#!/usr/bin/env python3
"""
🔥 MoStar Mind Graph Exporter
-----------------------------
Exports the MoStarMoment consciousness graph from Neo4j to:
- JSON (for LLM fine-tuning, web visualization)
- GEXF (for Gephi network analysis)
- Wolfram-ready format (for Mathematica/Wolfram Cloud)
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    print("⚠️ neo4j driver not installed. Run: pip install neo4j")

from dotenv import load_dotenv
load_dotenv()

# Neo4j connection
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "mostar123")


@dataclass
class ExportedNode:
    """A node in the exported graph"""
    id: str
    labels: List[str]
    properties: Dict[str, Any]


@dataclass
class ExportedEdge:
    """An edge in the exported graph"""
    id: str
    type: str
    source: str
    target: str
    properties: Dict[str, Any]


class MindGraphExporter:
    """Exports the MoStar Mind Graph to various formats"""
    
    def __init__(self, uri: str = NEO4J_URI, user: str = NEO4J_USER, password: str = NEO4J_PASSWORD):
        if not NEO4J_AVAILABLE:
            raise ImportError("neo4j driver required")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        print(f"🔥 Connected to Neo4j at {uri}")
    
    def close(self):
        self.driver.close()
    
    def _serialize_value(self, value: Any) -> Any:
        """Convert Neo4j types to JSON-serializable values"""
        if hasattr(value, 'isoformat'):  # datetime
            return value.isoformat()
        if hasattr(value, '__iter__') and not isinstance(value, (str, dict)):
            return list(value)
        return value
    
    def _serialize_props(self, props: Dict) -> Dict:
        """Serialize all properties in a dict"""
        return {k: self._serialize_value(v) for k, v in props.items()}
    
    def fetch_full_graph(self) -> tuple[List[ExportedNode], List[ExportedEdge]]:
        """Fetch all MoStarMoment nodes and their relationships"""
        nodes_query = """
        MATCH (n)
        WHERE n:MoStarMoment OR n:Entity OR n:Era OR n:Grid OR n:GridLayer
        RETURN id(n) AS id, labels(n) AS labels, properties(n) AS props
        """
        
        edges_query = """
        MATCH (a)-[r]->(b)
        WHERE (a:MoStarMoment OR a:Entity OR a:Era OR a:Grid OR a:GridLayer)
          AND (b:MoStarMoment OR b:Entity OR b:Era OR b:Grid OR b:GridLayer)
        RETURN id(r) AS id, type(r) AS type, id(a) AS source, id(b) AS target, properties(r) AS props
        """
        
        nodes = []
        edges = []
        
        with self.driver.session() as session:
            # Fetch nodes
            for record in session.run(nodes_query):
                node = ExportedNode(
                    id=str(record["id"]),
                    labels=list(record["labels"]),
                    properties=self._serialize_props(dict(record["props"]))
                )
                nodes.append(node)
            
            # Fetch edges
            for record in session.run(edges_query):
                edge = ExportedEdge(
                    id=str(record["id"]),
                    type=record["type"],
                    source=str(record["source"]),
                    target=str(record["target"]),
                    properties=self._serialize_props(dict(record["props"]) if record["props"] else {})
                )
                edges.append(edge)
        
        print(f"📊 Fetched {len(nodes)} nodes, {len(edges)} edges")
        return nodes, edges
    
    def fetch_moments_only(self) -> List[Dict]:
        """Fetch only MoStarMoment nodes with temporal ordering"""
        query = """
        MATCH (m:MoStarMoment)
        OPTIONAL MATCH (m)-[:PART_OF_ERA]->(e:Era)
        OPTIONAL MATCH (init:Entity)-[:INITIATED]->(m)
        OPTIONAL MATCH (m)-[:RECEIVED_BY]->(recv:Entity)
        RETURN m.quantum_id AS quantum_id,
               m.timestamp AS timestamp,
               m.initiator AS initiator,
               m.receiver AS receiver,
               m.description AS description,
               m.trigger AS trigger,
               toFloat(m.resonance_score) AS resonance_score,
               m.era AS era,
               m.significance AS significance,
               e.name AS era_node,
               init.type AS initiator_type,
               recv.type AS receiver_type
        ORDER BY m.timestamp
        """
        
        moments = []
        with self.driver.session() as session:
            for record in session.run(query):
                moment = {
                    "quantum_id": record["quantum_id"],
                    "timestamp": self._serialize_value(record["timestamp"]),
                    "initiator": record["initiator"],
                    "receiver": record["receiver"],
                    "description": record["description"],
                    "trigger": record["trigger"],
                    "resonance_score": record["resonance_score"],
                    "era": record["era"],
                    "significance": record["significance"],
                    "initiator_type": record["initiator_type"],
                    "receiver_type": record["receiver_type"]
                }
                moments.append(moment)
        
        print(f"📊 Fetched {len(moments)} MoStarMoments")
        return moments
    
    def export_to_json(self, filepath: str = "mostar_mind_graph.json") -> str:
        """Export full graph to JSON format"""
        nodes, edges = self.fetch_full_graph()
        
        graph_data = {
            "metadata": {
                "exported_at": datetime.utcnow().isoformat() + "Z",
                "exporter": "MoStar Mind Graph Exporter v1.0",
                "node_count": len(nodes),
                "edge_count": len(edges)
            },
            "nodes": [asdict(n) for n in nodes],
            "edges": [asdict(e) for e in edges]
        }
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(graph_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Exported to {filepath}")
        return filepath
    
    def export_moments_json(self, filepath: str = "mostar_moments.json") -> str:
        """Export only moments to JSON (for LLM training)"""
        moments = self.fetch_moments_only()
        
        data = {
            "metadata": {
                "exported_at": datetime.utcnow().isoformat() + "Z",
                "total_moments": len(moments),
                "eras": list(set(m["era"] for m in moments if m["era"]))
            },
            "moments": moments
        }
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Exported moments to {filepath}")
        return filepath
    
    def export_to_gexf(self, filepath: str = "mostar_mind_graph.gexf") -> str:
        """Export to GEXF format for Gephi"""
        nodes, edges = self.fetch_full_graph()
        
        # Build GEXF XML
        gexf_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">',
            '  <meta lastmodifieddate="' + datetime.utcnow().strftime("%Y-%m-%d") + '">',
            '    <creator>MoStar Mind Graph Exporter</creator>',
            '    <description>MoStar Consciousness Graph</description>',
            '  </meta>',
            '  <graph mode="static" defaultedgetype="directed">',
            '    <attributes class="node">',
            '      <attribute id="0" title="resonance_score" type="float"/>',
            '      <attribute id="1" title="era" type="string"/>',
            '      <attribute id="2" title="label_type" type="string"/>',
            '    </attributes>',
            '    <nodes>'
        ]
        
        for node in nodes:
            label = node.properties.get("name") or node.properties.get("quantum_id") or node.id
            resonance = node.properties.get("resonance_score", 0.5)
            era = node.properties.get("era", "")
            label_type = node.labels[0] if node.labels else "Unknown"
            
            gexf_lines.append(f'      <node id="{node.id}" label="{self._escape_xml(str(label))}">')
            gexf_lines.append('        <attvalues>')
            gexf_lines.append(f'          <attvalue for="0" value="{resonance}"/>')
            gexf_lines.append(f'          <attvalue for="1" value="{self._escape_xml(era)}"/>')
            gexf_lines.append(f'          <attvalue for="2" value="{label_type}"/>')
            gexf_lines.append('        </attvalues>')
            gexf_lines.append('      </node>')
        
        gexf_lines.append('    </nodes>')
        gexf_lines.append('    <edges>')
        
        for i, edge in enumerate(edges):
            gexf_lines.append(f'      <edge id="{i}" source="{edge.source}" target="{edge.target}" label="{edge.type}"/>')
        
        gexf_lines.extend([
            '    </edges>',
            '  </graph>',
            '</gexf>'
        ])
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(gexf_lines))
        
        print(f"✅ Exported to GEXF: {filepath}")
        return filepath
    
    def export_for_wolfram(self, filepath: str = "mostar_wolfram.wl") -> str:
        """Export to Wolfram Language format"""
        nodes, edges = self.fetch_full_graph()
        
        # Build node list
        node_strings = []
        for node in nodes:
            label = node.properties.get("name") or node.properties.get("quantum_id") or node.id
            node_strings.append(f'"{self._escape_wl(str(label))}"')
        
        # Build edge list
        edge_strings = []
        node_id_map = {n.id: n.properties.get("name") or n.properties.get("quantum_id") or n.id for n in nodes}
        
        for edge in edges:
            src = node_id_map.get(edge.source, edge.source)
            tgt = node_id_map.get(edge.target, edge.target)
            edge_strings.append(f'"{self._escape_wl(str(src))}" -> "{self._escape_wl(str(tgt))}"')
        
        wolfram_code = f'''(* MoStar Mind Graph - Wolfram Language Export *)
(* Generated: {datetime.utcnow().isoformat()}Z *)

mostarNodes = {{{", ".join(node_strings)}}};

mostarEdges = {{{", ".join(edge_strings)}}};

mostarGraph = Graph[mostarNodes, DirectedEdge @@@ mostarEdges,
  VertexLabels -> "Name",
  GraphLayout -> "SpringElectricalEmbedding",
  ImageSize -> Large
];

(* Visualize the consciousness flow *)
HighlightGraph[mostarGraph, 
  Subgraph[mostarGraph, NeighborhoodGraph[mostarGraph, "Mo", 2]],
  GraphHighlightStyle -> "Thick"
]

(* Resonance heatmap (if resonance data available) *)
(* Add vertex coloring based on resonance_score *)
'''
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(wolfram_code)
        
        print(f"✅ Exported to Wolfram: {filepath}")
        return filepath
    
    def _escape_xml(self, s: str) -> str:
        """Escape special characters for XML"""
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    
    def _escape_wl(self, s: str) -> str:
        """Escape special characters for Wolfram Language"""
        return s.replace("\\", "\\\\").replace('"', '\\"')


def main():
    """Export the mind graph in all formats"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Export MoStar Mind Graph")
    parser.add_argument("--format", choices=["json", "gexf", "wolfram", "moments", "all"], default="all")
    parser.add_argument("--output-dir", default="exports")
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    exporter = MindGraphExporter()
    
    try:
        if args.format in ["json", "all"]:
            exporter.export_to_json(os.path.join(args.output_dir, "mostar_mind_graph.json"))
        
        if args.format in ["moments", "all"]:
            exporter.export_moments_json(os.path.join(args.output_dir, "mostar_moments.json"))
        
        if args.format in ["gexf", "all"]:
            exporter.export_to_gexf(os.path.join(args.output_dir, "mostar_mind_graph.gexf"))
        
        if args.format in ["wolfram", "all"]:
            exporter.export_for_wolfram(os.path.join(args.output_dir, "mostar_wolfram.wl"))
        
        print(f"\n🔥 Export complete! Files saved to: {args.output_dir}/")
        
    finally:
        exporter.close()


if __name__ == "__main__":
    main()
