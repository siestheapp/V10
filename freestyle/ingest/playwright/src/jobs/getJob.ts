import { q } from '../db/pg';

export type IngestionJob = {
  id: number;
  brand: string;
  category_url: string;
  status: string;
};

export async function getJob(jobId: number): Promise<IngestionJob | null> {
  const rows = await q<IngestionJob>(`select id, brand, category_url, status from ingestion_job where id=$1`, [jobId]);
  return rows[0] || null;
}


