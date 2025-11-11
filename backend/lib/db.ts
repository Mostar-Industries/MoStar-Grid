// lib/db.ts
import { Pool, QueryResult } from 'pg'; // Ensure 'pg' is installed: npm install pg @types/pg

const NEON_DB_URL = process.env.NEON_DB_URL;

if (!NEON_DB_URL) {
  throw new Error('NEON_DB_URL not set in environment variables.');
}

const pool = new Pool({
  connectionString: NEON_DB_URL,
  ssl: { rejectUnauthorized: false }
});

export async function executeQuery(query: string, params: any[] = []): Promise<QueryResult> {
  const client = await pool.connect();
  try {
    const result = await client.query(query, params);
    return result;
  } finally {
    client.release();
  }
}

export async function getActiveDbType(): Promise<string> {
  return 'neon';
}