import neo4j from 'neo4j-driver';

const uri = process.env.NEO4J_URI;
const user = process.env.NEO4J_USER;
const password = process.env.NEO4J_PASSWORD;

if (!uri || !user || !password) {
  console.warn('Neo4j credentials missing – moments API may return 503');
}

export const driver = neo4j.driver(
  uri || 'bolt://localhost:7687',
  neo4j.auth.basic(user || '', password || ''),
  {
    maxConnectionLifetime: 3 * 60 * 60 * 1000,
    maxConnectionPoolSize: 50,
    connectionAcquisitionTimeout: 20000,
  }
);
