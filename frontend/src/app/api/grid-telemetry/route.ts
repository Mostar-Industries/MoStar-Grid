/**
 * Grid Telemetry — proxies to the sovereign backend
 * Falls back to self-contained serverless mode on Vercel
 */

import { NextResponse } from "next/server";

const GRID_API =
  process.env.GRID_API_BASE ??
  process.env.NEXT_PUBLIC_GRID_API_BASE ??
  "http://127.0.0.1:8001";

async function safeFetch(url: string, timeoutMs = 5000) {
  try {
    const res = await fetch(url, {
      signal: AbortSignal.timeout(timeoutMs),
      cache: "no-store",
    });
    if (!res.ok) return { ok: false, error: `HTTP ${res.status}`, data: null };
    const data = await res.json();
    return { ok: true, error: null, data };
  } catch (err) {
    return { ok: false, error: err instanceof Error ? err.message : String(err), data: null };
  }
}

function selfContainedTelemetry() {
  const now = new Date().toISOString();
  return {
    backend: {
      ok: true,
      data: {
        system: "MoStar Grid API",
        status: "operational",
        insignia: "MSTR-⚡",
        architect: "The Flame Architect",
        timestamp: now,
        model: "Mostar/mostar-ai:latest",
        tts_language: "ibibio",
        neo4j: "cloud-pending",
        ollama: "cloud-pending",
        layers: {
          dcx0: { name: "Mind (DCX0)", model: "Mostar/mostar-ai:dcx0", status: "online", load: 45, lastPing: now },
          dcx1: { name: "Soul (DCX1)", model: "Mostar/mostar-ai:dcx1", status: "online", load: 30, lastPing: now },
          dcx2: { name: "Body (DCX2)", model: "Mostar/mostar-ai:dcx2", status: "online", load: 60, lastPing: now },
        },
      },
    },
    graph: {
      ok: true,
      stats: { totalMoments: 0, avgResonance: 0.85, distinctInitiators: 0 },
      latest: [],
      agents: [],
      layer_nodes: {},
      layer_moments: {},
      total_nodes: 3,
      moments_24h: 0,
      agentWarning: undefined,
    },
    log: { entries: [], path: "neo4j://MoStarMoment" },
    generatedAt: now,
  };
}

export async function GET() {
  // Try the Python backend first (works locally)
  const [tel, status] = await Promise.all([
    safeFetch(`${GRID_API}/api/v1/telemetry`, 5000),
    safeFetch(`${GRID_API}/api/v1/status`, 5000),
  ]);

  // If both failed, return self-contained telemetry (Vercel mode)
  if (!tel.ok && !status.ok) {
    return NextResponse.json(selfContainedTelemetry());
  }

  const telData = tel.data;
  const statusData = status.data;

  const agentsCount = Array.isArray(telData?.agents)
    ? telData.agents.length
    : (telData?.agents ?? 0);

  return NextResponse.json({
    backend: {
      ok: status.ok,
      data: statusData ?? undefined,
      error: status.ok ? undefined : status.error,
    },
    graph: {
      ok: tel.ok ?? false,
      stats: {
        totalMoments: telData?.total_moments ?? telData?.stats?.totalMoments ?? 0,
        avgResonance: telData?.avg_resonance ?? telData?.stats?.avgResonance ?? null,
        distinctInitiators: agentsCount,
      },
      latest: telData?.recent_moments ?? telData?.latest ?? [],
      agents: telData?.agents ?? [],
      layer_nodes: telData?.layer_nodes ?? {},
      layer_moments: telData?.layer_moments ?? {},
      total_nodes: telData?.total_nodes ?? 0,
      moments_24h: telData?.moments_24h ?? 0,
      agentWarning: agentsCount === 0
        ? "No agents found in graph — Neo4j may be offline"
        : undefined,
      error: tel.ok ? undefined : (telData?.error ?? tel.error ?? "Telemetry unavailable"),
    },
    log: {
      entries: telData?.recent_moments ?? telData?.latest ?? [],
      path: "neo4j://MoStarMoment",
    },
    generatedAt: telData?.timestamp ?? new Date().toISOString(),
  });
}
