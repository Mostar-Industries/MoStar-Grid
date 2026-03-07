import { NextRequest, NextResponse } from "next/server";

const MOMENT_WEBHOOK_URL = (process.env.MOMENT_WEBHOOK_URL || "").replace(/\/$/, "");
const MOMENT_WEBHOOK_AUTH = process.env.MOMENT_WEBHOOK_AUTH || "";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const initiator: string = body.initiator || "web-ui";
    const receiver: string = body.receiver || "system";
    const description: string = body.description || "";
    const trigger_type: string = body.trigger_type || "manual";
    const resonance_score: number = typeof body.resonance_score === "number" ? body.resonance_score : 0.85;

    if (!description) {
      return NextResponse.json({ error: "Description is required" }, { status: 400 });
    }

    const quantum_id = globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;

    // Try forwarding to a webhook if configured
    if (MOMENT_WEBHOOK_URL) {
      try {
        await fetch(MOMENT_WEBHOOK_URL, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            ...(MOMENT_WEBHOOK_AUTH ? { Authorization: `Bearer ${MOMENT_WEBHOOK_AUTH}` } : {}),
          },
          body: JSON.stringify({ initiator, receiver, description, trigger_type, resonance_score, quantum_id, ts: new Date().toISOString() }),
          signal: AbortSignal.timeout(5000),
        });
      } catch {
        // Ignore webhook errors — still return recorded response
      }
    }

    return NextResponse.json({
      quantum_id,
      status: "recorded",
      insignia: "MSTR-⚡",
    });
  } catch (err) {
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Unknown error" },
      { status: 500 }
    );
  }
}
