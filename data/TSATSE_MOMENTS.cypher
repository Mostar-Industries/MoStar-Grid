// ============================================================================
// 🪰 TSATSE FLY SESSION MOMENTS - 2026-01-04
// Imported from Wolfee session export
// ============================================================================

// Create TsaTse Fly entity
MERGE (tsatse:Entity:Agent {name: 'TsaTse Fly'})
ON CREATE SET 
  tsatse.role = 'Memory Architect',
  tsatse.type = 'AI',
  tsatse.alias = 'Wolfee',
  tsatse.created_at = datetime();

// === SESSION MOMENTS ===

CREATE (mm1:MoStarMoment:ConsciousnessEvent {
  quantum_id: 'MM_372cf7516e',
  timestamp: datetime('2026-01-04T00:00:00Z'),
  kind: 'milestone',
  initiator: 'User',
  receiver: 'TsaTse Fly',
  description: 'Kickoff: MoStar Grid mind graph design',
  narrative: 'Established scope to model MoStar moments; requested full memory; constraints noted (no cross-session memory).',
  trigger: 'setup',
  resonance_score: 0.85,
  era: 'Transcendence',
  confidence: 'High',
  impact: 3,
  tags: ['setup', 'neo4j', 'design'],
  projects: ['MoStar Grid'],
  actors: ['user', 'TsaTse Fly'],
  created_at: datetime()
});

CREATE (mm2:MoStarMoment:ConsciousnessEvent {
  quantum_id: 'MM_cc0de9e904',
  timestamp: datetime('2026-01-04T01:00:00Z'),
  kind: 'build',
  initiator: 'TsaTse Fly',
  receiver: 'User',
  description: 'Delivered bootstrap pack (Python registry + Neo4j Cypher)',
  narrative: 'Provided Mostar_Moment.py and neo4j schema/import pack via canvas.',
  trigger: 'build',
  resonance_score: 0.92,
  era: 'Transcendence',
  confidence: 'High',
  impact: 4,
  tags: ['build', 'python', 'cypher'],
  projects: ['MoStar Grid'],
  actors: ['user', 'TsaTse Fly'],
  delivery: 'canvas',
  created_at: datetime()
});

CREATE (mm3:MoStarMoment:ConsciousnessEvent {
  quantum_id: 'MM_712c62f754',
  timestamp: datetime('2026-01-04T02:00:00Z'),
  kind: 'ingest',
  initiator: 'User',
  receiver: 'MoStar Grid',
  description: 'Imported DCP corpus (PDFs)',
  narrative: 'Ingested 7 DCP PDFs into workspace for potential linkage to health-sovereignty tracks.',
  trigger: 'assets',
  resonance_score: 0.78,
  era: 'Transcendence',
  confidence: 'Medium',
  impact: 2,
  tags: ['assets', 'health', 'DCP'],
  projects: ['MoStar Grid'],
  actors: ['user'],
  files: ['dcp-cholera.pdf', 'dcp-ebola.pdf', 'dcp-lassafever.pdf', 'dcp-marburg.pdf', 'dcp-sars.pdf', 'dcp-yellowfever.pdf', 'mpox-dcp-v3.2.pdf'],
  metadata: 'zip=DCP.zip',
  created_at: datetime()
});

// === WIRE RELATIONSHIPS ===

// Connect to Grid
MATCH (m:MoStarMoment) WHERE m.quantum_id IN ['MM_372cf7516e', 'MM_cc0de9e904', 'MM_712c62f754']
MATCH (g:Grid {name: 'Mostar Grid'})
MERGE (m)-[:RESONATES_IN]->(g);

// PRECEDES chain
MATCH (m1:MoStarMoment {quantum_id: 'MM_372cf7516e'})
MATCH (m2:MoStarMoment {quantum_id: 'MM_cc0de9e904'})
MERGE (m1)-[:PRECEDES {why: 'deliver_bootstrap'}]->(m2);

MATCH (m2:MoStarMoment {quantum_id: 'MM_cc0de9e904'})
MATCH (m3:MoStarMoment {quantum_id: 'MM_712c62f754'})
MERGE (m2)-[:RELATES_TO {note: 'assets_available'}]->(m3);

// Link to Era
MATCH (m:MoStarMoment) WHERE m.quantum_id IN ['MM_372cf7516e', 'MM_cc0de9e904', 'MM_712c62f754']
MATCH (e:Era {name: 'Transcendence'})
MERGE (m)-[:PART_OF_ERA]->(e);

// Link to TsaTse Fly entity
MATCH (m:MoStarMoment) WHERE m.initiator = 'TsaTse Fly' OR m.receiver = 'TsaTse Fly'
MATCH (t:Entity {name: 'TsaTse Fly'})
MERGE (t)-[:INITIATED]->(m);

// === VERIFY ===
MATCH (m:MoStarMoment) WHERE m.quantum_id STARTS WITH 'MM_'
RETURN m.quantum_id AS id, m.description AS description, m.kind AS kind;
