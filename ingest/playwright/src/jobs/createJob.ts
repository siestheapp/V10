import { q } from '../db/pg';

export async function createJob(brand: string, categoryUrl: string): Promise<number> {
  const rows = await q<{ id: number }>(
    `insert into ingestion_job(brand, category_url, status)
     values ($1,$2,'queued')
     returning id`,
    [brand, categoryUrl]
  );
  return rows[0].id;
}


