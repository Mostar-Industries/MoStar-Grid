import { NextResponse } from "next/server";

const GRID_API_BASE =
  process.env.GRID_API_BASE ??
  process.env.NEXT_PUBLIC_GRID_API_BASE ??
  "http://localhost:8001";

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const message: string = body?.message;
    if (!message) {
      return NextResponse.json({ error: "Missing chat message." }, { status: 400 });
    }

    const response = await fetch(`${GRID_API_BASE}/api/v1/reason`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ prompt: message }),
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(`Grid API responded with ${response.status}: ${text}`);
    }

    const payload = await response.json();
    return NextResponse.json(payload);
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Chat relay failed" },
      { status: 500 }
    );
  }
}
