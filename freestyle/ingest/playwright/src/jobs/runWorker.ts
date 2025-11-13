import pLimit from 'p-limit';
import { Browser } from 'playwright';
import { q } from '../db/pg';
import { newPage } from '../core/browser';
import { parsePdp } from '../adapters/reformation';
import { upsertBrand, ensureCategory, upsertStyle, upsertVariant, upsertProductUrl, insertPrice, insertImageRow } from '../db/upsert';
import { uploadImageToStorage } from '../images/storage';

type Task = { id: number; pdp_url: string };

async function fetchRunnableTasks(jobId: number, batch = 50): Promise<Task[]> {
  const rows = await q<Task>(
    `select id, pdp_url from ingestion_task
     where job_id=$1 and (status='queued' or (status='error' and retries < 3))
     order by id asc
     limit $2`,
    [jobId, batch]
  );
  return rows;
}

async function setTaskStatus(id: number, status: string, err?: string) {
  if (status === 'running') {
    await q(`update ingestion_task set status='running', started_at=now() where id=$1`, [id]);
  } else if (status === 'done') {
    await q(`update ingestion_task set status='done', finished_at=now() where id=$1`, [id]);
  } else if (status === 'error') {
    await q(`update ingestion_task set status='error', retries=retries+1, last_error=$2 where id=$1`, [id, err || null]);
  }
}

export async function runWorker(browser: Browser, jobId: number) {
  const concurrency = Number(process.env.MAX_CONCURRENCY) || 3;
  const limit = pLimit(concurrency);

  while (true) {
    const tasks = await fetchRunnableTasks(jobId, 50);
    if (tasks.length === 0) break;

    await Promise.all(
      tasks.map(task =>
        limit(async () => {
          await setTaskStatus(task.id, 'running');
          const page = await newPage(browser);
          try {
            const parsed = await parsePdp(page, task.pdp_url);
            const brandId = await upsertBrand(parsed.brand);
            const catId = await ensureCategory(parsed.category);
            const styleId = await upsertStyle({
              brand_id: brandId,
              category_id: catId,
              name: parsed.name,
              description: parsed.description ?? null
            });
            const variantId = await upsertVariant({ style_id: styleId });
            await upsertProductUrl(variantId, task.pdp_url);
            if (parsed.price) await insertPrice(variantId, parsed.price, parsed.currency || 'USD');

            for (let i = 0; i < parsed.images.length; i++) {
              const src = parsed.images[i];
              const { storagePath, width, height } = await uploadImageToStorage(styleId, variantId, src, i);
              await insertImageRow(variantId, styleId, src, i, storagePath || undefined, i === 0, width || undefined, height || undefined);
            }

            await setTaskStatus(task.id, 'done');
          } catch (e: any) {
            await setTaskStatus(task.id, 'error', String(e?.message || e));
          } finally {
            await page.close();
          }
        })
      )
    );
  }

  await q(`update ingestion_job set status='done', finished_at=now() where id=$1`, [jobId]);
}


