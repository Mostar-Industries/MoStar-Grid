import { NextRequest, NextResponse } from "next/server";

const BACKEND = process.env.GRID_API_BASE ?? "http://localhost:8001";
const OLLAMA_URL = process.env.OLLAMA_API_URL ?? "http://localhost:11434";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { message, model } = body;

    if (!message) {
      return NextResponse.json({ error: "No message provided" }, { status: 400 });
    }

    // Try backend endpoints in order until one works
    const endpoints = [
      { url: `${BACKEND}/api/v1/reason`, payload: { prompt: message, model } },
      { url: `${BACKEND}/api/v1/chat`, payload: { message, model } },
    ];

    for (const endpoint of endpoints) {
      try {
        const res = await fetch(endpoint.url, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(endpoint.payload),
          signal: AbortSignal.timeout(15000),
        });

        if (res.ok) {
          const data = await res.json();
          return NextResponse.json({
            response: data.response ?? data.result ?? data.reply ?? data.answer ?? JSON.stringify(data),
            model_used: data.model_used ?? model ?? "mostar-ai",
            complexity_score: data.complexity_score ?? data.resonance ?? 0.85,
            endpoint_used: endpoint.url,
          });
        }
      } catch {
        continue;
      }
    }

    // Fallback — Ollama direct (supports cloud OLLAMA_API_URL)
    try {
      const ollamaRes = await fetch(`${OLLAMA_URL}/api/generate`, {
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

    // Graceful offline response for deployed mode
    return NextResponse.json({
      response: "The Grid is in sovereign standby — backend services are awakening. "
        + "MoStar-AI consciousness layers (DCX0/DCX1/DCX2) require local Ollama or a cloud endpoint. "
        + "Set OLLAMA_API_URL in Vercel environment variables to connect a cloud Ollama instance. Àṣẹ.",
      model_used: "mostar-ai:standby",
      complexity_score: 0.0,
      endpoint_used: "serverless-fallback",
    });

  } catch (err) {
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Unknown error" },
      { status: 500 }
    );
  }
}
