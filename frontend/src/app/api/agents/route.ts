import { NextResponse } from 'next/server';
import { randomUUID } from 'crypto';
import { driver } from '../../../lib/neo4j';

export async function GET() {
  const ingestion_run_id = randomUUID();
  const timestamp = new Date().toISOString();

  if (!process.env.NEO4J_URI || !process.env.NEO4J_USER || !process.env.NEO4J_PASSWORD) {
    return NextResponse.json(
      {
        agents: [],
        count: 0,
        provenance: { source: 'error', timestamp, ingestion_run_id, error: 'Neo4j not configured' },
      },
      { status: 503 }
    );
  }

  const session = driver.session();
  try {
    const result = await session.run(`
      MATCH (a:Agent)
      OPTIONAL MATCH (a)-[:MANIFESTS]->(m:MoStarMoment)
      WITH a, collect(DISTINCT m) AS moments, coalesce(a.name, a.id, toString(id(a))) AS sortKey
      RETURN a, moments
      ORDER BY sortKey
      LIMIT 100
    `);

    const agents = result.records.map((record) => {
      const aNode = record.get('a') as unknown as {
        properties: Record<string, unknown>;
        identity: { toString(): string };
      };
      const moments = (record.get('moments') as unknown as Array<{ properties: Record<string, unknown> }> ) || [];

      const id = (aNode.properties['id'] as string) ?? aNode.identity.toString();

      return {
        id,
        ...aNode.properties,
        moments: moments.map((m) => m.properties),
        provenance: {
          source: 'neo4j',
          timestamp,
          upstream_id: aNode.identity.toString(),
          ingestion_run_id,
          confidence: 1.0,
        },
      };
    });

    return NextResponse.json({
      agents,
      count: agents.length,
      provenance: { source: 'neo4j', timestamp, ingestion_run_id },
    });
  } catch (error) {
    return NextResponse.json(
      {
        agents: [],
        count: 0,
        provenance: { source: 'error', timestamp, ingestion_run_id, error: error instanceof Error ? error.message : 'Unknown database error' },
      },
      { status: 503 }
    );
  } finally {
    await session.close();
  }
}
