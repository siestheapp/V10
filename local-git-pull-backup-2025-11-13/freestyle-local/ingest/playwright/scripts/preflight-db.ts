import 'dotenv/config';
import { Client } from 'pg';

(async () => {
  const url = process.env.DATABASE_URL!;
  if (!url) {
    throw new Error('DATABASE_URL is empty');
  }
  const client = new Client({ connectionString: url, ssl: /supabase\.co/.test(url) ? { rejectUnauthorized: false } : undefined });
  await client.connect();
  const res = await client.query(
    "select current_database() as db, current_user as usr, coalesce((select count(*) from information_schema.tables where table_schema='public' and table_name in ('product_master','product_variants','style','variant')),0)::int as has_catalog"
  );
  await client.end();
  const masked = url.replace(/:[^:@/]+@/, '://****@');
  console.log('Preflight:', { url: masked, ...res.rows[0] });
  if (!res.rows[0].has_catalog) {
    throw new Error('Preflight failed: catalog tables not found. You are pointed at the wrong DB.');
  }
})();


