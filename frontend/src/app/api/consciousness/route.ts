import { NextResponse } from "next/server";

const CONSCIOUSNESS_API_BASE =
  process.env.CONSCIOUSNESS_API_BASE ?? "http://localhost:8001";

type PreferredLayer = "auto" | "dcx0" | "dcx1" | "dcx2";

interface ConsciousnessRequest {
  query: string;
  agent_id: string;
  context?: string;
  preferred_layer?: PreferredLayer;
  session_id?: string;
}

export async function POST(request: Request) {
  try {
    const {
      query,
      agent_id = "web-ui",
      context,
      preferred_layer = "auto",
      session_id,
    }: Partial<ConsciousnessRequest> = await request.json();

    if (!query) {
      return NextResponse.json({ error: "Query is required" }, { status: 400 });
    }

    const response = await fetch(
      `${CONSCIOUSNESS_API_BASE}/api/v1/reason`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Agent-ID": agent_id,
          ...(session_id ? { "X-Session-ID": session_id } : {}),
        },
        body: JSON.stringify({
          prompt: query,
          context,
          preferred_layer,
          timestamp: new Date().toISOString(),
        }),
      }
    );

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Consciousness API error: ${response.status} - ${error}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Consciousness route error:", error);
    return NextResponse.json(
      {
        error: "Failed to process consciousness request",
        details: error instanceof Error ? error.message : String(error),
      },
      { status: 500 }
    );
  }
}

export const dynamic = "force-dynamic";
