import { randomUUID } from 'crypto';
import { NextResponse } from 'next/server';
import { driver } from '../../../../lib/neo4j';

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const ingestion_run_id = randomUUID();
  const timestamp = new Date().toISOString();
  const { id } = await params;
  const agentId = id;

  if (!process.env.NEO4J_URI || !process.env.NEO4J_USER || !process.env.NEO4J_PASSWORD) {
    return NextResponse.json(
      {
        agent: null,
        provenance: { source: 'error', timestamp, ingestion_run_id, error: 'Neo4j not configured' },
      },
      { status: 503 }
    );
  }

  const session = driver.session();
  try {
    const result = await session.run(
      `
      MATCH (a:Agent {id: $id})
      OPTIONAL MATCH (a)-[:MANIFESTS]->(m:MoStarMoment)
      RETURN a, collect(DISTINCT m) AS moments
      `,
      { id: agentId }
    );

    if (result.records.length === 0) {
      return NextResponse.json(
        {
          agent: null,
          provenance: { source: 'error', timestamp, ingestion_run_id, error: 'Agent not found' },
        },
        { status: 404 }
      );
    }

    const record = result.records[0];
    const aNode = record.get('a') as unknown as {
      properties: Record<string, unknown>;
      identity: { toString(): string };
    };
    const moments = (record.get('moments') as unknown as Array<{ properties: Record<string, unknown> }>) || [];

    const id = (aNode.properties['id'] as string) ?? aNode.identity.toString();

    const agent = {
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

    return NextResponse.json({
      agent,
      provenance: { source: 'neo4j', timestamp, ingestion_run_id },
    });
  } catch (error) {
    return NextResponse.json(
      {
        agent: null,
        provenance: { source: 'error', timestamp, ingestion_run_id, error: error instanceof Error ? error.message : 'Unknown database error' },
      },
      { status: 503 }
    );
  } finally {
    await session.close();
  }
}
