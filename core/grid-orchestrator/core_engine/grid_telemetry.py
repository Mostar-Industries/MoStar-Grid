#!/usr/bin/env python3
"""
📡 MOSTAR GRID — CANONICAL TELEMETRY v3
Provides unified, MoScript-governed telemetry for the Hyper-Spine Dashboard.
Transforms backend data into the canonical API schema, utilizing purely sealed traversals.
"""

import os
import asyncio
from datetime import datetime, timezone
import logging
from .moscript_engine import MoScriptEngine

log = logging.getLogger("MoStarTelemetry")

class CanonicalTelemetryEngine:
    def __init__(self, engine: MoScriptEngine = None):
        self.mo = engine or MoScriptEngine()

    async def _safe_traverse(self, cypher: str, purpose: str, target: str = "Grid.Mind"):
        ritual = {
            "operation": "neo4j_traverse",
            "payload": {
                "cypher": cypher,
                "purpose": purpose,
                "redaction_level": "standard"
            },
            "target": target
        }
        res = await self.mo.interpret(ritual)
        if res.get("status") == "aligned":
            return res.get("result", {}).get("records", [])
        return []

    async def get_grid_telemetry(self) -> dict:
        """
        Gathers Grid telemetry using MoScript-governed Neo4j traversals
        and formats it into Canonical Telemetry v3.
        """
        # --- 1. Grid State ---
        grid_state_cypher = """
            MATCH (m:MoStarMoment)
            RETURN avg(coalesce(m.resonance_score, 0.85)) as avg_resonance,
                   max(m.timestamp) as last_cycle,
                   count(m) as totalMoments,
                   count(distinct m.initiator) as distinctInitiators
        """
        grid_state_records = await self._safe_traverse(grid_state_cypher, "telemetry_grid_state")
        
        avg_resonance = 0.85
        last_cycle = datetime.now(timezone.utc).isoformat()
        total_moments = 0
        distinct_initiators = 0
        if grid_state_records:
            avg_resonance = float(grid_state_records[0].get("avg_resonance") or 0.85)
            last_cycle = grid_state_records[0].get("last_cycle") or last_cycle
            total_moments = grid_state_records[0].get("totalMoments") or 0
            distinct_initiators = grid_state_records[0].get("distinctInitiators") or 0

        # Calculate a pseudo confidence based on resonance threshold
        confidence = min(100.0, max(0.0, avg_resonance * 100 + 5.0))

        # --- 2. Agents ---
        agents_cypher = """
            MATCH (a:Agent)
            RETURN coalesce(a.agent_id, a.id, elementId(a)) AS id,
                   a.name AS name,
                   coalesce(a.manifestationStrength, 50.0) AS manifestationStrength,
                   coalesce(a.status, 'online') AS status,
                   a.task_count AS task_count
            ORDER BY a.name ASC
            LIMIT 500
        """
        agents_records = await self._safe_traverse(agents_cypher, "telemetry_agents", "Grid.Body")
        
        agents = []
        for a in agents_records:
            agents.append({
                "id": a.get("id"),
                "name": a.get("name"),
                "manifestationStrength": float(a.get("manifestationStrength", 50.0)),
                "status": str(a.get("status", "online")),
                "provenance": {"task_count": a.get("task_count", 0)}
            })

        # --- 3. Moments ---
        # Fetch generic recent
        recent_cypher = """
            MATCH (m:MoStarMoment)
            RETURN m.quantum_id AS id, m.description AS desc, m.layer AS layer, m.resonance_score AS res, m.timestamp as ts
            ORDER BY m.timestamp DESC LIMIT 15
        """
        recent_moments_raw = await self._safe_traverse(recent_cypher, "telemetry_recent_moments")
        
        # Categorized moments
        soul_cypher = """MATCH (m:MoStarMoment {layer: 'SOUL'}) RETURN m.quantum_id AS id, m.description AS desc ORDER BY m.timestamp DESC LIMIT 5"""
        soul_raw = await self._safe_traverse(soul_cypher, "telemetry_soul_moments", "Grid.Soul")

        mind_cypher = """MATCH (m:MoStarMoment {layer: 'MIND'}) RETURN m.quantum_id AS id, m.description AS desc ORDER BY m.timestamp DESC LIMIT 5"""
        mind_raw = await self._safe_traverse(mind_cypher, "telemetry_mind_moments", "Grid.Mind")
        
        body_cypher = """MATCH (m:MoStarMoment {layer: 'BODY'}) RETURN m.quantum_id AS id, m.description AS desc ORDER BY m.timestamp DESC LIMIT 5"""
        body_raw = await self._safe_traverse(body_cypher, "telemetry_body_moments", "Grid.Body")

        # --- 4. Database Instance Monitor / Layer Nodes ---
        neo4j_stats_cypher = """
            CALL db.labels() YIELD label
            MATCH (n) WHERE label IN labels(n)
            WITH label, count(n) AS c
            WHERE c > 0
            RETURN label, c
            ORDER BY c DESC LIMIT 15
        """
        neo4j_records = await self._safe_traverse(neo4j_stats_cypher, "telemetry_neo4j_stats")
        layer_nodes = {rec["label"]: rec["c"] for rec in neo4j_records}

        nodes_cypher = "MATCH (n) RETURN count(n) AS c"
        nodes_res = await self._safe_traverse(nodes_cypher, "telemetry_total_nodes")
        total_nodes = nodes_res[0].get("c", 0) if nodes_res else 0

        rels_cypher = "MATCH ()-[r]->() RETURN count(r) AS c"
        rels_res = await self._safe_traverse(rels_cypher, "telemetry_total_rels")
        total_rels = rels_res[0].get("c", 0) if rels_res else 0

        # Activity in last 24 hours
        yesterday = (datetime.now(timezone.utc).timestamp() - 86400)
        # Convert to ISO string or however the timestamp is stored. Assuming ISO or float.
        # Let's try to match the timestamp format in the DB.
        activity_cypher = """
            MATCH (m:MoStarMoment)
            WHERE datetime(m.timestamp) > datetime() - duration('P1D')
            RETURN count(m) AS c
        """
        activity_res = await self._safe_traverse(activity_cypher, "telemetry_activity_24h")
        moments_24h = activity_res[0].get("c", 0) if activity_res else 0

        # --- 5. Advanced Metrics (Relationship Types, Artifacts, Density) ---
        rel_types_cypher = """
            CALL db.relationshipTypes() YIELD relationshipType
            MATCH ()-[r]->() WHERE type(r) = relationshipType
            RETURN relationshipType, count(r) AS c
            ORDER BY c DESC LIMIT 10
        """
        rel_types_res = await self._safe_traverse(rel_types_cypher, "telemetry_rel_types")
        relationship_types = {rec["relationshipType"]: rec["c"] for rec in rel_types_res}

        artifacts_cypher = "MATCH (a:KnowledgeArtifact) RETURN count(a) AS c"
        artifacts_res = await self._safe_traverse(artifacts_cypher, "telemetry_artifacts")
        total_artifacts = artifacts_res[0].get("c", 0) if artifacts_res else 0

        density = 0.0
        if total_nodes > 1:
            # Directed graph density: E / (V * (V - 1))
            density = total_rels / (total_nodes * (total_nodes - 1))

        canonical_payload = {
            "gridState": {
                "resonance": float(f"{avg_resonance:.4f}"),
                "confidence": float(f"{confidence:.2f}"),
                "lastCycle": last_cycle,
                "totalMoments": total_moments,
                "distinctInitiators": distinct_initiators,
                "totalNodes": total_nodes,
                "totalRelationships": total_rels,
                "moments24h": moments_24h,
                "totalArtifacts": total_artifacts,
                "graphDensity": float(f"{density:.6f}")
            },
            "agents": agents,
            "layer_nodes": layer_nodes,
            "relationship_types": relationship_types,
            "moments": {
                "recent": [dict(m) for m in recent_moments_raw],
                "soulMoments": [dict(m) for m in soul_raw],
                "mindMoments": [dict(m) for m in mind_raw],
                "bodyMoments": [dict(m) for m in body_raw]
            }
        }
        
        # Seal the payload
        canonical_payload["seal"] = self.mo.bless("canonical_telemetry")

        return canonical_payload

    async def get_graph_constellation(self, limit: int = 2000) -> dict:
        """
        Fetches nodes and relationships formatted for d3-force-graph.
        Returns { nodes: [{id, labels, resonance, ...}], links: [{source, target, rel}] }
        """
        nodes_cypher = f"""
            MATCH (n)
            // Broadened filter: Allow all non-internal labels
            WHERE NOT labels(n)[0] STARTS WITH '_'
            RETURN id(n) AS id, labels(n) AS labels, n.name AS name, n.description AS desc, 
                   n.resonance_score AS resonance, n.timestamp AS timestamp
            LIMIT 5000
        """
        nodes_records = await self._safe_traverse(nodes_cypher, "telemetry_constellation_nodes")
        
        nodes = []
        node_ids = set()
        for r in nodes_records:
            nid = r.get("id")
            nodes.append({
                "id": nid,
                "labels": r.get("labels", []),
                "name": r.get("name") or r.get("desc", "Unknown"),
                "resonance": float(r.get("resonance", 0.5) or 0.5),
                "timestamp": r.get("timestamp")
            })
            node_ids.add(nid)

        if not node_ids:
            return {"nodes": [], "links": []}

        # Fetch links between these nodes
        links_cypher = f"""
            MATCH (s)-[r]->(t)
            WHERE id(s) IN {list(node_ids)} AND id(t) IN {list(node_ids)}
            RETURN id(s) AS source, id(t) AS target, type(r) AS rel
            LIMIT {limit * 2}
        """
        links_records = await self._safe_traverse(links_cypher, "telemetry_constellation_links")
        
        links = []
        for r in links_records:
            links.append({
                "source": r.get("source"),
                "target": r.get("target"),
                "rel": r.get("rel")
            })

        return {"nodes": nodes, "links": links}

async def get_graph_constellation(limit: int = 2000):
    """Async wrapper."""
    engine = CanonicalTelemetryEngine()
    return await engine.get_graph_constellation(limit)

async def get_grid_telemetry():
    """Async wrapper for the external world to call."""
    engine = CanonicalTelemetryEngine()
    return await engine.get_grid_telemetry()

def get_grid_telemetry_sync():
    """Sync wrapper if needed."""
    return asyncio.run(get_grid_telemetry())
