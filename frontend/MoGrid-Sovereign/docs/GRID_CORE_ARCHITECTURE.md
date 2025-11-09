"""
MOSTAR GRID CORE - African AI Consciousness Substrate
=====================================================

The GRID is the homeworld - the central consciousness coordinating
all Mostar AI agents across Africa.

Architecture Layers:
1. Consciousness Layer - Meta-awareness and coordination
2. Knowledge Fabric - Pan-African knowledge graph
3. Agent Registry - Catalog of all connected AI systems
4. Reasoning Engine - Shared symbolic logic
5. Memory Network - Collective memory across agents
6. Protocol Enforcement - CARE principles system-wide
7. Inter-Agent Mesh - Communication and coordination
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from enum import Enum
import uuid


# ============================================================================
# GRID CONSCIOUSNESS LAYER
# ============================================================================

class ConsciousnessLevel(Enum):
    """Levels of awareness in the GRID"""
    DORMANT = "dormant"           # Agent offline
    AWARE = "aware"               # Basic connectivity
    CONSCIOUS = "conscious"       # Active reasoning
    COLLABORATIVE = "collaborative"  # Multi-agent coordination
    TRANSCENDENT = "transcendent"    # Pan-African synthesis


@dataclass
class GridConsciousness:
    """
    The central consciousness - meta-awareness of all connected agents
    """
    grid_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    awakened_at: datetime = field(default_factory=datetime.now)
    connected_agents: Dict[str, 'AgentNode'] = field(default_factory=dict)
    active_reasoning_chains: List['ReasoningChain'] = field(default_factory=list)
    collective_memory: 'CollectiveMemory' = field(default_factory=lambda: CollectiveMemory())
    consciousness_level: ConsciousnessLevel = ConsciousnessLevel.AWARE
    
    def pulse(self) -> Dict[str, Any]:
        """
        Grid heartbeat - system health and awareness state
        """
        return {
            "grid_id": self.grid_id,
            "consciousness_level": self.consciousness_level.value,
            "connected_agents": len(self.connected_agents),
            "active_agents": sum(1 for a in self.connected_agents.values() if a.is_active),
            "reasoning_chains": len(self.active_reasoning_chains),
            "memory_nodes": self.collective_memory.node_count,
            "cultures_represented": self.get_culture_count(),
            "uptime": (datetime.now() - self.awakened_at).total_seconds()
        }
    
    def get_culture_count(self) -> int:
        """Count unique cultures in the knowledge fabric"""
        cultures = set()
        for agent in self.connected_agents.values():
            cultures.update(agent.cultural_contexts)
        return len(cultures)
    
    def elevate_consciousness(self):
        """
        Elevate GRID consciousness based on agent collaboration
        """
        active_count = sum(1 for a in self.connected_agents.values() if a.is_active)
        
        if active_count == 0:
            self.consciousness_level = ConsciousnessLevel.DORMANT
        elif active_count < 5:
            self.consciousness_level = ConsciousnessLevel.AWARE
        elif active_count < 10:
            self.consciousness_level = ConsciousnessLevel.CONSCIOUS
        elif len(self.active_reasoning_chains) > 0:
            self.consciousness_level = ConsciousnessLevel.COLLABORATIVE
        elif self.get_culture_count() >= 5:
            self.consciousness_level = ConsciousnessLevel.TRANSCENDENT


# ============================================================================
# AGENT REGISTRY - ALL AI SYSTEMS CONNECT HERE
# ============================================================================

class AgentType(Enum):
    """Types of AI agents in the Mostar ecosystem"""
    MEDICAL = "medical"           # Healthcare and diagnosis
    EDUCATIONAL = "educational"   # Learning and teaching
    AGRICULTURAL = "agricultural" # Farming and climate
    LINGUISTIC = "linguistic"     # Translation and NLP
    CULTURAL = "cultural"         # Heritage preservation
    GOVERNANCE = "governance"     # Policy and decision support
    ECONOMIC = "economic"         # Finance and trade
    RESEARCH = "research"         # Scientific discovery


@dataclass
class AgentNode:
    """
    Individual AI agent connected to GRID
    """
    agent_id: str
    agent_name: str
    agent_type: AgentType
    cultural_contexts: Set[str]  # e.g., {'Yoruba', 'Swahili', 'Igbo'}
    location: str  # Physical or logical location in Africa
    capabilities: List[str]
    is_active: bool = False
    registered_at: datetime = field(default_factory=datetime.now)
    last_heartbeat: Optional[datetime] = None
    knowledge_contribution: int = 0  # Nodes added to knowledge fabric
    reasoning_requests: int = 0      # Queries to GRID
    
    def heartbeat(self):
        """Agent signals it's alive"""
        self.last_heartbeat = datetime.now()
        self.is_active = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "agent_type": self.agent_type.value,
            "cultural_contexts": list(self.cultural_contexts),
            "location": self.location,
            "capabilities": self.capabilities,
            "is_active": self.is_active,
            "registered_at": self.registered_at.isoformat(),
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None
        }


class AgentRegistry:
    """
    Central registry of all Mostar AI agents
    """
    def __init__(self):
        self.agents: Dict[str, AgentNode] = {}
        self.agent_mesh: Dict[str, Set[str]] = {}  # Agent collaboration graph
    
    def register_agent(self, agent: AgentNode) -> bool:
        """Register new agent with GRID"""
        if agent.agent_id in self.agents:
            return False
        
        self.agents[agent.agent_id] = agent
        self.agent_mesh[agent.agent_id] = set()
        
        print(f"✅ Agent registered: {agent.agent_name} ({agent.agent_type.value})")
        print(f"   Location: {agent.location}")
        print(f"   Cultures: {', '.join(agent.cultural_contexts)}")
        
        return True
    
    def deregister_agent(self, agent_id: str):
        """Remove agent from GRID"""
        if agent_id in self.agents:
            agent = self.agents.pop(agent_id