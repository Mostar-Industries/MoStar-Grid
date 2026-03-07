import { NextResponse } from "next/server";

const GRID_API_BASE = process.env.GRID_API_BASE ?? "http://localhost:8001";
const OLLAMA_URL = process.env.OLLAMA_API_URL ?? "http://localhost:11434";

async function checkOllama(): Promise<string> {
  try {
    const r = await fetch(`${OLLAMA_URL}/api/tags`, {
      signal: AbortSignal.timeout(3000),
    });
    return r.ok ? "online" : "offline";
  } catch {
    return "offline";
  }
}

function buildStatus(ollama: string) {
  const now = new Date().toISOString();
  const overall = ollama === "online" ? "operational" : "degraded";
  return {
    system: "MoStar Grid API",
    status: overall,
    insignia: "MSTR-⚡",
    architect: "The Flame Architect",
    timestamp: now,
    model: "Mostar/mostar-ai:latest",
    tts_language: "ibibio",
    neo4j: "cloud-pending",
    ollama,
    layers: {
      dcx0: {
        name: "Mind (DCX0)",
        model: "Mostar/mostar-ai:dcx0",
        status: ollama,
        load: ollama === "online" ? 45 : 0,
        lastPing: ollama === "online" ? now : null,
      },
      dcx1: {
        name: "Soul (DCX1)",
        model: "Mostar/mostar-ai:dcx1",
        status: "cloud-pending",
        load: 0,
        lastPing: null,
      },
      dcx2: {
        name: "Body (DCX2)",
        model: "Mostar/mostar-ai:dcx2",
        status: ollama === "online" ? "degraded" : "offline",
        load: ollama === "online" ? 20 : 0,
        lastPing: ollama === "online" ? now : null,
      },
    },
  };
}

export async function GET() {
  // Try the Python backend first (works locally)
  try {
    const response = await fetch(`${GRID_API_BASE}/api/v1/status`, {
      signal: AbortSignal.timeout(4000),
      cache: "no-store",
    });
    if (response.ok) {
      const data = await response.json();
      return NextResponse.json(data);
    }
  } catch {
    // Backend unreachable — fall through to self-contained mode
  }

  // Self-contained mode (Vercel serverless)
  const ollama = await checkOllama();
  return NextResponse.json(buildStatus(ollama));
}
