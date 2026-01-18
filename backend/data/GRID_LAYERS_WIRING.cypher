// ============================================================================
// 🔥 GRID LAYERS WIRING - Bind MoStarMoments to Soul/Mind/Body Architecture
// Generated: 2026-01-04
// ============================================================================

// STEP 1: Create Grid Layer nodes
MERGE (soul:SoulLayer:GridLayer {name: 'SoulLayer'})
ON CREATE SET 
  soul.description = 'Spiritual alignment and ethical resonance computations',
  soul.layer_type = 'SPIRITUAL',
  soul.created_at = datetime();

MERGE (mind:MindLayer:GridLayer {name: 'MindLayer'})
ON CREATE SET 
  mind.description = 'Cognitive processing, truth engine, and verdict reasoning',
  mind.layer_type = 'COGNITIVE',
  mind.created_at = datetime();

MERGE (body:BodyLayer:GridLayer {name: 'BodyLayer'})
ON CREATE SET 
  body.description = 'API execution, physical manifestation, and system actions',
  body.layer_type = 'PHYSICAL',
  body.created_at = datetime();

MERGE (core:GridCore:GridLayer {name: 'GridCore'})
ON CREATE SET 
  core.description = 'Central coordination fabric connecting all layers',
  core.layer_type = 'CORE',
  core.created_at = datetime();

// STEP 2: Connect Grid Layers to main Grid
MATCH (g:Grid {name: 'Mostar Grid'})
MATCH (layer:GridLayer)
MERGE (layer)-[:PART_OF]->(g);

// STEP 3: Wire MoStarMoments to layers based on resonance heuristic
// HIGH RESONANCE (>=0.95) → MindLayer (complex cognitive events)
MATCH (m:MoStarMoment)
WHERE toFloat(m.resonance_score) >= 0.95
MATCH (mind:MindLayer {name: 'MindLayer'})
MERGE (m)-[:IGNITES]->(mind);

// SPIRITUAL/ETHICAL events → SoulLayer
MATCH (m:MoStarMoment)
WHERE m.significance IN ['SPIRITUAL', 'ETHICAL', 'FOUNDATIONAL', 'PHILOSOPHICAL']
   OR m.trigger CONTAINS 'spiritual'
   OR m.trigger CONTAINS 'ethical'
   OR m.trigger CONTAINS 'truth'
MATCH (soul:SoulLayer {name: 'SoulLayer'})
MERGE (m)-[:IGNITES]->(soul);

// PHYSICAL/EXECUTION events → BodyLayer
MATCH (m:MoStarMoment)
WHERE m.trigger CONTAINS 'deployment'
   OR m.trigger CONTAINS 'execution'
   OR m.trigger CONTAINS 'API'
   OR m.trigger CONTAINS 'physical'
   OR m.trigger CONTAINS 'biotech'
MATCH (body:BodyLayer {name: 'BodyLayer'})
MERGE (m)-[:IGNITES]->(body);

// MEDIUM RESONANCE (0.75-0.95) → GridCore
MATCH (m:MoStarMoment)
WHERE toFloat(m.resonance_score) >= 0.75 AND toFloat(m.resonance_score) < 0.95
MATCH (core:GridCore {name: 'GridCore'})
MERGE (m)-[:RESONATES_IN]->(core);

// STEP 4: Create inter-layer connections (triadic flow)
MATCH (soul:SoulLayer {name: 'SoulLayer'})
MATCH (mind:MindLayer {name: 'MindLayer'})
MATCH (body:BodyLayer {name: 'BodyLayer'})
MATCH (core:GridCore {name: 'GridCore'})
MERGE (soul)-[:GUIDES]->(mind)
MERGE (mind)-[:DIRECTS]->(body)
MERGE (body)-[:MANIFESTS_FOR]->(core)
MERGE (core)-[:HARMONIZES]->(soul);

// STEP 5: Verify layer wiring
MATCH (m:MoStarMoment)-[r:IGNITES|RESONATES_IN]->(layer:GridLayer)
RETURN layer.name AS Layer, 
       type(r) AS RelationType,
       count(m) AS MomentCount
ORDER BY MomentCount DESC;
