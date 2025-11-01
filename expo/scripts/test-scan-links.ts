#!/usr/bin/env ts-node
/*
 Batch test J.Crew product URLs using the same logic as the Scan screen.
 Reads URLs from args or known JSON files and reports whether lookup finds a product.
*/

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';

// Load env from project root .env so Supabase client works
const projectRoot = path.resolve(__dirname, '..', '..');
dotenv.config({ path: path.join(projectRoot, '.env') });

// Import the same functions the app uses
import { fetchProductByUrl, normalizeUrl } from '../lib/product';
import supabase from '../lib/supabase';

type Source = { name: string; urls: string[] };

function readUrlsFromKnownFiles(): Source[] {
  const candidates = [
    path.join(projectRoot, 'jcrew_all_21_urls.json'),
    path.join(projectRoot, 'jcrew_secret_wash_urls.json'),
  ];
  const sources: Source[] = [];
  for (const file of candidates) {
    if (!fs.existsSync(file)) continue;
    try {
      const raw = fs.readFileSync(file, 'utf8');
      const json = JSON.parse(raw);
      if (Array.isArray(json)) {
        const urls = json.map((x: any) => (typeof x === 'string' ? x : x.url)).filter(Boolean);
        if (urls.length) sources.push({ name: path.basename(file), urls });
      } else if (json && Array.isArray(json.urls)) {
        const urls = json.urls.filter((u: any) => typeof u === 'string');
        if (urls.length) sources.push({ name: path.basename(file), urls });
      }
    } catch {}
  }
  return sources;
}

function uniqueUrls(urls: string[]): string[] {
  const seen = new Set<string>();
  const out: string[] = [];
  for (const u of urls) {
    const norm = normalizeUrl(String(u));
    if (!norm) continue;
    if (seen.has(norm)) continue;
    seen.add(norm);
    out.push(norm);
  }
  return out;
}

async function testOne(url: string) {
  const results = await fetchProductByUrl(supabase, url);
  return results;
}

async function main() {
  const argvUrls = process.argv.slice(2).filter((x) => x && !x.startsWith('--'));
  const allSources: Source[] = [];
  if (argvUrls.length) {
    allSources.push({ name: 'argv', urls: argvUrls });
  }
  allSources.push(...readUrlsFromKnownFiles());
  if (!allSources.length) {
    console.error('No URLs provided and no known files found.');
    console.error('Usage: pnpm test:scan-links <url1> <url2> ...');
    process.exit(1);
  }

  const merged = uniqueUrls(allSources.flatMap((s) => s.urls));
  const summary = { total: merged.length, ok: 0, fail: 0 };

  const results: Array<{ url: string; found: boolean; product?: any; error?: string }> = [];

  for (const url of merged) {
    try {
      const res = await testOne(url);
      if (res && res.length) {
        summary.ok += 1;
        results.push({ url, found: true, product: res[0] });
      } else {
        summary.fail += 1;
        results.push({ url, found: false });
      }
    } catch (e: any) {
      summary.fail += 1;
      results.push({ url, found: false, error: e?.message || String(e) });
    }
  }

  // Print concise table
  console.log(`Tested ${summary.total} URLs → OK ${summary.ok}, FAIL ${summary.fail}`);
  const failures = results.filter((r) => !r.found);
  if (failures.length) {
    console.log('Failures:');
    for (const f of failures) {
      console.log(`- ${f.url}${f.error ? ` :: ${f.error}` : ''}`);
    }
  }

  // Save detailed JSON for inspection
  const outPath = path.join(projectRoot, 'scan_link_test_results.json');
  fs.writeFileSync(outPath, JSON.stringify({ summary, results }, null, 2));
  console.log(`Detailed results written to ${outPath}`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});









