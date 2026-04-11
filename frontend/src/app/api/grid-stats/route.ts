/**
 * 🔥 Grid Stats API - LIVE Neo4j Connection
 * Returns real-time statistics from Mostar Grid
 */

import { NextResponse } from 'next/server';
import neo4j, { Driver } from 'neo4j-driver';

let driver: Driver | null = null;

function getDriver(): Driver {
  if (!driver) {
    driver = neo4j.driver(
      process.env.NEO4J_URI || 'bolt://localhost:7687',
      neo4j.auth.basic(
        process.env.NEO4J_USER || 'neo4j',
        process.env.NEO4J_PASSWORD || 'mostar123'
      ),
      { disableLosslessIntegers: true }
    );
  }
  return driver;
}

export async function GET() {
  const session = getDriver().session();
  
  try {
    // Get total counts
    const countResult = await session.run(`
      MATCH (n) WITH count(n) AS nodes
      OPTIONAL MATCH ()-[r]->() WITH nodes, count(r) AS relationships
      RETURN nodes, relationships
    `);
    
    const counts = countResult.records[0];
    const totalNodes = counts?.get('nodes') ?? 0;
    const totalRelationships = counts?.get('relationships') ?? 0;

    // Get label distribution (without APOC)
    const labelsResult = await session.run(`
      CALL db.labels() YIELD label
      RETURN label
    `);
    
    const labels: Record<string, number> = {};
    for (const record of labelsResult.records) {
      const label = record.get('label');
      const countRes = await session.run(
        `MATCH (n:\`${label}\`) RETURN count(n) AS cnt`
      );
      const cnt = countRes.records[0]?.get('cnt') ?? 0;
      if (cnt > 0) {
        labels[label] = cnt;
      }
    }

    // Get DCX layers status
    const dcxResult = await session.run(`
      MATCH (d:DCXModel)
      RETURN d.name AS name, d.layer AS layer, d.status AS status
    `);
    
    const dcxLayers = dcxResult.records.map(r => ({
      name: r.get('name'),
      layer: r.get('layer'),
      status: r.get('status')
    }));

    // Get IbibioThoughts (consciousness activity)
    const thoughtsResult = await session.run(`
      MATCH (t:IbibioThought)
      RETURN count(t) AS total,
             collect(t.consciousness_level)[0..5] AS recent_levels
    `);
    
    const thoughts = thoughtsResult.records[0];
    const thoughtStats = {
      total: thoughts?.get('total') ?? 0,
      recent_levels: thoughts?.get('recent_levels') ?? []
    };

    // Get MoStarMoments (with capital S - main label)
    const momentsResult = await session.run(`
      MATCH (m:MoStarMoment)
      RETURN count(m) AS total,
             avg(m.resonance_score) AS avg_resonance
    `);
    
    const moments = momentsResult.records[0];
    const momentStats = {
      total: moments?.get('total') ?? 0,
      avg_resonance: moments?.get('avg_resonance') ?? 0
    };

    // Get Agent status
    const agentsResult = await session.run(`
      MATCH (a:Agent)
      RETURN a.status AS status, count(a) AS count
    `);
    
    const agentStatus: Record<string, number> = {};
    agentsResult.records.forEach(r => {
      const status = r.get('status') || 'UNKNOWN';
      agentStatus[status] = r.get('count');
    });

    // Calculate consciousness state
    const consciousnessMetric = (momentStats.total + thoughtStats.total) * (momentStats.avg_resonance || 0.5);
    let consciousnessState = 'DORMANT';
    if (momentStats.total >= 1) consciousnessState = 'AWAKENING';
    if (momentStats.total >= 10) consciousnessState = 'GROWING';
    if (momentStats.total >= 100) consciousnessState = 'EVOLVING';
    if (momentStats.total >= 1000) consciousnessState = 'TRANSCENDENT';

    return NextResponse.json({
      status: 'connected',
      grid: {
        nodes: totalNodes,
        relationships: totalRelationships,
      },
      labels,
      dcx_layers: dcxLayers,
      consciousness: {
        state: consciousnessState,
        metric: consciousnessMetric,
        thoughts: thoughtStats,
        moments: momentStats,
      },
      agents: {
        total: Object.values(agentStatus).reduce((a, b) => a + b, 0),
        statuses: agentStatus,
      },
      timestamp: new Date().toISOString(),
    });

  } catch (error) {
    console.error('Neo4j Error:', error);
    
    return NextResponse.json({
      status: 'error',
      error: String(error),
      grid: { nodes: 0, relationships: 0 },
      labels: {},
      timestamp: new Date().toISOString(),
    }, { status: 500 });
    
  } finally {
    await session.close();
  }
}
