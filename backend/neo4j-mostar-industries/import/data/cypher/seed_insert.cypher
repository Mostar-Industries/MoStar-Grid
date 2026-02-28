// Minimal seed insert for three moments from 2026-01-04
CREATE CONSTRAINT IF NOT EXISTS FOR (m:Moment) REQUIRE m.id IS UNIQUE;
MERGE (m:Moment {id:'MM_372cf7516e'})
SET m.date='2026-01-04', m.kind='milestone', m.title='Kickoff: MoStar Grid mind graph design', m.narrative='Established scope to model MoStar moments; requested full memory; constraints noted (no cross-session memory).', m.confidence='High', m.impact=3;
MERGE (a:Actor {name:'user'}) MERGE (a)-[:INVOLVED_IN]->(m);
MERGE (a:Actor {name:'TsaTse Fly'}) MERGE (a)-[:INVOLVED_IN]->(m);
MERGE (p:Project {name:'MoStar Grid'}) MERGE (m)-[:BELONGS_TO]->(p);
MERGE (t:Tag {name:'setup'}) MERGE (m)-[:TAGGED_AS]->(t);
MERGE (t:Tag {name:'neo4j'}) MERGE (m)-[:TAGGED_AS]->(t);
MERGE (t:Tag {name:'design'}) MERGE (m)-[:TAGGED_AS]->(t);
MERGE (m:Moment {id:'MM_cc0de9e904'})
SET m.date='2026-01-04', m.kind='build', m.title='Delivered bootstrap pack (Python registry + Neo4j Cypher)', m.narrative='Provided Mostar_Moment.py and neo4j schema/import pack via canvas.', m.confidence='High', m.impact=4;
MERGE (a:Actor {name:'user'}) MERGE (a)-[:INVOLVED_IN]->(m);
MERGE (a:Actor {name:'TsaTse Fly'}) MERGE (a)-[:INVOLVED_IN]->(m);
MERGE (p:Project {name:'MoStar Grid'}) MERGE (m)-[:BELONGS_TO]->(p);
MERGE (t:Tag {name:'build'}) MERGE (m)-[:TAGGED_AS]->(t);
MERGE (t:Tag {name:'python'}) MERGE (m)-[:TAGGED_AS]->(t);
MERGE (t:Tag {name:'cypher'}) MERGE (m)-[:TAGGED_AS]->(t);
MERGE (m:Moment {id:'MM_712c62f754'})
SET m.date='2026-01-04', m.kind='ingest', m.title='Imported DCP corpus (PDFs)', m.narrative='Ingested 7 DCP PDFs into workspace for potential linkage to health-sovereignty tracks.', m.confidence='Medium', m.impact=2;
MERGE (a:Actor {name:'user'}) MERGE (a)-[:INVOLVED_IN]->(m);
MERGE (p:Project {name:'MoStar Grid'}) MERGE (m)-[:BELONGS_TO]->(p);
MERGE (t:Tag {name:'assets'}) MERGE (m)-[:TAGGED_AS]->(t);
MERGE (t:Tag {name:'health'}) MERGE (m)-[:TAGGED_AS]->(t);
MERGE (t:Tag {name:'DCP'}) MERGE (m)-[:TAGGED_AS]->(t);
MATCH (s:Moment {id:'MM_372cf7516e'}), (d:Moment {id:'MM_cc0de9e904'}) MERGE (s)-[:PRECEDES]->(d);
MATCH (s:Moment {id:'MM_cc0de9e904'}), (d:Moment {id:'MM_712c62f754'}) MERGE (s)-[:RELATES_TO]->(d);
