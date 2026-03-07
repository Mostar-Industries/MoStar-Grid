import { NextResponse } from "next/server";

export async function GET() {
  // Stateless fallback: return empty feed with generatedAt timestamp
  const now = new Date().toISOString();
  return NextResponse.json({
    moments: [],
    count: 0,
    insignia: "MSTR-⚡",
    generatedAt: now,
  });
}
