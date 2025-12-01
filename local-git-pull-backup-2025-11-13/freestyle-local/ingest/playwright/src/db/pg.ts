import 'dotenv/config';
import { Pool } from 'pg';

const useSsl = /supabase\.co/.test(process.env.DATABASE_URL || '');

export const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 5,
  ssl: useSsl ? { rejectUnauthorized: false } : undefined
});

export async function q<T = any>(text: string, params?: any[]): Promise<T[]> {
  const client = await pool.connect();
  try {
    const res = await client.query(text, params);
    return res.rows as T[];
  } finally {
    client.release();
  }
}


