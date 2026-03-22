import neo4j from "neo4j-driver";

let driver;

function getDriver() {
  if (driver) {
    return driver;
  }

  const uri = process.env.NEO4J_URI;
  const user = process.env.NEO4J_USER;
  const password = process.env.NEO4J_PASSWORD;

  if (!uri || !user || !password) {
    return null;
  }

  driver = neo4j.driver(uri, neo4j.auth.basic(user, password), {
    maxConnectionLifetime: 3 * 60 * 60 * 1000,
    maxConnectionPoolSize: 20,
    connectionAcquisitionTimeout: 20000,
  });

  return driver;
}

export default async function handler(req, res) {
  const ingestionRunId = globalThis.crypto?.randomUUID?.() ?? `${Date.now()}`;
  const timestamp = new Date().toISOString();

  if (req.method !== "GET") {
    return res.status(405).json({
      error: "Method not allowed",
      allowed: ["GET"],
    });
  }

  const neo4jDriver = getDriver();
  if (!neo4jDriver) {
    return res.status(503).json({
      moments: [],
      count: 0,
      provenance: {
        source: "error",
        timestamp,
        ingestion_run_id: ingestionRunId,
        error: "Neo4j not configured",
      },
    });
  }

  const session = neo4jDriver.session();
  try {
    const result = await session.run(
      `
      MATCH (m:MoStarMoment)
      OPTIONAL MATCH (m)-[:PRECEDES]->(next:MoStarMoment)
      OPTIONAL MATCH (m)<-[:MANIFESTS]-(agent:Agent)
      WITH m, collect(DISTINCT next) AS nextMoments, collect(DISTINCT agent) AS agents
      RETURN m, nextMoments, agents
      ORDER BY m.created_at DESC
      LIMIT 100
      `
    );

    const moments = result.records.map((record) => {
      const mNode = record.get("m");
      const nexts = record.get("nextMoments") || [];
      const agents = record.get("agents") || [];
      const id = mNode.properties.id || mNode.identity.toString();

      return {
        id,
        ...mNode.properties,
        nextMoments: nexts.map((n) => n.properties),
        agents: agents.map((a) => a.properties),
        provenance: {
          source: "neo4j",
          timestamp,
          upstream_id: mNode.identity.toString(),
          ingestion_run_id: ingestionRunId,
          confidence: 1.0,
        },
      };
    });

    return res.status(200).json({
      moments,
      count: moments.length,
      provenance: {
        source: "neo4j",
        timestamp,
        ingestion_run_id: ingestionRunId,
        upstream_id: `neo4j:${process.env.NEO4J_URI}`,
      },
    });
  } catch (error) {
    return res.status(503).json({
      moments: [],
      count: 0,
      provenance: {
        source: "error",
        timestamp,
        ingestion_run_id: ingestionRunId,
        error: error instanceof Error ? error.message : "Unknown database error",
        error_type: error instanceof Error ? error.name : "Unknown",
      },
    });
  } finally {
    await session.close();
  }
}
