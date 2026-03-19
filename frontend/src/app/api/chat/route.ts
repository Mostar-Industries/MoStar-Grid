import { NextRequest, NextResponse } from "next/server";
import { GRID_API_BASE, OLLAMA_HOST } from "@/lib/apiConfig";
import { extractApiResponse } from "@/lib/apiUtils";

const BACKEND = GRID_API_BASE;

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { message, model } = body;

    if (!message) {
      return NextResponse.json({ error: "No message provided" }, { status: 400 });
    }

    // Try endpoints in order until one works
    const endpoints = [
      { url: `${BACKEND}/api/v1/reason`, payload: { prompt: message, model } },
      { url: `${BACKEND}/api/v1/chat`, payload: { message, model } },
      { url: `${BACKEND}/chat`, payload: { message, model } },
      { url: `${BACKEND}/reason`, payload: { query: message, model } },
      { url: `${BACKEND}/remostar/query`, payload: { query: message, language: "en" } },
    ];

    let lastError = "";

    for (const endpoint of endpoints) {
      try {
        const res = await fetch(endpoint.url, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(endpoint.payload),
          signal: AbortSignal.timeout(30000),
        });

        if (res.ok) {
          const data = await res.json();
          return NextResponse.json({
            response: extractApiResponse(data, JSON.stringify(data)),
            model_used: data.model_used ?? model ?? "mostar-ai",
            complexity_score: data.complexity_score ?? data.resonance ?? 0.85,
            endpoint_used: endpoint.url,
          });
        }
        lastError = `${endpoint.url} → ${res.status}`;
      } catch (e) {
        lastError = `${endpoint.url} → ${e instanceof Error ? e.message : "unreachable"}`;
        continue;
      }
    }

    // Fallback — Ollama direct
    try {
      const ollamaRes = await fetch(`${OLLAMA_HOST}/api/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: model ?? "Mostar/mostar-ai:latest",
          prompt: message,
          stream: false,
        }),
        signal: AbortSignal.timeout(60000),
      });

      if (ollamaRes.ok) {
        const data = await ollamaRes.json();
        return NextResponse.json({
          response: data.response,
          model_used: data.model ?? "mostar-ai-direct",
          complexity_score: 0.85,
          endpoint_used: "ollama-direct",
        });
      }
    } catch {
      // Ollama also unreachable
    }

    return NextResponse.json(
      {
        error: "All endpoints unreachable",
        tried: lastError,
        suggestion: "Ensure backend is running on port 7001 and Ollama on 11434",
      },
      { status: 503 }
    );

  } catch (err) {
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Unknown error" },
      { status: 500 }
    );
  }
}
