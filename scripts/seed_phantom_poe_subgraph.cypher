// Phantom POE subgraph seed
// Clean compartment using POE_* labels only

// -------------------------------------------------------------------
// Constraints and indexes
// -------------------------------------------------------------------
CREATE CONSTRAINT poe_run_uid IF NOT EXISTS
FOR (n:POE_Run) REQUIRE n.uid IS UNIQUE;

CREATE CONSTRAINT poe_node_uid IF NOT EXISTS
FOR (n:POE_Node) REQUIRE n.uid IS UNIQUE;

CREATE CONSTRAINT poe_signal_uid IF NOT EXISTS
FOR (n:POE_Signal) REQUIRE n.uid IS UNIQUE;

CREATE CONSTRAINT poe_corridor_uid IF NOT EXISTS
FOR (n:POE_Corridor) REQUIRE n.uid IS UNIQUE;

CREATE CONSTRAINT poe_entropy_uid IF NOT EXISTS
FOR (n:POE_Entropy) REQUIRE n.uid IS UNIQUE;

CREATE CONSTRAINT poe_moment_uid IF NOT EXISTS
FOR (n:POE_Moment) REQUIRE n.uid IS UNIQUE;

CREATE INDEX poe_signal_workspace IF NOT EXISTS
FOR (n:POE_Signal) ON (n.workspace);

CREATE INDEX poe_corridor_workspace IF NOT EXISTS
FOR (n:POE_Corridor) ON (n.workspace);

CREATE INDEX poe_moment_workspace IF NOT EXISTS
FOR (n:POE_Moment) ON (n.workspace);

// -------------------------------------------------------------------
// Run node
// -------------------------------------------------------------------
WITH
  datetime() AS now,
  "phantom-poe" AS workspace,
  "mo-border-phantom-001" AS system,
  "RUN-PHANTOM-2026-04-08-0001" AS runId,
  "phantom-poe-engine" AS source,
  "run-RUN-PHANTOM-2026-04-08-0001" AS sourceRecordId,
  "v1.0.0" AS normalizationVersion
MERGE (run:POE_Run {uid: workspace + "|run|" + runId})
SET
  run.runId = runId,
  run.workspace = workspace,
  run.system = system,
  run.source = source,
  run.sourceRecordId = sourceRecordId,
  run.ingestedAt = coalesce(run.ingestedAt, now),
  run.updatedAt = now,
  run.normalizationVersion = normalizationVersion,
  run.engine = "phantom-poe-engine",
  run.status = "completed",
  run.seedMode = "partitioned",
  run.createdBy = "codex";

// -------------------------------------------------------------------
// POE nodes (anchors + formal POE references)
// -------------------------------------------------------------------
UNWIND [
  {id: "NODE-KE-LWANDA", name: "Lwanda", lat: -1.2790, lng: 34.1450, type: "anchor", risk: "HIGH"},
  {id: "NODE-TZ-BUNDA", name: "Bunda", lat: -2.0430, lng: 33.8710, type: "anchor", risk: "HIGH"},
  {id: "NODE-UG-ISHASHA", name: "Ishasha", lat: -0.9440, lng: 29.6250, type: "anchor", risk: "MEDIUM"},
  {id: "NODE-CD-RUTSHURU", name: "Rutshuru", lat: -1.1900, lng: 29.4440, type: "anchor", risk: "MEDIUM"},
  {id: "NODE-TZ-SONGEA", name: "Songea", lat: -10.6820, lng: 35.6500, type: "anchor", risk: "LOW"},
  {id: "NODE-MZ-LICHINGA", name: "Lichinga", lat: -13.3120, lng: 35.2410, type: "anchor", risk: "LOW"},
  {id: "NODE-POE-KE-SIRARI", name: "Sirari Formal POE", lat: -1.2520, lng: 34.4760, type: "formal_poe", risk: "LOW"},
  {id: "NODE-POE-UG-BUNAGANA", name: "Bunagana Formal POE", lat: -1.2850, lng: 29.5920, type: "formal_poe", risk: "LOW"},
  {id: "NODE-POE-TZ-SONGEA", name: "Songea Formal POE", lat: -10.6820, lng: 35.6500, type: "formal_poe", risk: "LOW"}
] AS n
WITH
  n,
  datetime() AS now,
  "phantom-poe" AS workspace,
  "mo-border-phantom-001" AS system,
  "RUN-PHANTOM-2026-04-08-0001" AS runId,
  "geo-registry" AS source,
  "v1.0.0" AS normalizationVersion
MERGE (node:POE_Node {uid: workspace + "|node|" + n.id})
SET
  node.nodeId = n.id,
  node.id = n.id,
  node.name = n.name,
  node.lat = n.lat,
  node.lng = n.lng,
  node.type = n.type,
  node.risk = n.risk,
  node.workspace = workspace,
  node.system = system,
  node.runId = runId,
  node.source = source,
  node.sourceRecordId = "node-" + n.id,
  node.ingestedAt = coalesce(node.ingestedAt, now),
  node.updatedAt = now,
  node.normalizationVersion = normalizationVersion;

// -------------------------------------------------------------------
// Corridors
// -------------------------------------------------------------------
UNWIND [
  {
    id: "CORRIDOR-KE-TZ-047",
    short: "KE-TZ-047",
    region: "Lwanda -> Bunda (KE/TZ border)",
    score: 0.7887,
    riskClass: "HIGH",
    activated: true,
    latentState: "active",
    startNode: "NODE-KE-LWANDA",
    endNode: "NODE-TZ-BUNDA",
    startCC: "KE",
    endCC: "TZ",
    mode: "mixed-foot-road",
    velocity: "moderate",
    totalKm: 111.9,
    seasonal: "wet-season-amplified",
    canoe: false,
    detour: true,
    nearestFormalPOE: "Sirari Formal POE",
    gapZone: true,
    firstDetected: "2026-04-04T06:20:00Z",
    source: "phantom-poe-engine"
  },
  {
    id: "CORRIDOR-UG-CD-018",
    short: "UG-CD-018",
    region: "Ishasha -> Rutshuru (UG/CD border)",
    score: 0.5834,
    riskClass: "MEDIUM",
    activated: true,
    latentState: "active",
    startNode: "NODE-UG-ISHASHA",
    endNode: "NODE-CD-RUTSHURU",
    startCC: "UG",
    endCC: "CD",
    mode: "foot-track",
    velocity: "slow",
    totalKm: 32.4,
    seasonal: "stable",
    canoe: false,
    detour: false,
    nearestFormalPOE: "Bunagana Formal POE",
    gapZone: true,
    firstDetected: "2026-04-05T02:05:00Z",
    source: "phantom-poe-engine"
  },
  {
    id: "CORRIDOR-TZ-MZ-031",
    short: "TZ-MZ-031",
    region: "Songea -> Lichinga (TZ/MZ border)",
    score: 0.2341,
    riskClass: "LOW",
    activated: false,
    latentState: "dormant",
    startNode: "NODE-TZ-SONGEA",
    endNode: "NODE-MZ-LICHINGA",
    startCC: "TZ",
    endCC: "MZ",
    mode: "road",
    velocity: "intermittent",
    totalKm: 293.8,
    seasonal: "dry-season-limited",
    canoe: false,
    detour: false,
    nearestFormalPOE: "Songea Formal POE",
    gapZone: false,
    firstDetected: "2026-04-01T11:15:00Z",
    source: "phantom-poe-engine"
  }
] AS c
WITH
  c,
  datetime() AS now,
  "phantom-poe" AS workspace,
  "mo-border-phantom-001" AS system,
  "RUN-PHANTOM-2026-04-08-0001" AS runId,
  "v1.0.0" AS normalizationVersion
MERGE (corr:POE_Corridor {uid: workspace + "|corridor|" + c.id})
SET
  corr.corridorId = c.id,
  corr.id = c.id,
  corr.short = c.short,
  corr.region = c.region,
  corr.score = c.score,
  corr.riskClass = c.riskClass,
  corr.activated = c.activated,
  corr.latentState = c.latentState,
  corr.startNode = c.startNode,
  corr.endNode = c.endNode,
  corr.startCC = c.startCC,
  corr.endCC = c.endCC,
  corr.mode = c.mode,
  corr.velocity = c.velocity,
  corr.totalKm = c.totalKm,
  corr.seasonal = c.seasonal,
  corr.canoe = c.canoe,
  corr.detour = c.detour,
  corr.nearestFormalPOE = c.nearestFormalPOE,
  corr.gapZone = c.gapZone,
  corr.firstDetected = c.firstDetected,
  corr.timestamp = now,
  corr.workspace = workspace,
  corr.system = system,
  corr.runId = runId,
  corr.source = c.source,
  corr.sourceRecordId = "corridor-" + c.id,
  corr.ingestedAt = coalesce(corr.ingestedAt, now),
  corr.updatedAt = now,
  corr.normalizationVersion = normalizationVersion,
  corr.soulGravity = CASE c.id WHEN "CORRIDOR-KE-TZ-047" THEN 0.73 WHEN "CORRIDOR-UG-CD-018" THEN 0.52 ELSE 0.21 END,
  corr.soulDiffusion = CASE c.id WHEN "CORRIDOR-KE-TZ-047" THEN 0.81 WHEN "CORRIDOR-UG-CD-018" THEN 0.60 ELSE 0.19 END,
  corr.soulCentrality = CASE c.id WHEN "CORRIDOR-KE-TZ-047" THEN 0.77 WHEN "CORRIDOR-UG-CD-018" THEN 0.58 ELSE 0.28 END,
  corr.soulHMM = CASE c.id WHEN "CORRIDOR-KE-TZ-047" THEN 0.84 WHEN "CORRIDOR-UG-CD-018" THEN 0.57 ELSE 0.15 END,
  corr.soulSeasonal = CASE c.id WHEN "CORRIDOR-KE-TZ-047" THEN 0.69 WHEN "CORRIDOR-UG-CD-018" THEN 0.44 ELSE 0.30 END,
  corr.soulLinguistic = CASE c.id WHEN "CORRIDOR-KE-TZ-047" THEN 0.63 WHEN "CORRIDOR-UG-CD-018" THEN 0.49 ELSE 0.22 END,
  corr.soulEntropy = CASE c.id WHEN "CORRIDOR-KE-TZ-047" THEN 0.79 WHEN "CORRIDOR-UG-CD-018" THEN 0.53 ELSE 0.18 END,
  corr.soulTerrain = CASE c.id WHEN "CORRIDOR-KE-TZ-047" THEN 0.56 WHEN "CORRIDOR-UG-CD-018" THEN 0.61 ELSE 0.40 END;

// Attach run + start/end node links for corridors
UNWIND [
  {id: "CORRIDOR-KE-TZ-047", startNode: "NODE-KE-LWANDA", endNode: "NODE-TZ-BUNDA"},
  {id: "CORRIDOR-UG-CD-018", startNode: "NODE-UG-ISHASHA", endNode: "NODE-CD-RUTSHURU"},
  {id: "CORRIDOR-TZ-MZ-031", startNode: "NODE-TZ-SONGEA", endNode: "NODE-MZ-LICHINGA"}
] AS c
WITH c, "phantom-poe" AS workspace, "RUN-PHANTOM-2026-04-08-0001" AS runId
MATCH (run:POE_Run {uid: workspace + "|run|" + runId})
MATCH (corr:POE_Corridor {uid: workspace + "|corridor|" + c.id})
MATCH (startNode:POE_Node {uid: workspace + "|node|" + c.startNode})
MATCH (endNode:POE_Node {uid: workspace + "|node|" + c.endNode})
MERGE (run)-[:POE_PRODUCED]->(corr)
MERGE (corr)-[:POE_STARTS_AT]->(startNode)
MERGE (corr)-[:POE_ENDS_AT]->(endNode);

// -------------------------------------------------------------------
// Signals
// -------------------------------------------------------------------
UNWIND [
  {id: "SIG-KE-TZ-001", corridorId: "CORRIDOR-KE-TZ-047", nodeId: "NODE-KE-LWANDA", source: "AFRO Sentinel", sourceRecordId: "AFRO-100421", type: "disease", truthScore: 0.91, locationConfidence: "HIGH", timestamp: "2026-04-08T03:10:00Z", lat: -1.271, lng: 34.160},
  {id: "SIG-KE-TZ-002", corridorId: "CORRIDOR-KE-TZ-047", nodeId: "NODE-TZ-BUNDA", source: "DHIS2/EWARS", sourceRecordId: "EWARS-882711", type: "disease", truthScore: 0.83, locationConfidence: "MEDIUM", timestamp: "2026-04-08T03:26:00Z", lat: -2.051, lng: 33.860},
  {id: "SIG-KE-TZ-003", corridorId: "CORRIDOR-KE-TZ-047", nodeId: "NODE-KE-LWANDA", source: "IOM DTM", sourceRecordId: "DTM-53011", type: "displacement", truthScore: 0.79, locationConfidence: "MEDIUM", timestamp: "2026-04-08T04:15:00Z", lat: -1.295, lng: 34.140},
  {id: "SIG-KE-TZ-004", corridorId: "CORRIDOR-KE-TZ-047", nodeId: "NODE-TZ-BUNDA", source: "ACLED", sourceRecordId: "ACLED-99173", type: "conflict", truthScore: 0.72, locationConfidence: "MEDIUM", timestamp: "2026-04-08T04:52:00Z", lat: -2.030, lng: 33.890},

  {id: "SIG-UG-CD-001", corridorId: "CORRIDOR-UG-CD-018", nodeId: "NODE-UG-ISHASHA", source: "AFRO Sentinel", sourceRecordId: "AFRO-100519", type: "disease", truthScore: 0.80, locationConfidence: "MEDIUM", timestamp: "2026-04-08T00:45:00Z", lat: -0.948, lng: 29.632},
  {id: "SIG-UG-CD-002", corridorId: "CORRIDOR-UG-CD-018", nodeId: "NODE-CD-RUTSHURU", source: "IOM DTM", sourceRecordId: "DTM-54109", type: "displacement", truthScore: 0.74, locationConfidence: "MEDIUM", timestamp: "2026-04-08T01:05:00Z", lat: -1.174, lng: 29.435},
  {id: "SIG-UG-CD-003", corridorId: "CORRIDOR-UG-CD-018", nodeId: "NODE-CD-RUTSHURU", source: "ACLED", sourceRecordId: "ACLED-99204", type: "conflict", truthScore: 0.66, locationConfidence: "LOW", timestamp: "2026-04-08T01:22:00Z", lat: -1.196, lng: 29.451},
  {id: "SIG-UG-CD-004", corridorId: "CORRIDOR-UG-CD-018", nodeId: "NODE-UG-ISHASHA", source: "DHIS2/EWARS", sourceRecordId: "EWARS-882920", type: "disease", truthScore: 0.77, locationConfidence: "MEDIUM", timestamp: "2026-04-08T01:33:00Z", lat: -0.940, lng: 29.615},

  {id: "SIG-TZ-MZ-001", corridorId: "CORRIDOR-TZ-MZ-031", nodeId: "NODE-TZ-SONGEA", source: "AFRO Sentinel", sourceRecordId: "AFRO-100601", type: "disease", truthScore: 0.76, locationConfidence: "HIGH", timestamp: "2026-04-07T11:30:00Z", lat: -10.679, lng: 35.645},
  {id: "SIG-TZ-MZ-002", corridorId: "CORRIDOR-TZ-MZ-031", nodeId: "NODE-MZ-LICHINGA", source: "IOM DTM", sourceRecordId: "DTM-55201", type: "displacement", truthScore: 0.70, locationConfidence: "LOW", timestamp: "2026-04-07T12:15:00Z", lat: -13.298, lng: 35.255},
  {id: "SIG-TZ-MZ-003", corridorId: "CORRIDOR-TZ-MZ-031", nodeId: "NODE-MZ-LICHINGA", source: "ACLED", sourceRecordId: "ACLED-99297", type: "conflict", truthScore: 0.65, locationConfidence: "LOW", timestamp: "2026-04-07T12:38:00Z", lat: -13.321, lng: 35.232},
  {id: "SIG-TZ-MZ-004", corridorId: "CORRIDOR-TZ-MZ-031", nodeId: "NODE-TZ-SONGEA", source: "DHIS2/EWARS", sourceRecordId: "EWARS-883115", type: "disease", truthScore: 0.75, locationConfidence: "MEDIUM", timestamp: "2026-04-07T13:02:00Z", lat: -10.691, lng: 35.658}
] AS s
WITH
  s,
  datetime() AS now,
  "phantom-poe" AS workspace,
  "mo-border-phantom-001" AS system,
  "RUN-PHANTOM-2026-04-08-0001" AS runId,
  "v1.0.0" AS normalizationVersion
MERGE (sig:POE_Signal {uid: workspace + "|signal|" + s.id})
SET
  sig.signalId = s.id,
  sig.id = s.id,
  sig.corridorId = s.corridorId,
  sig.type = s.type,
  sig.truthScore = s.truthScore,
  sig.locationConfidence = s.locationConfidence,
  sig.timestamp = datetime(s.timestamp),
  sig.lat = s.lat,
  sig.lng = s.lng,
  sig.status = CASE WHEN s.truthScore >= 0.75 THEN "validated" ELSE "watch" END,
  sig.workspace = workspace,
  sig.system = system,
  sig.runId = runId,
  sig.source = s.source,
  sig.sourceRecordId = s.sourceRecordId,
  sig.ingestedAt = coalesce(sig.ingestedAt, now),
  sig.updatedAt = now,
  sig.normalizationVersion = normalizationVersion;

// Signal relationships
UNWIND [
  {id: "SIG-KE-TZ-001", corridorId: "CORRIDOR-KE-TZ-047", nodeId: "NODE-KE-LWANDA"},
  {id: "SIG-KE-TZ-002", corridorId: "CORRIDOR-KE-TZ-047", nodeId: "NODE-TZ-BUNDA"},
  {id: "SIG-KE-TZ-003", corridorId: "CORRIDOR-KE-TZ-047", nodeId: "NODE-KE-LWANDA"},
  {id: "SIG-KE-TZ-004", corridorId: "CORRIDOR-KE-TZ-047", nodeId: "NODE-TZ-BUNDA"},
  {id: "SIG-UG-CD-001", corridorId: "CORRIDOR-UG-CD-018", nodeId: "NODE-UG-ISHASHA"},
  {id: "SIG-UG-CD-002", corridorId: "CORRIDOR-UG-CD-018", nodeId: "NODE-CD-RUTSHURU"},
  {id: "SIG-UG-CD-003", corridorId: "CORRIDOR-UG-CD-018", nodeId: "NODE-CD-RUTSHURU"},
  {id: "SIG-UG-CD-004", corridorId: "CORRIDOR-UG-CD-018", nodeId: "NODE-UG-ISHASHA"},
  {id: "SIG-TZ-MZ-001", corridorId: "CORRIDOR-TZ-MZ-031", nodeId: "NODE-TZ-SONGEA"},
  {id: "SIG-TZ-MZ-002", corridorId: "CORRIDOR-TZ-MZ-031", nodeId: "NODE-MZ-LICHINGA"},
  {id: "SIG-TZ-MZ-003", corridorId: "CORRIDOR-TZ-MZ-031", nodeId: "NODE-MZ-LICHINGA"},
  {id: "SIG-TZ-MZ-004", corridorId: "CORRIDOR-TZ-MZ-031", nodeId: "NODE-TZ-SONGEA"}
] AS s
WITH s, "phantom-poe" AS workspace, "RUN-PHANTOM-2026-04-08-0001" AS runId
MATCH (run:POE_Run {uid: workspace + "|run|" + runId})
MATCH (sig:POE_Signal {uid: workspace + "|signal|" + s.id})
MATCH (node:POE_Node {uid: workspace + "|node|" + s.nodeId})
MATCH (corr:POE_Corridor {uid: workspace + "|corridor|" + s.corridorId})
MERGE (run)-[:POE_INGESTED]->(sig)
MERGE (sig)-[:POE_LOCATED_AT]->(node)
MERGE (corr)-[:POE_CONTAINS_SIGNAL]->(sig);

// -------------------------------------------------------------------
// Entropy alerts
// -------------------------------------------------------------------
UNWIND [
  {id: "ENT-KE-TZ-047", corridorId: "CORRIDOR-KE-TZ-047", nodeId: "NODE-KE-LWANDA", entropyShift: 0.67, confidence: 0.86, timestamp: "2026-04-08T05:01:00Z"},
  {id: "ENT-UG-CD-018", corridorId: "CORRIDOR-UG-CD-018", nodeId: "NODE-UG-ISHASHA", entropyShift: 0.41, confidence: 0.74, timestamp: "2026-04-08T01:44:00Z"},
  {id: "ENT-TZ-MZ-031", corridorId: "CORRIDOR-TZ-MZ-031", nodeId: "NODE-TZ-SONGEA", entropyShift: 0.18, confidence: 0.57, timestamp: "2026-04-07T13:30:00Z"}
] AS e
WITH
  e,
  datetime() AS now,
  "phantom-poe" AS workspace,
  "mo-border-phantom-001" AS system,
  "RUN-PHANTOM-2026-04-08-0001" AS runId,
  "entropy-engine" AS source,
  "v1.0.0" AS normalizationVersion
MERGE (ent:POE_Entropy {uid: workspace + "|entropy|" + e.id})
SET
  ent.entropyId = e.id,
  ent.id = e.id,
  ent.corridorId = e.corridorId,
  ent.entropyShift = e.entropyShift,
  ent.confidence = e.confidence,
  ent.timestamp = datetime(e.timestamp),
  ent.workspace = workspace,
  ent.system = system,
  ent.runId = runId,
  ent.source = source,
  ent.sourceRecordId = "entropy-" + e.id,
  ent.ingestedAt = coalesce(ent.ingestedAt, now),
  ent.updatedAt = now,
  ent.normalizationVersion = normalizationVersion;

UNWIND [
  {id: "ENT-KE-TZ-047", nodeId: "NODE-KE-LWANDA"},
  {id: "ENT-UG-CD-018", nodeId: "NODE-UG-ISHASHA"},
  {id: "ENT-TZ-MZ-031", nodeId: "NODE-TZ-SONGEA"}
] AS e
WITH e, "phantom-poe" AS workspace, "RUN-PHANTOM-2026-04-08-0001" AS runId
MATCH (run:POE_Run {uid: workspace + "|run|" + runId})
MATCH (ent:POE_Entropy {uid: workspace + "|entropy|" + e.id})
MATCH (node:POE_Node {uid: workspace + "|node|" + e.nodeId})
MERGE (run)-[:POE_PRODUCED]->(ent)
MERGE (ent)-[:POE_ALERT_ON]->(node);

// -------------------------------------------------------------------
// Trinity moments
// -------------------------------------------------------------------
UNWIND [
  {id: "MOMENT-KE-TZ-047", corridorId: "CORRIDOR-KE-TZ-047", scriptId: "mo-signal-ingest-001", wooState: "PERMITTED", sealedAt: "2026-04-08T05:08:00Z", summary: "Active high-risk corridor validated"},
  {id: "MOMENT-UG-CD-018", corridorId: "CORRIDOR-UG-CD-018", scriptId: "mo-corridor-detect-001", wooState: "PERMITTED", sealedAt: "2026-04-08T01:55:00Z", summary: "Active medium-risk corridor validated"},
  {id: "MOMENT-TZ-MZ-031", corridorId: "CORRIDOR-TZ-MZ-031", scriptId: "mo-trinity-synthesis-001", wooState: "PERMITTED", sealedAt: "2026-04-07T13:36:00Z", summary: "Dormant low-risk corridor monitored"}
] AS m
WITH
  m,
  datetime() AS now,
  "phantom-poe" AS workspace,
  "mo-border-phantom-001" AS system,
  "RUN-PHANTOM-2026-04-08-0001" AS runId,
  "mo-script-engine" AS source,
  "v1.0.0" AS normalizationVersion
MERGE (moment:POE_Moment {uid: workspace + "|moment|" + m.id})
SET
  moment.momentId = m.id,
  moment.id = m.id,
  moment.corridorId = m.corridorId,
  moment.scriptId = m.scriptId,
  moment.wooState = m.wooState,
  moment.sealedAt = datetime(m.sealedAt),
  moment.summary = m.summary,
  moment.workspace = workspace,
  moment.system = system,
  moment.runId = runId,
  moment.source = source,
  moment.sourceRecordId = "moment-" + m.id,
  moment.ingestedAt = coalesce(moment.ingestedAt, now),
  moment.updatedAt = now,
  moment.normalizationVersion = normalizationVersion;

UNWIND [
  {id: "MOMENT-KE-TZ-047", corridorId: "CORRIDOR-KE-TZ-047"},
  {id: "MOMENT-UG-CD-018", corridorId: "CORRIDOR-UG-CD-018"},
  {id: "MOMENT-TZ-MZ-031", corridorId: "CORRIDOR-TZ-MZ-031"}
] AS m
WITH m, "phantom-poe" AS workspace, "RUN-PHANTOM-2026-04-08-0001" AS runId
MATCH (run:POE_Run {uid: workspace + "|run|" + runId})
MATCH (moment:POE_Moment {uid: workspace + "|moment|" + m.id})
MATCH (corr:POE_Corridor {uid: workspace + "|corridor|" + m.corridorId})
MERGE (run)-[:POE_PRODUCED]->(moment)
MERGE (moment)-[:POE_SYNTHESIZES]->(corr);

