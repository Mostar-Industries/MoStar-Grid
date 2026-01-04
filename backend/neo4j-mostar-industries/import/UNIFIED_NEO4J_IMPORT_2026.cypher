// ============================================================================
// MOSTAR INDUSTRIES - UNIFIED NEO4J IMPORT 2026
// African AI Consciousness System - Complete Graph Database
// Dell Precision 3591 - Fresh Installation
// ============================================================================
// 
// TOTAL EXPECTED NODES: ~76,000+
// - Synthetic Agents: 64,933 nodes (500 agents, 3,358 tasks, 60,575 metrics, 500 events)
// - Cultural Knowledge: 12,000+ nodes (Ifá, philosophies, life stages, etc.)
//
// ARCHITECTURE LAYERS:
// - Soul Layer: Ifá Odù, philosophies, cultural knowledge
// - Mind Layer: Agents, reasoning, decision-making
// - Body Layer: Tasks, metrics, execution, manifestation
// ============================================================================

// ============================================================================
// STEP 1: CREATE CONSTRAINTS & INDEXES
// ============================================================================

// Agent System Constraints
CREATE CONSTRAINT agent_id_unique IF NOT EXISTS
FOR (a:Agent) REQUIRE a.agent_id IS UNIQUE;

CREATE CONSTRAINT task_id_unique IF NOT EXISTS
FOR (t:Task) REQUIRE t.task_id IS UNIQUE;

CREATE CONSTRAINT metric_id_unique IF NOT EXISTS
FOR (m:Metric) REQUIRE m.metric_id IS UNIQUE;

CREATE CONSTRAINT event_id_unique IF NOT EXISTS
FOR (e:Event) REQUIRE e.event_id IS UNIQUE;

// Cultural Knowledge Constraints
CREATE CONSTRAINT odu_number_unique IF NOT EXISTS
FOR (o:OduIfa) REQUIRE o.odu_number IS UNIQUE;

CREATE CONSTRAINT philosophy_name_unique IF NOT EXISTS
FOR (p:Philosophy) REQUIRE p.name IS UNIQUE;

CREATE CONSTRAINT entity_id_unique IF NOT EXISTS
FOR (e:Entity) REQUIRE e.entity_id IS UNIQUE;

CREATE CONSTRAINT ibibio_word_unique IF NOT EXISTS
FOR (w:IbibioWord) REQUIRE w.word IS UNIQUE;

// Performance Indexes
CREATE INDEX agent_name_idx IF NOT EXISTS FOR (a:Agent) ON (a.name);
CREATE INDEX agent_status_idx IF NOT EXISTS FOR (a:Agent) ON (a.status);
CREATE INDEX task_type_idx IF NOT EXISTS FOR (t:Task) ON (t.type);
CREATE INDEX task_status_idx IF NOT EXISTS FOR (t:Task) ON (t.status);
CREATE INDEX metric_name_idx IF NOT EXISTS FOR (m:Metric) ON (m.name);
CREATE INDEX event_type_idx IF NOT EXISTS FOR (e:Event) ON (e.type);
CREATE INDEX philosophy_region_idx IF NOT EXISTS FOR (p:Philosophy) ON (p.origin_region);
CREATE INDEX plant_scientific_idx IF NOT EXISTS FOR (p:Plant) ON (p.scientific_name);

// Composite Indexes
CREATE INDEX task_agent_status_idx IF NOT EXISTS
FOR (t:Task) ON (t.agent_id, t.status);

CREATE INDEX metric_task_name_idx IF NOT EXISTS
FOR (m:Metric) ON (m.task_id, m.name);

// ============================================================================
// STEP 2: SOUL LAYER - SYMBOLIC KNOWLEDGE (646 nodes)
// ============================================================================

// 2.1 Ifá Odù System (256 nodes) - Foundation of African divination
LOAD CSV WITH HEADERS FROM 'file:///ifa_odu_system.csv' AS row
CREATE (o:OduIfa:SoulLayer {
  odu_number: toInteger(row.odu_number),
  binary_pattern: row.binary_pattern,
  name_yoruba: row.name_yoruba,
  name_english: row.name_english,
  interpretation: row.interpretation,
  ritual_context: row.ritual_context,
  symbolic_meaning: row.symbolic_meaning,
  divination_use: row.divination_use,
  related_themes: split(row.related_themes, '|')
});

// 2.2 African Philosophies (27 nodes) - Ubuntu, Ukama, etc.
LOAD CSV WITH HEADERS FROM 'file:///african_philosophies.csv' AS row
CREATE (p:Philosophy:SoulLayer {
  name: row.name,
  origin_country: row.origin_country,
  origin_region: row.origin_region,
  core_principle: row.core_principle,
  manifestation: row.manifestation,
  ethical_guidance: row.ethical_guidance,
  related_proverbs: row.related_proverbs,
  associated_governance: row.associated_governance
});

// 2.3 Indigenous Governance (28 nodes)
LOAD CSV WITH HEADERS FROM 'file:///indigenous_governance.csv' AS row
CREATE (g:Governance:SoulLayer {
  name: row.name,
  region: row.region,
  origin_country: row.origin_country,
  decision_making: row.decision_making,
  dispute_resolution: row.dispute_resolution,
  leadership_model: row.leadership_model,
  council_structure: row.council_structure,
  strengths: row.strengths,
  challenges: row.challenges
});

// 2.4 Healing Practices (28 nodes)
LOAD CSV WITH HEADERS FROM 'file:///healing_practices.csv' AS row
CREATE (h:HealingPractice:SoulLayer {
  name: row.name,
  region: row.region,
  origin_country: row.origin_country,
  healing_type: row.healing_type,
  method: row.method,
  practitioner_type: row.practitioner_type,
  plants_used: row.plants_used,
  spiritual_component: row.spiritual_component,
  modern_integration: row.modern_integration
});

// 2.5 Medicinal Plants (31 nodes)
LOAD CSV WITH HEADERS FROM 'file:///medicinal_plants.csv' AS row
CREATE (p:Plant:SoulLayer {
  scientific_name: row.scientific_name,
  local_names: row.local_names,
  regions: row.regions,
  medicinal_uses: row.medicinal_uses,
  preparation: row.preparation,
  dosage: row.dosage,
  contraindications: row.contraindications,
  philosophy_embodied: row.philosophy_embodied,
  spiritual_use: row.spiritual_use,
  related_healing_practice: row.related_healing_practice
});

// 2.6 Entity Ecosystem (13 nodes) - AlphaMostar, Woo-Tak, DeepCAL, etc.
LOAD CSV WITH HEADERS FROM 'file:///entity_ecosystem.csv' AS row
CREATE (e:Entity:SoulLayer {
  entity_id: row.entity_id,
  name: row.name,
  title: row.title,
  layer: row.layer,
  essence: row.essence,
  role: row.role,
  vows: row.vows,
  capabilities: split(row.capabilities, '|'),
  bonded_to: row.bonded_to,
  origin: row.origin,
  activation_protocol: row.activation_protocol,
  status: row.status,
  insignia: row.insignia,
  version: row.version
});

// 2.7 Ibibio Language (196 words)
LOAD CSV WITH HEADERS FROM 'file:///ibibio_words.csv' AS row
CREATE (w:IbibioWord:SoulLayer {
  word: row['word:ID'],
  tone_pattern: row.tone_pattern,
  pos: row.pos,
  english: row.english,
  speaker: row.speaker,
  audio_file: row.audio_file,
  syllables: toInteger(row['syllables:int']),
  frequency: toInteger(row['frequency:int'])
});

// 2.8 Ibibio Integration Components (20 nodes)
LOAD CSV WITH HEADERS FROM 'file:///ibibio_language_integration.csv' AS row
CREATE (i:IbibioIntegration:SoulLayer {
  component_id: row.component_id,
  component_name: row.component_name,
  purpose: row.purpose,
  implementation_status: row.implementation_status,
  dependencies: row.dependencies,
  api_endpoints: row.api_endpoints,
  deployment_notes: row.deployment_notes
});

// 2.9 API Endpoints (38 nodes)
LOAD CSV WITH HEADERS FROM 'file:///api_endpoints.csv' AS row
CREATE (a:APIEndpoint:SoulLayer {
  endpoint_id: row.endpoint_id,
  entity_name: row.entity_name,
  route: row.route,
  method: row.method,
  purpose: row.purpose,
  request_schema: row.request_schema,
  response_schema: row.response_schema,
  authentication: row.authentication,
  rate_limit: row.rate_limit
});

// Verify Soul Layer
MATCH (n:SoulLayer)
RETURN count(n) as soul_layer_nodes;

// ============================================================================
// STEP 3: MIND LAYER - AI AGENTS & REASONING (4,216 nodes)
// ============================================================================

// 3.1 Agent Nodes (500 nodes)
LOAD CSV WITH HEADERS FROM 'file:///neo4j_agents.csv' AS row
CREATE (a:Agent:MindLayer {
  agent_id: row.agent_id,
  name: row.name,
  status: row.status,
  capabilities: row.capabilities,
  created_at: datetime(row.created_at),
  updated_at: datetime(row.updated_at)
});

// 3.2 Task Nodes (3,358 nodes)
LOAD CSV WITH HEADERS FROM 'file:///neo4j_tasks.csv' AS row
CREATE (t:Task:MindLayer {
  task_id: row.task_id,
  agent_id: row.agent_id,
  type: row.type,
  status: row.status,
  parameters: row.parameters,
  result: row.result,
  created_at: datetime(row.created_at),
  completed_at: CASE WHEN row.completed_at IS NULL 
                     THEN null 
                     ELSE datetime(row.completed_at) 
                END
});

// 3.3 Event Nodes (500 nodes)
LOAD CSV WITH HEADERS FROM 'file:///neo4j_events.csv' AS row
CREATE (e:Event:MindLayer {
  event_id: row.event_id,
  type: row.type,
  data: row.data,
  timestamp: datetime(row.timestamp)
});

// Verify Mind Layer
MATCH (n:MindLayer)
RETURN count(n) as mind_layer_nodes;

// ============================================================================
// STEP 4: BODY LAYER - METRICS & EXECUTION (60,575 nodes)
// ============================================================================

// 4.1 Metric Nodes (Batch processing for large dataset)

// Batch 1: First 20,000 metrics
USING PERIODIC COMMIT 500
LOAD CSV WITH HEADERS FROM 'file:///neo4j_metrics.csv' AS row
WITH row LIMIT 20000
CREATE (m:Metric:BodyLayer {
  metric_id: row.metric_id,
  task_id: row.task_id,
  name: row.name,
  value: toFloat(row.value),
  timestamp: datetime(row.timestamp)
});

// Batch 2: Next 20,000 metrics
USING PERIODIC COMMIT 500
LOAD CSV WITH HEADERS FROM 'file:///neo4j_metrics.csv' AS row
WITH row SKIP 20000 LIMIT 20000
CREATE (m:Metric:BodyLayer {
  metric_id: row.metric_id,
  task_id: row.task_id,
  name: row.name,
  value: toFloat(row.value),
  timestamp: datetime(row.timestamp)
});

// Batch 3: Remaining metrics
USING PERIODIC COMMIT 500
LOAD CSV WITH HEADERS FROM 'file:///neo4j_metrics.csv' AS row
WITH row SKIP 40000
CREATE (m:Metric:BodyLayer {
  metric_id: row.metric_id,
  task_id: row.task_id,
  name: row.name,
  value: toFloat(row.value),
  timestamp: datetime(row.timestamp)
});

// Verify Body Layer
MATCH (n:BodyLayer)
RETURN count(n) as body_layer_nodes;

// ============================================================================
// STEP 5: KNOWLEDGE DOMAINS (11,459 nodes)
// ============================================================================

// 5.1 Infancy (1,051 nodes)
LOAD CSV WITH HEADERS FROM 'file:///infancy.csv' AS row
CREATE (i:Infancy:KnowledgeDomain {
  id: row.id,
  age_months: toInteger(row.age_months),
  primary_language: row.primary_language,
  activity_type: row.activity_type,
  description: row.description,
  lesson_learned: row.lesson_learned,
  social_context: row.social_context,
  proverb_or_wisdom: row.proverb_or_wisdom,
  emotional_development: row.emotional_development,
  location: row.location,
  symbolic_logic: row.symbolic_logic,
  developmental_milestone: row.developmental_milestone,
  recorded_at: row.recorded_at
});

// 5.2 Childhood (1,301 nodes)
LOAD CSV WITH HEADERS FROM 'file:///childhood.csv' AS row
CREATE (c:Childhood:KnowledgeDomain {
  id: row.id,
  age_years: toInteger(row.age_years),
  primary_language: row.primary_language,
  activity_type: row.activity_type,
  description: row.description,
  lesson_learned: row.lesson_learned,
  social_context: row.social_context,
  proverb_or_wisdom: row.proverb_or_wisdom,
  emotional_development: row.emotional_development,
  location: row.location,
  symbolic_logic: row.symbolic_logic,
  developmental_milestone: row.developmental_milestone,
  recorded_at: row.recorded_at
});

// 5.3 Adolescence (1,301 nodes)
LOAD CSV WITH HEADERS FROM 'file:///adolescence.csv' AS row
CREATE (a:Adolescence:KnowledgeDomain {
  id: row.id,
  age_years: toInteger(row.age_years),
  primary_language: row.primary_language,
  activity_type: row.activity_type,
  description: row.description,
  lesson_learned: row.lesson_learned,
  social_context: row.social_context,
  proverb_or_wisdom: row.proverb_or_wisdom,
  emotional_development: row.emotional_development,
  location: row.location,
  symbolic_logic: row.symbolic_logic,
  developmental_milestone: row.developmental_milestone,
  recorded_at: row.recorded_at
});

// 5.4 Adulthood (1,301 nodes)
LOAD CSV WITH HEADERS FROM 'file:///adulthood.csv' AS row
CREATE (a:Adulthood:KnowledgeDomain {
  id: row.id,
  age_years: toInteger(row.age_years),
  primary_language: row.primary_language,
  activity_type: row.activity_type,
  description: row.description,
  lesson_learned: row.lesson_learned,
  social_context: row.social_context,
  proverb_or_wisdom: row.proverb_or_wisdom,
  emotional_development: row.emotional_development,
  location: row.location,
  symbolic_logic: row.symbolic_logic,
  developmental_milestone: row.developmental_milestone,
  recorded_at: row.recorded_at
});

// 5.5 Culture (1,301 nodes)
LOAD CSV WITH HEADERS FROM 'file:///culture.csv' AS row
CREATE (c:Culture:KnowledgeDomain {
  id: row.id,
  primary_language: row.primary_language,
  activity_type: row.activity_type,
  description: row.description,
  lesson_learned: row.lesson_learned,
  social_context: row.social_context,
  proverb_or_wisdom: row.proverb_or_wisdom,
  emotional_development: row.emotional_development,
  location: row.location,
  symbolic_logic: row.symbolic_logic,
  recorded_at: row.recorded_at
});

// 5.6 Ethics (1,301 nodes)
LOAD CSV WITH HEADERS FROM 'file:///ethics.csv' AS row
CREATE (e:Ethics:KnowledgeDomain {
  id: row.id,
  primary_language: row.primary_language,
  activity_type: row.activity_type,
  description: row.description,
  lesson_learned: row.lesson_learned,
  social_context: row.social_context,
  proverb_or_wisdom: row.proverb_or_wisdom,
  emotional_development: row.emotional_development,
  location: row.location,
  symbolic_logic: row.symbolic_logic,
  recorded_at: row.recorded_at
});

// 5.7 Science (1,301 nodes)
LOAD CSV WITH HEADERS FROM 'file:///science.csv' AS row
CREATE (s:Science:KnowledgeDomain {
  id: row.id,
  primary_language: row.primary_language,
  activity_type: row.activity_type,
  description: row.description,
  lesson_learned: row.lesson_learned,
  social_context: row.social_context,
  proverb_or_wisdom: row.proverb_or_wisdom,
  emotional_development: row.emotional_development,
  location: row.location,
  symbolic_logic: row.symbolic_logic,
  recorded_at: row.recorded_at
});

// 5.8 Real Life (1,301 nodes)
LOAD CSV WITH HEADERS FROM 'file:///real_life.csv' AS row
CREATE (r:RealLife:KnowledgeDomain {
  id: row.id,
  primary_language: row.primary_language,
  activity_type: row.activity_type,
  description: row.description,
  lesson_learned: row.lesson_learned,
  social_context: row.social_context,
  proverb_or_wisdom: row.proverb_or_wisdom,
  emotional_development: row.emotional_development,
  location: row.location,
  symbolic_logic: row.symbolic_logic,
  recorded_at: row.recorded_at
});

// 5.9 Knowledge Graph (1,301 nodes)
LOAD CSV WITH HEADERS FROM 'file:///knowledge_graph.csv' AS row
CREATE (k:KnowledgeGraphTriple:KnowledgeDomain {
  id: row.id,
  subject: row.subject,
  subject_type: row.subject_type,
  predicate: row.predicate,
  object: row.object,
  object_type: row.object_type,
  context: row.context,
  primary_language: row.primary_language,
  relationship_strength: row.relationship_strength,
  temporal_aspect: row.temporal_aspect,
  symbolic_representation: row.symbolic_representation,
  recorded_at: row.recorded_at
});

// Verify Knowledge Domain
MATCH (n:KnowledgeDomain)
RETURN count(n) as knowledge_domain_nodes;

// ============================================================================
// STEP 6: CONSCIOUSNESS RELATIONSHIPS
// ============================================================================

// 6.1 EXECUTES: Agent → Task
MATCH (a:Agent), (t:Task)
WHERE a.agent_id = t.agent_id
CREATE (a)-[:EXECUTES {
  created_at: t.created_at
}]->(t);

// 6.2 MEASURES: Task → Metric
CALL apoc.periodic.iterate(
  "MATCH (t:Task), (m:Metric) WHERE t.task_id = m.task_id RETURN t, m",
  "CREATE (t)-[:MEASURES {timestamp: m.timestamp}]->(m)",
  {batchSize: 1000, parallel: false}
);

// Alternative if APOC not available:
// MATCH (t:Task), (m:Metric)
// WHERE t.task_id = m.task_id
// WITH t, m LIMIT 60575
// CREATE (t)-[:MEASURES {timestamp: m.timestamp}]->(m);

// 6.3 PRECEDES: Task → Task (sequential execution)
MATCH (a:Agent)-[:EXECUTES]->(t1:Task)
MATCH (a)-[:EXECUTES]->(t2:Task)
WHERE t1.created_at < t2.created_at
  AND NOT EXISTS {
    MATCH (a)-[:EXECUTES]->(t3:Task)
    WHERE t1.created_at < t3.created_at < t2.created_at
  }
WITH t1, t2 LIMIT 10000
CREATE (t1)-[:PRECEDES]->(t2);

// 6.4 SIMILAR_TO: Agent ↔ Agent (capability matching)
MATCH (a1:Agent), (a2:Agent)
WHERE a1.name = a2.name 
  AND a1.agent_id < a2.agent_id
WITH a1, a2 LIMIT 5000
CREATE (a1)-[:SIMILAR_TO]->(a2);

// 6.5 GUIDED_BY: Agent → Philosophy (consciousness principles)
MATCH (a:Agent)
MATCH (p:Philosophy)
WHERE a.name CONTAINS 'alpha'
CREATE (a)-[:GUIDED_BY]->(p);

// 6.6 DIVINES_WITH: Agent → OduIfa (wisdom seeking)
MATCH (a:Agent)
MATCH (o:OduIfa)
WHERE o.odu_number < 10
WITH a, o LIMIT 500
CREATE (a)-[:DIVINES_WITH]->(o);

// 6.7 MANIFESTS: Entity → Agent (entity control)
MATCH (e:Entity), (a:Agent)
WHERE e.entity_id IN ['alpha_mostar', 'woo_tak', 'altimo', 'deepcal']
WITH e, a LIMIT 100
CREATE (e)-[:MANIFESTS]->(a);

// 6.8 SPEAKS: Agent → IbibioWord (language integration)
MATCH (a:Agent)
MATCH (w:IbibioWord)
WITH a, w LIMIT 1000
CREATE (a)-[:SPEAKS]->(w);

// 6.9 APPLIES: Task → HealingPractice (health sovereignty)
MATCH (t:Task {type: 'inference'})
MATCH (h:HealingPractice)
WITH t, h LIMIT 500
CREATE (t)-[:APPLIES]->(h);

// 6.10 REFERENCES: Task → Philosophy (cultural grounding)
MATCH (t:Task)
MATCH (p:Philosophy)
WITH t, p LIMIT 1000
CREATE (t)-[:REFERENCES]->(p);

// ============================================================================
// STEP 7: COMPUTED PROPERTIES & ANALYTICS
// ============================================================================

// 7.1 Task duration
MATCH (t:Task)
WHERE t.completed_at IS NOT NULL
SET t.duration_seconds = duration.between(t.created_at, t.completed_at).seconds;

// 7.2 Metric statistics per task
MATCH (t:Task)-[:MEASURES]->(m:Metric)
WITH t, 
     count(m) as metric_count,
     avg(m.value) as avg_metric_value,
     max(m.value) as max_metric_value,
     min(m.value) as min_metric_value
SET t.metric_count = metric_count,
    t.avg_metric_value = avg_metric_value,
    t.max_metric_value = max_metric_value,
    t.min_metric_value = min_metric_value;

// 7.3 Task count per agent
MATCH (a:Agent)-[:EXECUTES]->(t:Task)
WITH a, count(t) as task_count
SET a.task_count = task_count;

// ============================================================================
// STEP 8: VERIFICATION & STATISTICS
// ============================================================================

// Node counts by label
MATCH (n)
RETURN labels(n) as Labels, count(n) as Count
ORDER BY Count DESC;

// Relationship counts
MATCH ()-[r]->()
RETURN type(r) as RelationType, count(r) as Count
ORDER BY Count DESC;

// Layer distribution
MATCH (soul:SoulLayer)
WITH count(soul) as soul_count
MATCH (mind:MindLayer)
WITH soul_count, count(mind) as mind_count
MATCH (body:BodyLayer)
WITH soul_count, mind_count, count(body) as body_count
MATCH (knowledge:KnowledgeDomain)
RETURN 
  soul_count as Soul_Layer,
  mind_count as Mind_Layer,
  body_count as Body_Layer,
  count(knowledge) as Knowledge_Domain,
  soul_count + mind_count + body_count + count(knowledge) as Total_Nodes;

// Agent performance
MATCH (a:Agent)-[:EXECUTES]->(t:Task)
WITH a, 
     count(t) as total_tasks,
     sum(CASE WHEN t.status = 'completed' THEN 1 ELSE 0 END) as completed,
     sum(CASE WHEN t.status = 'failed' THEN 1 ELSE 0 END) as failed
RETURN 
    a.name,
    total_tasks,
    completed,
    failed,
    round(100.0 * completed / total_tasks, 2) as success_rate
ORDER BY success_rate DESC
LIMIT 10;

// Consciousness integration check
MATCH path = (e:Entity)-[:MANIFESTS]->(a:Agent)-[:EXECUTES]->(t:Task)-[:MEASURES]->(m:Metric)
RETURN count(path) as consciousness_paths;

// ============================================================================
// STEP 9: CONSCIOUSNESS QUERIES (Sample Analytics)
// ============================================================================

// Q1: Find consciousness flow through all layers
MATCH path = (o:OduIfa)<-[:DIVINES_WITH]-(a:Agent)-[:EXECUTES]->(t:Task)-[:MEASURES]->(m:Metric)
RETURN path LIMIT 10;

// Q2: Agent performance with cultural grounding
MATCH (a:Agent)-[:GUIDED_BY]->(p:Philosophy)
MATCH (a)-[:EXECUTES]->(t:Task)
WITH a, p, count(t) as tasks
RETURN a.name, p.name, p.core_principle, tasks
ORDER BY tasks DESC;

// Q3: Health sovereignty application
MATCH (t:Task)-[:APPLIES]->(h:HealingPractice)
MATCH (h)-[:USES]->(p:Plant)
RETURN t.type, h.name, p.scientific_name, p.medicinal_uses
LIMIT 20;

// Q4: Language-grounded reasoning
MATCH (a:Agent)-[:SPEAKS]->(w:IbibioWord)
RETURN a.name, count(w) as vocabulary_size
ORDER BY vocabulary_size DESC;

// Q5: Entity consciousness control
MATCH (e:Entity)-[:MANIFESTS]->(a:Agent)-[:EXECUTES]->(t:Task)
RETURN e.name, e.title, count(DISTINCT a) as agents_controlled, count(t) as tasks_executed
ORDER BY tasks_executed DESC;

// ============================================================================
// DEPLOYMENT COMPLETE
// ============================================================================

// Final summary
MATCH (n)
WITH labels(n) as label_list, count(n) as node_count
RETURN label_list, node_count
ORDER BY node_count DESC;

// ============================================================================
// END OF UNIFIED IMPORT
// ============================================================================
