import { NextResponse } from "next/server";

const OLLAMA_URL = (process.env.OLLAMA_API_URL || "").replace(/\/$/, "");
const OLLAMA_API_KEY = process.env.OLLAMA_API_KEY || "";

interface OllamaTagModel {
  name: string;
  [key: string]: unknown;
}

async function fetchModelsFromOllama() {
  if (!OLLAMA_URL) return null;
  try {
    const res = await fetch(`${OLLAMA_URL}/api/tags`, {
      headers: OLLAMA_API_KEY ? { Authorization: `Bearer ${OLLAMA_API_KEY}` } : undefined,
      signal: AbortSignal.timeout(5000),
      cache: "no-store",
    });
    if (!res.ok) return null;
    const data = await res.json();
    const loaded = Array.isArray(data?.models)
      ? (data.models as OllamaTagModel[]).map((m) => m.name).filter(Boolean)
      : [];
    return { models: loaded, count: loaded.length, source: "ollama-live" };
  } catch {
    return null;
  }
}

function fallbackModels() {
  return {
    models: [
      "Mostar/mostar-ai:latest",
      "Mostar/mostar-ai:dcx0",
      "Mostar/mostar-ai:dcx1",
      "Mostar/mostar-ai:dcx2",
      "Mostar/remostar-light:dcx1",
      "Mostar/remostar-light:dcx2",
    ],
    count: 6,
    source: "manifest",
  };
}

export async function GET() {
  const live = await fetchModelsFromOllama();
  return NextResponse.json(live ?? fallbackModels());
}
