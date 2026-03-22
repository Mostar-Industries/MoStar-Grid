import { NextRequest, NextResponse } from "next/server";

// Cloud TTS provider hook
const TTS_PROVIDER_URL = (process.env.TTS_PROVIDER_URL || "").replace(/\/$/, "");
const TTS_API_KEY = process.env.TTS_API_KEY || "";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json().catch(() => ({}));
    const text: string | undefined = body.text || body.message;
    const language: string = body.language || "ibibio";
    const voice: string | undefined = body.voice;

    if (!text) {
      return NextResponse.json({ error: "No text provided" }, { status: 400 });
    }

    // If a cloud TTS endpoint is configured, proxy the request
    if (TTS_PROVIDER_URL) {
      try {
        const res = await fetch(TTS_PROVIDER_URL, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            ...(TTS_API_KEY ? { Authorization: `Bearer ${TTS_API_KEY}` } : {}),
          },
          body: JSON.stringify({ text, language, voice }),
          signal: AbortSignal.timeout(20000),
        });

        if (res.ok) {
          // Expect provider to return either an audio_url or base64 content
          const data = await res.json();
          return NextResponse.json({
            audio_url: data.audio_url ?? null,
            audio_base64: data.audio_base64 ?? null,
            language,
            insignia: "MSTR-⚡",
            provider: "cloud",
          });
        }
      } catch {
        // Fall through to graceful standby
      }
    }

    // Graceful standby response
    return NextResponse.json({
      message: "Voice synthesis is in sovereign standby. Configure TTS_PROVIDER_URL to enable cloud TTS.",
      language,
      insignia: "MSTR-⚡",
      provider: "standby",
    });
  } catch (err) {
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Unknown error" },
      { status: 500 }
    );
  }
}
