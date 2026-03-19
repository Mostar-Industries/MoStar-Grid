import { NextResponse } from "next/server";
import { GRID_API_BASE } from "@/lib/apiConfig";

const GRID_API_BASE_URL = GRID_API_BASE;

export async function GET() {
  try {
    const response = await fetch(`${GRID_API_BASE_URL}/api/v1/status`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      // lightweight revalidate window for incremental static regens (Next.js hint)
      next: { revalidate: 10 },
    });

    if (!response.ok) {
      throw new Error(`Status check failed: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Status check error:", error);
    return NextResponse.json(
      {
        status: "error",
        message: error instanceof Error ? error.message : "Unknown error",
        layers: {
          dcx0: { status: "offline", lastPing: null },
          dcx1: { status: "offline", lastPing: null },
          dcx2: { status: "offline", lastPing: null },
        },
      },
      { status: 200 }
    );
  }
}
