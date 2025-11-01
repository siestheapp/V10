#!/usr/bin/env node
// Batch test J.Crew product URLs using Supabase REST, mirroring the Scan screen lookup.
// Usage:
//   node ./scripts/test-scan-links.mjs <url1> <url2> ...
// If no args are provided, it will pull from known files in the repo.

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, '..', '..');

// Minimal .env loader (root .env)
function loadEnv() {
  const envPath = path.join(projectRoot, '.env');
  if (!fs.existsSync(envPath)) return;
  const lines = fs.readFileSync(envPath, 'utf8').split(/\r?\n/);
  for (const line of lines) {
    if (!line || line.trim().startsWith('#')) continue;
    const eq = line.indexOf('=');
    if (eq === -1) continue;
    const key = line.slice(0, eq).trim();
    const val = line.slice(eq + 1).trim().replace(/^"|"$/g, '');
    if (!(key in process.env)) process.env[key] = val;
  }
}
loadEnv();

const SUPABASE_URL = process.env.EXPO_PUBLIC_SUPABASE_URL;
const SUPABASE_KEY = process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY;
if (!SUPABASE_URL || !SUPABASE_KEY) {
  console.error('Missing EXPO_PUBLIC_SUPABASE_URL or EXPO_PUBLIC_SUPABASE_ANON_KEY in .env');
  process.exit(1);
}

function normalizeUrl(raw) {
  const trimmed = String(raw || '').trim();
  if (!trimmed) return '';
  const withProtocol = /^[a-zA-Z][a-zA-Z\d+.-]*:/.test(trimmed) ? trimmed : `https://${trimmed}`;
  try {
    const url = new URL(withProtocol);
    url.hostname = url.hostname.toLowerCase();
    const removable = new Set(['fbclid', 'gclid', 'ref']);
    const params = url.searchParams;
    Array.from(params.keys()).forEach((key) => {
      const lower = key.toLowerCase();
      if (lower.startsWith('utm') || removable.has(lower)) {
        params.delete(key);
      }
    });
    url.search = params.toString() ? `?${params.toString()}` : '';
    url.hash = '';
    if (url.pathname !== '/') {
      url.pathname = url.pathname.replace(/\/+/g, '/');
      if (url.pathname.endsWith('/')) {
        url.pathname = url.pathname.replace(/\/+$/, '');
        if (!url.pathname) url.pathname = '/';
      }
    }
    return url.toString();
  } catch {
    return trimmed;
  }
}

function getTrailingPath(input) {
  try {
    const url = new URL(input);
    const pathname = url.pathname.endsWith('/') && url.pathname !== '/' ? url.pathname.replace(/\/+$/, '') : url.pathname;
    const pathOnly = pathname === '/' ? '' : pathname;
    const search = url.search;
    const trailing = `${pathOnly}${search}`.replace(/^\/+/, '');
    return trailing || null;
  } catch {
    return null;
  }
}

const headers = {
  apikey: SUPABASE_KEY,
  Authorization: `Bearer ${SUPABASE_KEY}`,
};

async function rpcProductLookup(url) {
  const res = await fetch(`${SUPABASE_URL}/rest/v1/rpc/product_lookup`, {
    method: 'POST',
    headers: { ...headers, 'Content-Type': 'application/json' },
    body: JSON.stringify({ input_url: url }),
  });
  if (!res.ok) return [];
  return await res.json();
}

async function selectFromView(view, normalized, trailing, includeImage) {
  const columns = includeImage
    ? 'brand,style_name,style_code,fit,color,variant_code,product_url,image_url'
    : 'brand,style_name,style_code,fit,color,variant_code,product_url';

  // exact
  {
    const q = new URL(`${SUPABASE_URL}/rest/v1/${view}`);
    q.searchParams.set('select', columns);
    q.searchParams.set('product_url', `eq.${normalized}`);
    q.searchParams.set('limit', '1');
    const res = await fetch(q.toString(), { headers });
    if (!res.ok) throw new Error(`select ${view} failed: ${res.status}`);
    const rows = await res.json();
    if (Array.isArray(rows) && rows.length) return rows;
  }

  if (trailing) {
    const q2 = new URL(`${SUPABASE_URL}/rest/v1/${view}`);
    q2.searchParams.set('select', columns);
    // anywhere match (equivalent to %trailing)
    q2.searchParams.set('product_url', `ilike.*${trailing}`);
    q2.searchParams.set('limit', '1');
    const res2 = await fetch(q2.toString(), { headers });
    if (!res2.ok) throw new Error(`ilike ${view} failed: ${res2.status}`);
    const rows2 = await res2.json();
    if (Array.isArray(rows2) && rows2.length) return rows2;
  }

  return [];
}

async function selectFromCache(normalized, trailing) {
  // Exact
  let row = null;
  {
    const q = new URL(`${SUPABASE_URL}/rest/v1/jcrew_product_cache`);
    q.searchParams.set('select', 'product_url,product_image,product_code');
    q.searchParams.set('product_url', `eq.${normalized}`);
    q.searchParams.set('limit', '1');
    const res = await fetch(q.toString(), { headers });
    if (!res.ok) return [];
    const rows = await res.json();
    row = Array.isArray(rows) && rows[0] ? rows[0] : null;
  }
  // Prefix
  if (!row && trailing) {
    const q2 = new URL(`${SUPABASE_URL}/rest/v1/jcrew_product_cache`);
    q2.searchParams.set('select', 'product_url,product_image,product_code');
    q2.searchParams.set('product_url', `ilike.*${trailing}`);
    q2.searchParams.set('limit', '1');
    const res2 = await fetch(q2.toString(), { headers });
    if (!res2.ok) return [];
    const rows2 = await res2.json();
    row = Array.isArray(rows2) && rows2[0] ? rows2[0] : null;
  }
  if (!row) return [];

  // Enrich with product_master + brands
  let styleName = '';
  let brandName = '';
  const code = row.product_code || null;
  if (code) {
    const pm = new URL(`${SUPABASE_URL}/rest/v1/product_master`);
    pm.searchParams.set('select', 'base_name,brand_id');
    pm.searchParams.set('product_code', `eq.${code}`);
    pm.searchParams.set('limit', '1');
    const pmRes = await fetch(pm.toString(), { headers });
    if (pmRes.ok) {
      const pmRows = await pmRes.json();
      if (Array.isArray(pmRows) && pmRows[0]) {
        styleName = pmRows[0].base_name || '';
        const brandId = pmRows[0].brand_id;
        if (brandId != null) {
          const b = new URL(`${SUPABASE_URL}/rest/v1/brands`);
          b.searchParams.set('select', 'name');
          b.searchParams.set('id', `eq.${brandId}`);
          b.searchParams.set('limit', '1');
          const bRes = await fetch(b.toString(), { headers });
          if (bRes.ok) {
            const bRows = await bRes.json();
            brandName = Array.isArray(bRows) && bRows[0] ? (bRows[0].name || '') : '';
          }
        }
      }
    }
  }

  return [
    {
      brand: brandName,
      style_name: styleName,
      style_code: code,
      fit: null,
      color: null,
      variant_code: null,
      product_url: row.product_url || normalized,
      image_url: row.product_image || null,
    },
  ];
}

async function fetchProductByUrlLikeApp(url) {
  const normalized = normalizeUrl(url);
  if (!normalized) return [];
  const trailing = getTrailingPath(normalized);

  // 1) RPC product_lookup
  try {
    const rpc = await rpcProductLookup(normalized);
    if (Array.isArray(rpc) && rpc.length) return rpc;
  } catch {}

  // 2) v_product_variants_img
  try {
    const withImg = await selectFromView('v_product_variants_img', normalized, trailing, true);
    if (withImg && withImg.length) return withImg;
  } catch {}

  // 3) v_product_variants
  try {
    const fallback = await selectFromView('v_product_variants', normalized, trailing, false);
    if (fallback && fallback.length) return fallback;
  } catch {}

  // 4) cache fallback
  return await selectFromCache(normalized, trailing);
}

function readUrlsFromKnownFiles() {
  const files = [
    path.join(projectRoot, 'jcrew_all_21_urls.json'),
    path.join(projectRoot, 'jcrew_secret_wash_urls.json'),
  ];
  const urls = [];
  for (const file of files) {
    if (!fs.existsSync(file)) continue;
    try {
      const raw = fs.readFileSync(file, 'utf8');
      const json = JSON.parse(raw);
      if (Array.isArray(json)) {
        for (const entry of json) {
          const u = typeof entry === 'string' ? entry : entry?.url;
          if (u) urls.push(u);
        }
      } else if (json && Array.isArray(json.urls)) {
        for (const u of json.urls) if (typeof u === 'string') urls.push(u);
      }
    } catch {}
  }
  return urls;
}

function uniqueUrls(list) {
  const seen = new Set();
  const out = [];
  for (const u of list) {
    const n = normalizeUrl(u);
    if (!n || seen.has(n)) continue;
    seen.add(n);
    out.push(n);
  }
  return out;
}

async function main() {
  const argvUrls = process.argv.slice(2).filter((x) => x && !x.startsWith('--'));
  const urls = uniqueUrls(argvUrls.length ? argvUrls : readUrlsFromKnownFiles());
  if (!urls.length) {
    console.error('No URLs provided and no known URL files found.');
    process.exit(1);
  }

  const results = [];
  let ok = 0, fail = 0;
  for (const url of urls) {
    try {
      const data = await fetchProductByUrlLikeApp(url);
      if (data && data.length) {
        ok++;
        results.push({ url, found: true, product: data[0] });
      } else {
        fail++;
        results.push({ url, found: false });
      }
    } catch (e) {
      fail++;
      results.push({ url, found: false, error: e?.message || String(e) });
    }
  }

  const summary = { total: urls.length, ok, fail };
  console.log(`Tested ${summary.total} URLs → OK ${summary.ok}, FAIL ${summary.fail}`);
  const failures = results.filter(r => !r.found);
  if (failures.length) {
    console.log('Failures:');
    for (const f of failures) console.log(`- ${f.url}${f.error ? ` :: ${f.error}` : ''}`);
  }

  const outPath = path.join(projectRoot, 'scan_link_test_results.json');
  fs.writeFileSync(outPath, JSON.stringify({ summary, results }, null, 2));
  console.log(`Detailed results written to ${outPath}`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});









