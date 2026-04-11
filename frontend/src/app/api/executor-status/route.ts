/**
 * Executor Status API
 * -------------------
 * Returns the live state of the Mo Executor from Neo4j.
 *
 * Data comes from two real sources:
 *   1. ExecutorHeartbeat node — written by mo_executor.py on every cycle
 *   2. ExecutionEvent nodes   — written by mo_executor.py per processed moment
 *
 * If the heartbeat is older than 60s, Mo is considered STALLED.
 * If no heartbeat node exists, Mo has NEVER run.
 */

import { NextResponse } from "next/server";
import { randomUUID } from "crypto";
import http from "node:http";
import https from "node:https";
import { driver } from "../../../lib/neo4j";

interface Heartbeat {
    executor_id: string;
    last_heartbeat: string;
    cycle_count: number;
    total_processed: number;
    status: string;
}

interface ExecutionEvent {
    id: string;
    processed_at: string;
    action: string;
    reasoning_summary: string;
}

interface ExecutorStatus {
    status: "ALIVE" | "STALLED" | "NEVER_RUN";
    is_alive: boolean;
    stalled_ms: number;
    heartbeat: Heartbeat | null;
    recent_events: ExecutionEvent[];
    pending_moments: number;
}

function neoToNumber(v: unknown): number {
    const maybe = v as { toNumber?: () => number } | null;
    if (maybe && typeof maybe.toNumber === "function") return maybe.toNumber();
    const n = Number(v);
    return Number.isNaN(n) ? 0 : n;
}

function neoToString(v: unknown): string {
    if (v == null) return "";
    if (typeof v === "object" && "toString" in (v as object)) {
        return (v as { toString(): string }).toString();
    }
    return String(v);
}

type BackendTelemetry = {
    gridState?: {
        lastCycle?: string;
    };
    agents?: Array<{
        id?: string;
        name?: string;
        status?: string;
    }>;
};

async function fetchBackendTelemetry(): Promise<BackendTelemetry | null> {
    const GRID_API = process.env.GRID_API_BASE || "http://127.0.0.1:8001";
    return (await fetchJsonDirect(
        `${GRID_API}/api/v1/telemetry`,
        30000
    )) as BackendTelemetry | null;
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

function buildFallbackExecutor(
    telemetry: BackendTelemetry | null,
    now: Date
): ExecutorStatus | null {
    if (!telemetry) return null;

    const executorAgent = (telemetry.agents || []).find((agent) => {
        const id = String(agent.id || "").toLowerCase();
        const name = String(agent.name || "").toLowerCase();
        return id === "agent-mo-executor" || name.includes("executor");
    });

    if (!executorAgent) {
        return {
            status: "NEVER_RUN",
            is_alive: false,
            stalled_ms: 0,
            heartbeat: null,
            recent_events: [],
            pending_moments: 0,
        };
    }

    const beatIso =
        telemetry.gridState?.lastCycle && !Number.isNaN(new Date(telemetry.gridState.lastCycle).getTime())
            ? telemetry.gridState.lastCycle
            : now.toISOString();

    const statusText = String(executorAgent.status || "").toLowerCase();
    const markedOnline = statusText === "online" || statusText === "alive";
    const stalledMs = markedOnline
        ? 0
        : Math.max(0, now.getTime() - new Date(beatIso).getTime());
    const isAlive = markedOnline;

    return {
        status: isAlive ? "ALIVE" : "STALLED",
        is_alive: isAlive,
        stalled_ms: stalledMs,
        heartbeat: {
            executor_id: String(executorAgent.id || "agent-mo-executor"),
            last_heartbeat: isAlive ? now.toISOString() : beatIso,
            cycle_count: 0,
            total_processed: 0,
            status: markedOnline ? "online" : "stalled",
        },
        recent_events: [],
        pending_moments: 0,
    };
}

export async function GET() {
    const ingestion_run_id = randomUUID();
    const now = new Date();
    const timestamp = now.toISOString();

    const fallbackTelemetry = await fetchBackendTelemetry();

    const session = driver.session();
    try {
        const heartbeatResult = await session.run(`
            MATCH (hb:ExecutorHeartbeat)
            RETURN
              hb.executor_id      AS executor_id,
              hb.last_heartbeat   AS last_heartbeat,
              hb.cycle_count      AS cycle_count,
              hb.total_processed  AS total_processed,
              hb.status           AS status
            LIMIT 1
          `);

        const eventsResult = await session.run(`
            MATCH (e:ExecutionEvent)
            RETURN
              e.id              AS id,
              e.executor_id     AS executor_id,
              e.processed_at    AS processed_at,
              e.action          AS action,
              e.reasoning_summary AS reasoning_summary
            ORDER BY e.processed_at DESC
            LIMIT 10
          `);

        const pendingResult = await session.run(`
            MATCH (m:MoStarMoment)
            WHERE m.mo_processed IS NULL
            RETURN count(m) AS pending_count
          `);

        // Parse heartbeat
        const hbRecord = heartbeatResult.records[0] ?? null;
        let executorAlive = false;
        let stalledMs = 0;

        const heartbeat = hbRecord
            ? {
                executor_id: neoToString(hbRecord.get("executor_id")),
                last_heartbeat: neoToString(hbRecord.get("last_heartbeat")),
                cycle_count: neoToNumber(hbRecord.get("cycle_count")),
                total_processed: neoToNumber(hbRecord.get("total_processed")),
                status: neoToString(hbRecord.get("status")),
            }
            : null;

        if (heartbeat?.last_heartbeat) {
            const lastBeat = new Date(heartbeat.last_heartbeat);
            stalledMs = now.getTime() - lastBeat.getTime();
            executorAlive = stalledMs < 60_000; // alive if beat within last 60s
        }

        // Parse execution events
        const events = eventsResult.records.map((r) => ({
            id: neoToString(r.get("id")),
            executor_id: neoToString(r.get("executor_id")),
            processed_at: neoToString(r.get("processed_at")),
            action: neoToString(r.get("action")),
            reasoning_summary: neoToString(r.get("reasoning_summary")),
        }));

        const pendingCount = neoToNumber(
            pendingResult.records[0]?.get("pending_count") ?? 0
        );

        // Determine status label
        let executorStatus: string;
        if (!heartbeat) {
            executorStatus = "NEVER_RUN";
        } else if (executorAlive) {
            executorStatus = "ALIVE";
        } else {
            executorStatus = "STALLED";
        }

        return NextResponse.json({
            executor: {
                status: executorStatus,
                is_alive: executorAlive,
                stalled_ms: stalledMs,
                heartbeat,
                recent_events: events,
                pending_moments: pendingCount,
            },
            provenance: {
                source: "neo4j",
                timestamp,
                ingestion_run_id,
            },
        });
    } catch (error) {
        const fallback = buildFallbackExecutor(fallbackTelemetry, now);
        if (fallback) {
            return NextResponse.json({
                executor: fallback,
                provenance: {
                    source: "backend_telemetry_fallback",
                    timestamp,
                    ingestion_run_id,
                    warning:
                        error instanceof Error
                            ? error.message
                            : "Neo4j query failed; using backend telemetry fallback.",
                },
            });
        }
        return NextResponse.json(
            {
                executor: null,
                provenance: {
                    source: "error",
                    timestamp,
                    ingestion_run_id,
                    error: error instanceof Error ? error.message : "Unknown error",
                },
            },
            { status: 503 }
        );
    } finally {
        await session.close();
    }
}
