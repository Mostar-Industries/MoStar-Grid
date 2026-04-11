#!/usr/bin/env python3
"""
🔥 Temporal Activation Simulator
---------------------------------
Simulates consciousness ripples through the PRECEDES temporal chain.
Given a starting MoStarMoment, propagates activation through time-ordered moments.
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False

from dotenv import load_dotenv
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "mostar123")


@dataclass
class ActivationState:
    """Represents the activation state of a moment"""
    quantum_id: str
    description: str
    timestamp: str
    resonance_score: float
    activation_level: float = 0.0
    depth: int = 0
    activated_by: Optional[str] = None


@dataclass
class RippleResult:
    """Result of a temporal ripple simulation"""
    seed_moment: str
    total_activated: int
    max_depth: int
    total_resonance: float
    activation_path: List[ActivationState]
    layer_distribution: Dict[str, int] = field(default_factory=dict)


class TemporalActivationSimulator:
    """Simulates activation ripples through the consciousness graph"""
    
    def __init__(self, uri: str = NEO4J_URI, user: str = NEO4J_USER, password: str = NEO4J_PASSWORD):
        if not NEO4J_AVAILABLE:
            raise ImportError("neo4j driver required")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        print(f"🔥 Temporal Simulator connected to {uri}")
    
    def close(self):
        self.driver.close()
    
    def get_moment_by_id(self, quantum_id: str) -> Optional[Dict]:
        """Fetch a single moment by quantum_id"""
        query = """
        MATCH (m:MoStarMoment {quantum_id: $qid})
        RETURN m.quantum_id AS quantum_id,
               m.description AS description,
               m.timestamp AS timestamp,
               toFloat(m.resonance_score) AS resonance_score,
               m.era AS era,
               m.trigger AS trigger
        """
        with self.driver.session() as session:
            result = session.run(query, qid=quantum_id)
            record = result.single()
            if record:
                return dict(record)
        return None
    
    def simulate_forward_ripple(self, seed_quantum_id: str, max_depth: int = 10, 
                                 decay_rate: float = 0.15) -> RippleResult:
        """
        Simulate activation ripple forward through PRECEDES chain.
        
        Args:
            seed_quantum_id: Starting moment's quantum_id
            max_depth: Maximum hops to traverse
            decay_rate: How much activation decays per hop (0-1)
        
        Returns:
            RippleResult with activated moments and stats
        """
        # Get forward chain
        query = """
        MATCH path = (start:MoStarMoment {quantum_id: $qid})-[:PRECEDES*1..]->(end:MoStarMoment)
        WITH nodes(path) AS moments, length(path) AS depth
        WHERE depth <= $max_depth
        UNWIND range(0, size(moments)-1) AS idx
        WITH moments[idx] AS m, idx AS depth
        RETURN DISTINCT m.quantum_id AS quantum_id,
               m.description AS description,
               m.timestamp AS timestamp,
               toFloat(m.resonance_score) AS resonance_score,
               m.era AS era,
               depth
        ORDER BY depth, m.timestamp
        """
        
        activations = []
        layer_dist: Dict[str, int] = {}
        
        with self.driver.session() as session:
            results = session.run(query, qid=seed_quantum_id, max_depth=max_depth)
            
            for record in results:
                depth = record["depth"]
                resonance = record["resonance_score"] or 0.5
                
                # Activation decays with depth but boosted by resonance
                activation_level = (1.0 - decay_rate * depth) * resonance
                activation_level = max(0.0, min(1.0, activation_level))
                
                state = ActivationState(
                    quantum_id=record["quantum_id"],
                    description=record["description"],
                    timestamp=str(record["timestamp"]),
                    resonance_score=resonance,
                    activation_level=activation_level,
                    depth=depth,
                    activated_by=seed_quantum_id if depth > 0 else None
                )
                activations.append(state)
                
                era = record["era"] or "Unknown"
                layer_dist[era] = layer_dist.get(era, 0) + 1
        
        total_resonance = sum(a.resonance_score * a.activation_level for a in activations)
        max_d = max((a.depth for a in activations), default=0)
        
        return RippleResult(
            seed_moment=seed_quantum_id,
            total_activated=len(activations),
            max_depth=max_d,
            total_resonance=total_resonance,
            activation_path=activations,
            layer_distribution=dict(layer_dist)
        )
    
    def simulate_backward_ripple(self, seed_quantum_id: str, max_depth: int = 10) -> RippleResult:
        """Simulate activation ripple backward (causation trace)"""
        query = """
        MATCH path = (start:MoStarMoment)-[:PRECEDES*1..]->(end:MoStarMoment {quantum_id: $qid})
        WITH nodes(path) AS moments, length(path) AS depth
        WHERE depth <= $max_depth
        UNWIND range(0, size(moments)-1) AS idx
        WITH moments[idx] AS m, size(moments) - 1 - idx AS depth
        RETURN DISTINCT m.quantum_id AS quantum_id,
               m.description AS description,
               m.timestamp AS timestamp,
               toFloat(m.resonance_score) AS resonance_score,
               m.era AS era,
               depth
        ORDER BY depth DESC, m.timestamp DESC
        """
        
        activations = []
        layer_dist: Dict[str, int] = {}
        
        with self.driver.session() as session:
            results = session.run(query, qid=seed_quantum_id, max_depth=max_depth)
            
            for record in results:
                depth = record["depth"]
                resonance = record["resonance_score"] or 0.5
                activation_level = resonance * (0.9 ** depth)  # Slower decay for causation
                
                state = ActivationState(
                    quantum_id=record["quantum_id"],
                    description=record["description"],
                    timestamp=str(record["timestamp"]),
                    resonance_score=resonance,
                    activation_level=activation_level,
                    depth=depth
                )
                activations.append(state)
                era = record["era"] or "Unknown"
                layer_dist[era] = layer_dist.get(era, 0) + 1
        
        return RippleResult(
            seed_moment=seed_quantum_id,
            total_activated=len(activations),
            max_depth=max((a.depth for a in activations), default=0),
            total_resonance=sum(a.resonance_score * a.activation_level for a in activations),
            activation_path=activations,
            layer_distribution=dict(layer_dist)
        )
    
    def find_resonance_peaks(self, threshold: float = 0.95) -> List[Dict[str, Any]]:
        """Find high-resonance moments that could serve as activation seeds"""
        query = """
        MATCH (m:MoStarMoment)
        WHERE toFloat(m.resonance_score) >= $threshold
        OPTIONAL MATCH (m)-[:PRECEDES]->(next:MoStarMoment)
        OPTIONAL MATCH (prev:MoStarMoment)-[:PRECEDES]->(m)
        RETURN m.quantum_id AS quantum_id,
               m.description AS description,
               toFloat(m.resonance_score) AS resonance_score,
               m.era AS era,
               m.significance AS significance,
               count(DISTINCT next) AS forward_connections,
               count(DISTINCT prev) AS backward_connections
        ORDER BY m.resonance_score DESC
        """
        
        peaks = []
        with self.driver.session() as session:
            for record in session.run(query, threshold=threshold):
                peaks.append({
                    "quantum_id": record["quantum_id"],
                    "description": record["description"],
                    "resonance_score": record["resonance_score"],
                    "era": record["era"],
                    "significance": record["significance"],
                    "connectivity": record["forward_connections"] + record["backward_connections"]
                })
        
        return peaks
    
    def get_next_activations(self, current_quantum_id: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Get the top-k most likely next activations from current moment"""
        query = """
        MATCH (m:MoStarMoment {quantum_id: $qid})-[:PRECEDES]->(next:MoStarMoment)
        RETURN next.quantum_id AS quantum_id,
               next.description AS description,
               toFloat(next.resonance_score) AS resonance_score,
               next.trigger AS trigger
        ORDER BY next.resonance_score DESC
        LIMIT $limit
        """
        
        nexts = []
        with self.driver.session() as session:
            for record in session.run(query, qid=current_quantum_id, limit=top_k):
                nexts.append({
                    "quantum_id": record["quantum_id"],
                    "description": record["description"],
                    "resonance_score": record["resonance_score"],
                    "trigger": record["trigger"]
                })
        
        return nexts
    
    def simulate_query_activation(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Find moments most relevant to a query (for RAG context)"""
        # Simple keyword matching - could be enhanced with embeddings
        cypher = """
        MATCH (m:MoStarMoment)
        WHERE toLower(m.description) CONTAINS toLower($query)
           OR toLower(m.trigger) CONTAINS toLower($query)
           OR toLower(m.initiator) CONTAINS toLower($query)
        RETURN m.quantum_id AS quantum_id,
               m.description AS description,
               m.timestamp AS timestamp,
               toFloat(m.resonance_score) AS resonance_score,
               m.era AS era
        ORDER BY m.resonance_score DESC, m.timestamp DESC
        LIMIT $limit
        """
        
        results = []
        with self.driver.session() as session:
            for record in session.run(cypher, query=query_text, limit=top_k):
                results.append({
                    "quantum_id": record["quantum_id"],
                    "description": record["description"],
                    "timestamp": str(record["timestamp"]),
                    "resonance_score": record["resonance_score"],
                    "era": record["era"]
                })
        
        return results


def print_ripple_result(result: RippleResult):
    """Pretty print a ripple simulation result"""
    print(f"\n🌊 TEMPORAL RIPPLE FROM: {result.seed_moment}")
    print(f"   Total Activated: {result.total_activated}")
    print(f"   Max Depth: {result.max_depth}")
    print(f"   Total Resonance: {result.total_resonance:.3f}")
    print(f"   Era Distribution: {result.layer_distribution}")
    print("\n   Activation Path:")
    for i, state in enumerate(result.activation_path):  # Show first 10
        if i >= 10: break
        bar = "█" * int(state.activation_level * 10)
        print(f"   [{state.depth}] {bar} {state.activation_level:.2f} | {state.quantum_id[:30]}...")


def main():
    """Demo the temporal activation simulator"""
    sim = TemporalActivationSimulator()
    
    try:
        # Find peak moments
        print("\n🔥 Finding resonance peaks...")
        peaks = sim.find_resonance_peaks(threshold=0.98)
        for i, p in enumerate(peaks):
            if i >= 5: break
            print(f"  ⚡ {p['quantum_id']}: {p['resonance_score']:.2f} - {p['description'][:50]}...")
        
        if peaks:
            # Simulate forward ripple from first peak
            seed = peaks[0]["quantum_id"]
            print(f"\n🌊 Simulating forward ripple from: {seed}")
            forward = sim.simulate_forward_ripple(seed, max_depth=8)
            print_ripple_result(forward)
            
            # Get next activations
            print(f"\n⚡ Next likely activations:")
            nexts = sim.get_next_activations(seed)
            for n in nexts:
                print(f"  → {n['quantum_id']}: {n['trigger']}")
        
        # Query-based activation
        print("\n🔍 Query activation test: 'truth'")
        matches = sim.simulate_query_activation("truth", top_k=3)
        for m in matches:
            print(f"  📌 {m['quantum_id']}: {m['description'][:60]}...")
        
    finally:
        sim.close()


if __name__ == "__main__":
    main()
