/**
 * Grid Telemetry — proxies to the sovereign backend
 * Falls back to self-contained serverless mode on Vercel
 */

import { NextResponse } from "next/server";
import { randomUUID } from "crypto";
import { driver } from "../../../lib/neo4j";

function neoToNumber(v: unknown): number {
  // neo4j Integer has toNumber; fall back to Number()
  const maybe = v as { toNumber?: () => number } | null;
  if (maybe && typeof maybe.toNumber === "function") {
    return maybe.toNumber();
  }
  const n = Number(v as number);
  return Number.isNaN(n) ? 0 : n;
}

export async function GET() {
  const ingestion_run_id = randomUUID();
  const timestamp = new Date().toISOString();

  if (!process.env.NEO4J_URI || !process.env.NEO4J_USER || !process.env.NEO4J_PASSWORD) {
    return NextResponse.json(
      {
        telemetry: null,
        provenance: { source: "error", timestamp, ingestion_run_id, error: "Neo4j not configured" },
      },
      { status: 503 }
    );
  }

  const session = driver.session();
  try {
    const [nodeCountsResult, relCountResult, newNodesResult, avgConnectionsResult, recentMomentsResult, agentsResult] =
      await Promise.all([
        session.run(`MATCH (n) RETURN labels(n) AS labels, count(n) AS count ORDER BY count DESC`),
        session.run(`MATCH ()-[r]->() RETURN count(r) AS total`),
        session.run(`MATCH (n) WHERE exists(n.created_at) AND n.created_at > datetime() - duration('P1D') RETURN count(n) AS new_nodes`),
        session.run(`MATCH (m:MoStarMoment) OPTIONAL MATCH (m)-[r]-() RETURN m.id AS id, count(r) AS degree`),
        session.run(`MATCH (m:MoStarMoment) RETURN m ORDER BY m.created_at DESC LIMIT 10`),
        session.run(`MATCH (a:Agent) RETURN a LIMIT 100`),
      ]);

    const nodeCounts = nodeCountsResult.records.map((rec) => ({
      label: (rec.get("labels") as string[])[0],
      count: neoToNumber(rec.get("count")),
    }));

    const totalRelationships = neoToNumber(relCountResult.records[0].get("total"));
    const newNodesLast24h = neoToNumber(newNodesResult.records[0].get("new_nodes"));

    const degrees = avgConnectionsResult.records.map((r) => neoToNumber(r.get("degree")));
    const totalDegree = degrees.reduce((s, v) => s + (Number.isFinite(v) ? v : 0), 0);
    const avgResonance = degrees.length > 0 ? totalDegree / degrees.length : 0;

    const recent = recentMomentsResult.records.map((r) => {
      const m = r.get("m") as unknown as { properties: Record<string, unknown>; identity: { toString(): string } };
      return {
        id: (m.properties["id"] as string) ?? m.identity.toString(),
        ...m.properties,
        provenance: { source: "neo4j", timestamp, upstream_id: m.identity.toString(), ingestion_run_id, confidence: 1.0 },
      };
    });

    const agents = agentsResult.records.map((r) => {
      const a = r.get("a") as unknown as { properties: Record<string, unknown>; identity: { toString(): string } };
      return {
        id: (a.properties["id"] as string) ?? a.identity.toString(),
        ...a.properties,
        provenance: { source: "neo4j", timestamp, upstream_id: a.identity.toString(), ingestion_run_id, confidence: 1.0 },
      };
    });

    const telemetry = {
      nodeCounts,
      totalRelationships,
      newNodesLast24h,
      avgResonance: Number.isFinite(avgResonance) ? parseFloat(avgResonance.toFixed(2)) : 0,
      latest: recent,
      agents,
      timestamp,
    };

    return NextResponse.json({
      telemetry,
      provenance: { source: "neo4j", timestamp, ingestion_run_id },
    });
  } catch (error) {
    return NextResponse.json(
      {
        telemetry: null,
        provenance: {
          source: "error",
          timestamp,
          ingestion_run_id,
          error: error instanceof Error ? error.message : "Unknown database error",
        },
      },
      { status: 503 }
    );
  } finally {
    await session.close();
  }
}
