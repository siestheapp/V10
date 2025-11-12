import { Browser } from 'playwright';
import { q } from '../db/pg';
import { ReformationAdapter } from '../adapters/reformation';
import { newPage } from '../core/browser';

export async function seedCategoryTasks(browser: Browser, jobId: number, categoryUrl: string) {
  // Use brand-specific crawl with our UA/context
  const page = await newPage(browser);
  const urls = await ReformationAdapter.crawlCategory(page, categoryUrl);
  await page.close();
  console.log(`[seedCategoryTasks] Collected ${urls.length} PDP urls for job ${jobId}`);
  for (const url of urls) {
    await q(
      `insert into public.ingestion_task(job_id, pdp_url) values ($1,$2)
       on conflict (job_id, pdp_url) do nothing`,
      [jobId, url]
    );
  }
  await q(
    `update public.ingestion_job set status='running', totals = jsonb_set(coalesce(totals,'{}'::jsonb), '{tasks}', to_jsonb($2::int)) where id=$1`,
    [jobId, urls.length]
  );
}


