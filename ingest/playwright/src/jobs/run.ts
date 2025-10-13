import 'dotenv/config';
import PQueue from 'p-queue';
import { withBrowser, newPage } from '../core/browser';
import { ReformationAdapter } from '../adapters/reformation';
import { q } from '../db/pg';
import { upsertBrand, ensureCategory, upsertStyle, upsertVariant, upsertProductUrl, insertPrice, insertImageRow } from '../db/upsert';
import { uploadImageToStorage } from '../images/storage';

type Adapter = typeof ReformationAdapter;

async function createJob(brand: string, categoryUrl: string) {
  const rows = await q<{ id: number }>(
    `insert into ingestion_job(brand, category_url, status, started_at)
     values ($1,$2,'running', now()) returning id`,
    [brand, categoryUrl]
  );
  return rows[0].id;
}

async function addTasks(jobId: number, pdpUrls: string[]) {
  for (const url of Array.from(new Set(pdpUrls))) {
    await q(
      `insert into ingestion_task(job_id, pdp_url) values ($1,$2)
       on conflict do nothing`,
      [jobId, url]
    ).catch(() => {});
  }
}

async function runJob(adapter: Adapter, categoryUrl: string) {
  const jobId = await createJob(adapter.brandName, categoryUrl);
  const totals = { pdps: 0, styles: 0, variants: 0, images: 0 };

  await withBrowser(async browser => {
    const page = await newPage(browser);
    const pdpUrls = await adapter.crawlCategory(page, categoryUrl);
    await addTasks(jobId, pdpUrls);

    const brandId = await upsertBrand(adapter.brandName);
    const categoryId = await ensureCategory(adapter.categoryName);

    const queue = new PQueue({ concurrency: parseInt(process.env.MAX_CONCURRENCY || '3', 10) });
    const tasks = await q<{ id: number; pdp_url: string }>(
      `select id, pdp_url from ingestion_task where job_id=$1 and status='queued'`,
      [jobId]
    );

    for (const task of tasks) {
      queue.add(async () => {
        await q(`update ingestion_task set status='running', started_at=now() where id=$1`, [task.id]);
        try {
          const p = await newPage(browser);
          const data = await adapter.extractPdp(p, task.pdp_url);

          if (!data.name || data.name.length < 2) throw new Error('No product name');

          const styleId = await upsertStyle({
            brand_id: brandId,
            category_id: categoryId,
            name: data.name,
            gender: 'womens',
            description: data.description || null
          });
          const variantId = await upsertVariant({ style_id: styleId, size_scale: data.size_scale });

          await upsertProductUrl(variantId, data.product_url);
          if (data.list_price) await insertPrice(variantId, data.list_price, 'USD');

          totals.styles += 1;
          totals.variants += 1;

          let pos = 0;
          for (const imgUrl of data.images.slice(0, 12)) {
            pos++;
            const { storagePath, width, height } = await uploadImageToStorage(styleId, variantId, imgUrl, pos);
            await insertImageRow(
              variantId,
              styleId,
              imgUrl,
              pos,
              storagePath ?? undefined,
              pos === 1,
              width ?? undefined,
              height ?? undefined
            );
            totals.images += 1;
          }

          await q(`update ingestion_task set status='done', finished_at=now() where id=$1`, [task.id]);
          await p.close();
          totals.pdps += 1;
        } catch (err: any) {
          await q(
            `update ingestion_task set status='error', last_error=$2, retries=retries+1, finished_at=now() where id=$1`,
            [task.id, (err?.message || '').slice(0, 1000)]
          );
        }
      });
    }

    await queue.onIdle();
  });

  await q(`update ingestion_job set status='done', totals=$2, finished_at=now() where id=$1`, [jobId, totals]);
  console.log('JOB DONE', { jobId, totals });
}

(async () => {
  const categoryUrl = process.argv[2];
  if (!categoryUrl) throw new Error('Usage: ts-node src/jobs/run.ts <CATEGORY_URL>');
  await runJob(ReformationAdapter, categoryUrl);
})();


