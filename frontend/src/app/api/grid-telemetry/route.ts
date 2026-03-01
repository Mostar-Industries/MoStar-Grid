/**
 * Grid Telemetry — proxies to the sovereign backend /api/v1/telemetry endpoint
 * Maps the response to the TelemetryPayload shape expected by useGridTelemetry
 */

import { NextResponse } from "next/server";

const GRID_API =
  process.env.GRID_API_BASE ??
  process.env.NEXT_PUBLIC_GRID_API_BASE ??
  "http://localhost:7001";

export async function GET() {
  // Try the full telemetry endpoint
  try {
    const [telRes, statusRes] = await Promise.all([
      fetch(`${GRID_API}/api/v1/telemetry`, { signal: AbortSignal.timeout(8000), cache: "no-store" }),
      fetch(`${GRID_API}/api/v1/status`, { signal: AbortSignal.timeout(4000), cache: "no-store" }),
    ]);

    const telData = telRes.ok ? await telRes.json() : null;
    const statusData = statusRes.ok ? await statusRes.json() : null;

    // Map to TelemetryPayload shape expected by useGridTelemetry
    return NextResponse.json({
      backend: {
        ok: statusRes.ok,
        data: statusData ?? undefined,
        error: statusRes.ok ? undefined : `status returned ${statusRes.status}`,
      },
      graph: {
        ok: telData?.ok ?? false,
        stats: telData?.stats ?? { totalMoments: 0, avgResonance: null, distinctInitiators: 0 },
        latest: telData?.latest ?? [],
        agents: telData?.agents ?? [],
        agentWarning: telData?.agents?.length === 0 ? "No agents found in graph — Neo4j may be offline" : undefined,
        error: telData?.ok ? undefined : (telData?.error ?? "Telemetry unavailable"),
      },
      log: {
        entries: telData?.latest ?? [],
        path: "neo4j://MoStarMoment",
      },
      generatedAt: telData?.timestamp ?? new Date().toISOString(),
    });
  } catch (err) {
    // Total failure — backend unreachable
    return NextResponse.json({
      backend: { ok: false, error: err instanceof Error ? err.message : String(err) },
      graph: { ok: false, stats: null, latest: [], agents: [] },
      log: { entries: [], path: "error" },
      generatedAt: new Date().toISOString(),
    });
  }
}
