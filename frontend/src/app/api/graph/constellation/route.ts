import { NextResponse } from "next/server";
import { driver } from "../../../../lib/neo4j";
import neo4j from "neo4j-driver";

const GRID_API_BASE = process.env.GRID_API_BASE;

export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const limit = Math.min(parseInt(searchParams.get("limit") || "1500"), 2000);

  // ── Primary: proxy to Railway backend ────────────────────────────
  if (GRID_API_BASE) {
    try {
      const upstream = await fetch(
        `${GRID_API_BASE}/api/v1/graph/constellation?limit=${limit}`,
        { cache: "no-store", signal: AbortSignal.timeout(6000) }
      );
      if (upstream.ok) {
        // Stream response directly to bypass Vercel 4.5MB payload limit
        return new NextResponse(upstream.body, {
          status: 200,
          headers: { "Content-Type": "application/json" },
        });
      }
    } catch {
      // fall through to Neo4j direct
    }
  }

  // ── Fallback: query Neo4j Aura directly via global singleton driver ─
  // driver is created once at module scope in src/lib/neo4j.ts;
  // serverless warm-starts reuse the connection pool — no pool exhaustion.
  const neoLimit = neo4j.int(limit);
  const session = driver.session();
  try {
    const nodesRes = await session.run(
      `MATCH (n)
       RETURN elementId(n) AS id,
              coalesce(n.name, n.title, n.id, elementId(n)) AS name,
              labels(n) AS labels,
              coalesce(n.resonance_score, 0.5) AS resonance
       LIMIT $limit`,
      { limit: neoLimit }
    );

    const linksRes = await session.run(
      `MATCH (a)-[r]->(b)
       RETURN elementId(a) AS source,
              elementId(b) AS target,
              type(r)      AS rel
       LIMIT $limit`,
      { limit: neoLimit }
    );

    const nodes = nodesRes.records.map((rec) => ({
      id:        rec.get("id"),
      name:      String(rec.get("name") ?? ""),
      labels:    rec.get("labels") as string[],
      resonance: Number(rec.get("resonance") ?? 0.5),
    }));

    const links = linksRes.records.map((rec) => ({
      source: rec.get("source"),
      target: rec.get("target"),
      rel:    String(rec.get("rel")),
    }));

    return NextResponse.json({ nodes, links });
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    return NextResponse.json(
      { nodes: [], links: [], error: msg },
      { status: 503 }
    );
  } finally {
    await session.close();
  }
}
