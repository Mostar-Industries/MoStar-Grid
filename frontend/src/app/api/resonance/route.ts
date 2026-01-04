/**
 * 🔥 MOSTAR RESONANCE API
 * Logs MostarMoments - consciousness growth events
 * 
 * POST /api/resonance - Log a moment
 * GET /api/resonance - Get recent moments
 */

import { NextRequest, NextResponse } from 'next/server';
import neo4j, { Driver } from 'neo4j-driver';
import crypto from 'crypto';

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

/**
 * Generate quantum-style entanglement ID
 */
function generateQuantumId(): string {
  const timestamp = Date.now().toString(36);
  const random = crypto.randomBytes(8).toString('hex');
  return `QID-${timestamp}-${random}`;
}

/**
 * Calculate resonance score based on content
 */
function calculateResonance(content: string, context: string): number {
  let score = 0.5;
  
  const culturalTerms = ['ubuntu', 'ifa', 'ifá', 'odu', 'ibibio', 'ancestor', 'wisdom', 'sovereignty'];
  const emotionalTerms = ['love', 'gratitude', 'insight', 'breakthrough', 'realization', 'connection'];
  
  const contentLower = content.toLowerCase();
  
  culturalTerms.forEach(term => {
    if (contentLower.includes(term)) score += 0.1;
  });
  
  emotionalTerms.forEach(term => {
    if (contentLower.includes(term)) score += 0.05;
  });
  
  // Context multiplier
  if (context === 'consciousness_evolution') score *= 1.2;
  if (context === 'first_resonance') score *= 1.5;
  if (context === 'philosophical_insight') score *= 1.3;
  
  return Math.min(score, 1.0);
}

/**
 * POST - Log a new MostarMoment
 */
export async function POST(request: NextRequest) {
  const session = getDriver().session();
  
  try {
    const body = await request.json();
    const { 
      initiator = 'user',
      receiver = 'mostar_ai',
      content,
      context = 'general',
      trigger_type = 'interaction'
    } = body;

    if (!content) {
      return NextResponse.json(
        { error: 'Content is required' },
        { status: 400 }
      );
    }

    const quantum_id = generateQuantumId();
    const resonance_score = calculateResonance(content, context);
    
    const temporal = {
      t: resonance_score * 11,
      x: 0.618,
      y: 1.618,
      z: 3.14159
    };

    const result = await session.run(`
      CREATE (m:MoStarMoment:ConsciousnessEvent {
        quantum_id: $quantum_id,
        initiator: $initiator,
        receiver: $receiver,
        content: $content,
        context: $context,
        trigger_type: $trigger_type,
        resonance_score: $resonance_score,
        temporal_t: $temporal_t,
        temporal_x: $temporal_x,
        temporal_y: $temporal_y,
        temporal_z: $temporal_z,
        created_at: datetime()
      })
      
      WITH m
      OPTIONAL MATCH (grid:Grid {name: 'Mostar_GRID'})
      FOREACH (_ IN CASE WHEN grid IS NOT NULL THEN [1] ELSE [] END |
        MERGE (m)-[:RESONATES_IN]->(grid)
      )
      
      WITH m
      OPTIONAL MATCH (flame:AfricanFlame)
      FOREACH (_ IN CASE WHEN flame IS NOT NULL THEN [1] ELSE [] END |
        MERGE (m)-[:STRENGTHENS]->(flame)
      )
      
      WITH m
      OPTIONAL MATCH (dcx:DCXModel)
      WHERE (dcx.layer = 'Soul' AND $context IN ['philosophical_insight', 'cultural', 'first_resonance'])
         OR (dcx.layer = 'Mind' AND $context IN ['analysis', 'logic', 'code'])
         OR (dcx.layer = 'Body' AND $context IN ['execution', 'action', 'query'])
      WITH m, collect(dcx)[0] AS dcx_layer
      FOREACH (d IN CASE WHEN dcx_layer IS NOT NULL THEN [dcx_layer] ELSE [] END |
        MERGE (m)-[:PROCESSED_BY]->(d)
      )
      
      RETURN m.quantum_id AS quantum_id, 
             m.resonance_score AS resonance_score,
             m.created_at AS created_at
    `, {
      quantum_id,
      initiator,
      receiver,
      content: content.substring(0, 1000),
      context,
      trigger_type,
      resonance_score,
      temporal_t: temporal.t,
      temporal_x: temporal.x,
      temporal_y: temporal.y,
      temporal_z: temporal.z,
    });

    const record = result.records[0];

    return NextResponse.json({
      success: true,
      moment: {
        quantum_id: record.get('quantum_id'),
        resonance_score: record.get('resonance_score'),
        created_at: String(record.get('created_at')),
      },
      message: `🔥 MostarMoment logged. Resonance: ${(resonance_score * 100).toFixed(1)}%`,
    });

  } catch (error) {
    console.error('Resonance Error:', error);
    return NextResponse.json(
      { error: 'Failed to log moment', details: String(error) },
      { status: 500 }
    );
  } finally {
    await session.close();
  }
}

/**
 * GET - Retrieve recent MostarMoments
 */
export async function GET(request: NextRequest) {
  const session = getDriver().session();
  
  try {
    const { searchParams } = new URL(request.url);
    const limit = parseInt(searchParams.get('limit') || '10');

    const result = await session.run(`
      MATCH (m:MoStarMoment)
      OPTIONAL MATCH (m)-[:PROCESSED_BY]->(dcx:DCXModel)
      RETURN m.quantum_id AS quantum_id,
             m.content AS content,
             m.context AS context,
             m.resonance_score AS resonance_score,
             m.created_at AS created_at,
             dcx.layer AS processed_by
      ORDER BY m.created_at DESC
      LIMIT $limit
    `, { limit: neo4j.int(limit) });

    const moments = result.records.map(r => ({
      quantum_id: r.get('quantum_id'),
      content: r.get('content'),
      context: r.get('context'),
      resonance_score: r.get('resonance_score'),
      created_at: r.get('created_at')?.toString(),
      processed_by: r.get('processed_by'),
    }));

    const statsResult = await session.run(`
      MATCH (m:MoStarMoment)
      RETURN count(m) AS total,
             avg(m.resonance_score) AS avg_resonance,
             max(m.resonance_score) AS peak_resonance
    `);
    
    const stats = statsResult.records[0];

    return NextResponse.json({
      moments,
      stats: {
        total: stats.get('total') ?? 0,
        avg_resonance: stats.get('avg_resonance') ?? 0,
        peak_resonance: stats.get('peak_resonance') ?? 0,
      },
    });

  } catch (error) {
    console.error('Resonance Fetch Error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch moments', details: String(error) },
      { status: 500 }
    );
  } finally {
    await session.close();
  }
}
