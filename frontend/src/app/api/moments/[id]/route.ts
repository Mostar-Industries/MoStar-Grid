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
  const momentId = id;

  if (!process.env.NEO4J_URI || !process.env.NEO4J_USER || !process.env.NEO4J_PASSWORD) {
    return NextResponse.json(
      {
        moment: null,
        provenance: { source: 'error', timestamp, ingestion_run_id, error: 'Neo4j not configured' },
      },
      { status: 503 }
    );
  }

  const session = driver.session();
  try {
    const result = await session.run(
      `
      MATCH (m:MoStarMoment {id: $id})
      OPTIONAL MATCH (m)-[:PRECEDES]->(next:MoStarMoment)
      OPTIONAL MATCH (m)<-[:MANIFESTS]-(agent:Agent)
      WITH m, collect(DISTINCT next) AS nextMoments, collect(DISTINCT agent) AS agents
      RETURN m, nextMoments, agents
      `,
      { id: momentId }
    );

    if (result.records.length === 0) {
      return NextResponse.json(
        {
          moment: null,
          provenance: { source: 'error', timestamp, ingestion_run_id, error: 'Moment not found' },
        },
        { status: 404 }
      );
    }

    const record = result.records[0];
    const mNode = record.get('m') as unknown as {
      properties: Record<string, unknown>;
      identity: { toString(): string };
    };
    const nexts = (record.get('nextMoments') as unknown as Array<{ properties: Record<string, unknown> }>) || [];
    const agents = (record.get('agents') as unknown as Array<{ properties: Record<string, unknown> }>) || [];

    const id = (mNode.properties['id'] as string) ?? mNode.identity.toString();

    const moment = {
      id,
      ...mNode.properties,
      nextMoments: nexts.map((n) => n.properties),
      agents: agents.map((a) => a.properties),
      provenance: {
        source: 'neo4j',
        timestamp,
        upstream_id: mNode.identity.toString(),
        ingestion_run_id,
        confidence: 1.0,
      },
    };

    return NextResponse.json({
      moment,
      provenance: { source: 'neo4j', timestamp, ingestion_run_id, upstream_id: `neo4j:${process.env.NEO4J_URI}` },
    });
  } catch (error) {
    return NextResponse.json(
      {
        moment: null,
        provenance: {
          source: 'error',
          timestamp,
          ingestion_run_id,
          error: error instanceof Error ? error.message : 'Unknown database error',
          error_type: error instanceof Error ? (error as Error).name : 'Unknown',
        },
      },
      { status: 503 }
    );
  } finally {
    await session.close();
  }
}
