import { randomUUID } from "crypto";
import { NextResponse } from "next/server";
import http from "node:http";
import https from "node:https";
import { driver } from "../../../lib/neo4j";

let lastGoodTelemetry: Record<string, unknown> | null = null;
let lastGoodTelemetryTs = 0;
let lastGoodBackendStatus: Record<string, unknown> | null = null;

function neoToNumber(v: unknown): number {
  const maybe = v as { toNumber?: () => number } | null;
  if (maybe && typeof maybe.toNumber === "function") return maybe.toNumber();
  const n = Number(v as number);
  return Number.isNaN(n) ? 0 : n;
}

async function fetchBackendStatus(base: string) {
  return fetchJsonDirect(`${base}/api/v1/status`, 30000);
}

async function fetchBackendTelemetry(base: string) {
  return fetchJsonDirect(`${base}/api/v1/telemetry`, 30000);
}

async function fetchJsonDirect(url: string, timeoutMs: number): Promise<any | null> {
  return new Promise((resolve) => {
    try {
      const parsed = new URL(url);
      const lib = parsed.protocol === "https:" ? https : http;
      const req = lib.request(
        parsed,
        {
          method: "GET",
          headers: { Accept: "application/json" },
        },
        (res) => {
          let body = "";
          res.setEncoding("utf8");
          res.on("data", (chunk) => (body += chunk));
          res.on("end", () => {
            if (!res.statusCode || res.statusCode < 200 || res.statusCode >= 300) {
              resolve(null);
              return;
            }
            try {
              resolve(JSON.parse(body));
            } catch {
              resolve(null);
            }
          });
        }
      );

      req.setTimeout(timeoutMs, () => {
        req.destroy();
        resolve(null);
      });
      req.on("error", () => resolve(null));
      req.end();
    } catch {
      resolve(null);
    }
  });
}

export async function GET() {
  const ingestion_run_id = randomUUID();
  const timestamp = new Date().toISOString();
  const GRID_API = process.env.GRID_API_BASE || "http://127.0.0.1:8001";

  const [backendStatus, backendTelemetry] = await Promise.all([
    fetchBackendStatus(GRID_API),
    fetchBackendTelemetry(GRID_API),
  ]);
  if (backendStatus) {
    lastGoodBackendStatus = backendStatus as Record<string, unknown>;
  }

  // Preferred path: real backend telemetry + real backend status
  if (backendTelemetry) {
    const gridState = backendTelemetry?.gridState || {};
    const agentsList = backendTelemetry?.agents || [];
    const resolvedStatus = backendStatus || lastGoodBackendStatus || {};

    const payload = {
      backend: {
        ok: true,
        data: {
          ...(resolvedStatus as Record<string, unknown>),
          system: (resolvedStatus as any)?.system || "MoStar Grid API",
          neo4j: (resolvedStatus as any)?.neo4j || "unknown",
          ollama_model: (resolvedStatus as any)?.model || "Mostar/mostar-ai:latest",
        },
      },
      graph: {
        ok: true,
        stats: {
          totalMoments: gridState.totalMoments ?? 0,
          avgResonance: gridState.resonance ?? 0,
          distinctInitiators: gridState.distinctInitiators ?? 0,
          totalAgents: agentsList.length ?? 0,
          totalNodes: gridState.totalNodes ?? 0,
          totalRelationships: gridState.totalRelationships ?? 0,
          moments24h: gridState.moments24h ?? 0,
          totalArtifacts: gridState.totalArtifacts ?? 0,
          graphDensity: gridState.graphDensity ?? 0,
        },
        latest: backendTelemetry?.moments?.recent || [],
        agents: agentsList,
        layer_nodes: backendTelemetry?.layer_nodes || {},
        relationship_types: backendTelemetry?.relationship_types || {},
      },
      log: {
        entries: backendTelemetry?.moments?.recent || [],
        path: "neo4j://database/canonical",
      },
      generatedAt: timestamp,
    };

    lastGoodTelemetry = payload;
    lastGoodTelemetryTs = Date.now();
    return NextResponse.json(payload);
  }

  // Direct Neo4j fallback: still real data, no simulated constants
  const timeout = new Promise<never>((_, reject) =>
    setTimeout(() => reject(new Error("Neo4j timeout")), 4000)
  );

  const session = driver.session();
  try {
    const momentsCountRes = await Promise.race([session.run("MATCH (m:MoStarMoment) RETURN count(m) AS c"), timeout]);
    const momentsRes = await session.run("MATCH (m:MoStarMoment) RETURN m ORDER BY m.timestamp DESC LIMIT 15");
    const agentsRes = await session.run("MATCH (a:Agent) RETURN a LIMIT 1000");
    const countsRes = await session.run(
      "MATCH (n) WITH count(n) AS nodes MATCH ()-[r]->() RETURN nodes, count(r) AS rels"
    );
    const activityCountRes = await session.run(
      "MATCH (m:MoStarMoment) WHERE datetime(m.timestamp) > datetime() - duration('P1D') RETURN count(m) AS c"
    );
    const layerRes = await session.run(
      "CALL db.labels() YIELD label MATCH (n) WHERE label IN labels(n) RETURN label, count(n) AS c ORDER BY c DESC LIMIT 20"
    );
    const relTypesRes = await session.run(
      "CALL db.relationshipTypes() YIELD relationshipType MATCH ()-[r]->() WHERE type(r)=relationshipType RETURN relationshipType, count(r) AS c ORDER BY c DESC LIMIT 20"
    );
    const artifactsRes = await session.run("MATCH (a:KnowledgeArtifact) RETURN count(a) AS c");

    const totalMoments = neoToNumber(momentsCountRes.records[0]?.get("c"));
    const totalNodes = neoToNumber(countsRes.records[0]?.get("nodes"));
    const totalRelationships = neoToNumber(countsRes.records[0]?.get("rels"));
    const moments24h = neoToNumber(activityCountRes.records[0]?.get("c"));
    const totalArtifacts = neoToNumber(artifactsRes.records[0]?.get("c"));
    const density = totalNodes > 1 ? totalRelationships / (totalNodes * (totalNodes - 1)) : 0;

    const latestMoments = momentsRes.records.map((r) => {
      const props = r.get("m").properties;
      return {
        ...props,
        resonance_score: neoToNumber(props.resonance_score),
        quantum_id: props.quantum_id || randomUUID(),
        timestamp: props.timestamp || timestamp,
      };
    });

    const layer_nodes: Record<string, number> = {};
    for (const rec of layerRes.records) {
      const label = String(rec.get("label"));
      const c = neoToNumber(rec.get("c"));
      if (c > 0) layer_nodes[label] = c;
    }

    const relationship_types: Record<string, number> = {};
    for (const rec of relTypesRes.records) {
      relationship_types[String(rec.get("relationshipType"))] = neoToNumber(rec.get("c"));
    }

    const agents = agentsRes.records.map((r) => {
      const p = r.get("a").properties;
      return {
        ...p,
        id: p.agent_id || p.id || r.get("a").elementId,
      };
    });

    const payload = {
      backend: {
        ok: Boolean(backendStatus),
        data: backendStatus || { system: "MoStar Grid API", neo4j: "online" },
      },
      graph: {
        ok: true,
        stats: {
          totalMoments,
          avgResonance:
            latestMoments.length > 0
              ? latestMoments.reduce((a: number, m: any) => a + (Number(m.resonance_score) || 0), 0) / latestMoments.length
              : 0,
          distinctInitiators: new Set(latestMoments.map((m: any) => m.initiator).filter(Boolean)).size,
          totalAgents: agents.length,
          totalNodes,
          totalRelationships,
          moments24h,
          totalArtifacts,
          graphDensity: density,
        },
        latest: latestMoments,
        agents,
        layer_nodes,
        relationship_types,
      },
      log: {
        entries: latestMoments,
        path: "neo4j://direct",
      },
      generatedAt: timestamp,
      provenance: {
        source: "neo4j_direct",
        ingestion_run_id,
      },
    };

    lastGoodTelemetry = payload;
    lastGoodTelemetryTs = Date.now();
    return NextResponse.json(payload);
  } catch {
    if (lastGoodTelemetry && Date.now() - lastGoodTelemetryTs < 5 * 60_000) {
      return NextResponse.json({
        ...lastGoodTelemetry,
        generatedAt: timestamp,
        provenance: {
          source: "cached_last_good",
          ingestion_run_id,
        },
      });
    }
    return NextResponse.json(
      {
        backend: { ok: false, data: { system: "MoStar Grid API", neo4j: "offline" } },
        graph: {
          ok: false,
          stats: { totalMoments: 0, avgResonance: 0, distinctInitiators: 0, totalAgents: 0, totalNodes: 0, totalRelationships: 0, moments24h: 0, totalArtifacts: 0, graphDensity: 0 },
          latest: [],
          agents: [],
          layer_nodes: {},
          relationship_types: {},
        },
        log: { entries: [], path: "neo4j://offline" },
        generatedAt: timestamp,
      },
      { status: 503 }
    );
  } finally {
    await session.close();
  }
}
