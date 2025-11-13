import 'dotenv/config';
import { createClient } from '@supabase/supabase-js';
import crypto from 'crypto';
import fetch from 'node-fetch';

const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

const BUCKET = process.env.SUPABASE_STORAGE_BUCKET!;

export async function downloadBuffer(url: string): Promise<Buffer | null> {
  const res = await fetch(url, { timeout: 30000 } as any);
  if (!res.ok) return null;
  const arr = await (res as any).arrayBuffer();
  return Buffer.from(arr);
}

function guessExtensionFromUrl(url: string): string {
  const ext = url.split('?')[0].split('.').pop()?.toLowerCase();
  if (!ext) return 'jpg';
  if (['jpg', 'jpeg', 'png', 'webp', 'gif', 'avif'].includes(ext)) return ext === 'jpg' ? 'jpeg' : ext;
  return 'jpeg';
}

export async function uploadImageToStorage(
  styleId: number,
  variantId: number,
  srcUrl: string,
  position: number
) {
  const buf = await downloadBuffer(srcUrl);
  if (!buf) return { storagePath: null as string | null, width: null as number | null, height: null as number | null };

  const hash = crypto.createHash('sha1').update(buf).digest('hex').slice(0, 16);
  const ext = guessExtensionFromUrl(srcUrl);
  const objectPath = `styles/${styleId}/variants/${variantId}/${position}-${hash}.${ext}`;

  const { error } = await supabase.storage.from(BUCKET).upload(objectPath, buf, {
    contentType: `image/${ext}`,
    upsert: false
  });

  if (error && !String(error.message).includes('The resource already exists')) {
    console.error('upload error', error.message);
    return { storagePath: null, width: null, height: null };
  }

  return { storagePath: objectPath, width: null, height: null };
}


