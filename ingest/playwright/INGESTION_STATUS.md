# Reformation Dresses Ingestion – Status Report

Date: 2025-10-12

## What’s implemented

- Project scaffold under `ingest/playwright/` (TypeScript, Playwright, Supabase, Postgres).
- Env loading via `.env` and `dotenv-cli` for `psql` parity.
- DB helpers: `src/db/pg.ts` (pg pool), `src/db/upsert.ts` (`public.*` tables: brand/category/style/variant/product_url/price_history/product_images).
- Storage: `src/images/storage.ts` uploading to Supabase public bucket (no sharp, tolerant to failures).
- Core: `withBrowser/newPage`, image helpers.
- Adapter: `src/adapters/reformation.ts` with category crawler (cookie + infinite scroll) and PDP parser.
- Jobs: `createJob`, `seedCategoryTasks`, `runWorker` + CLI `src/index.ts`.
- One‑shot runner `src/jobs/run.ts` and debug crawler `scripts/debug-crawl.ts`.
- SQL: `sql/001_jobs_and_images.sql` (jobs/tasks/images minimal). Runtime ALTERs aligned Supabase `public` schema.

## Verified behavior

- Targeting: `psql` and Node target Supabase when run via `dotenv -e .env -- sh -c '…'`.
- TLS: Preflight works with `NODE_TLS_REJECT_UNAUTHORIZED=0` (temporary); permanent CA fix documented.
- Crawler: `https://www.thereformation.com/dresses` yields PDP URLs (debug run found 65 links).
- Job creation: `ingestion_job` rows created with correct `category_url`.

## Current issues / gaps

1) TLS for Node (pg)
- Node connections error without a CA override on this machine. Temporary workaround used.
- Proper fix: install CA bundle and set `NODE_EXTRA_CA_CERTS` (Homebrew `ca-certificates`) or configure pg ssl with trusted certs.

2) Migration/schema mismatches
- Supabase uses `public.style`, `public.variant`, etc. Upserts updated to `public.*`; `public.product_images` created without FKs.
- `ingestion_job` originally lacked `category_url`, `totals`, etc.; added via `ALTER TABLE`.

3) Seeding didn’t persist tasks
- Crawler returned 65 PDP URLs (logged), but zero rows appeared in `public.ingestion_task` after seeding.
- Inserts now reference `public.ingestion_task` explicitly; still zero rows and no thrown errors.

4) Worker not run (no tasks present)
- Since no tasks persisted, the worker had nothing to process.

## Evidence

- Target (Supabase): `current_database=postgres`, `current_user=postgres`; `\dt public.*` lists `brand/category/style/variant/product_url/...`.
- Debug crawl: `npx ts-node scripts/debug-crawl.ts https://www.thereformation.com/dresses` → `Found PDP URLs: 65`.
- Seeding log: `[seedCategoryTasks] Collected 65 PDP urls for job 2`, but `select status,count(*) from public.ingestion_task where job_id=2` → 0 rows.

## Likely causes for missing inserts

- TLS/SSL nuance on pooled Node pg connections (less likely; would usually throw).
- Privileges/RLS blocking inserts (verify RLS off for these tables; check grants for `postgres`).
- Different Postgres URL at runtime vs `psql` (log `process.env.DATABASE_URL` and `select current_database(), current_user;` inside Node).
- Silent error swallowed in code path (add explicit try/catch + logging around q()).

## Recommended next steps

1) Make TLS trust permanent
- `brew install ca-certificates`
- `export NODE_EXTRA_CA_CERTS="$(brew --prefix openssl@3)/etc/openssl@3/cert.pem"` and add to shell profile.

2) Add insert diagnostics
- Log first 3 URLs and results of each `insert into public.ingestion_task…` with error messages.

3) Confirm DB URL and identity inside Node
- Log `process.env.DATABASE_URL` and run `select current_database(), current_user;` via `q()` in `seedCategoryTasks`.

4) Manual insert from Node
- Run a one-off ts-node script to insert a single row into `public.ingestion_task` and select it back.

5) Fallback seeding mode
- Accept a newline‑delimited file of PDP URLs to seed tasks (skip crawling) to unblock ingestion.

6) Adapter hardening
- Retry/backoff for crawling, cap URLs, normalize PDP URLs (strip color query), dedupe.

## How to run (current sequence)

- Verify target and schema:
  - `npx dotenv -e .env -- sh -c 'psql "$DATABASE_URL" -c "select current_database(), current_user;"'`
  - `npx dotenv -e .env -- sh -c 'psql "$DATABASE_URL" -c "\\dt public.*"'`
- Create job:
  - `NODE_TLS_REJECT_UNAUTHORIZED=0 npm run init-job -- --category "https://www.thereformation.com/dresses" --brand "Reformation"`
- Seed tasks:
  - `NODE_TLS_REJECT_UNAUTHORIZED=0 npm run seed-tasks -- --job <id>`
- Prune to 5 tasks:
  - `npx dotenv -e .env -- sh -c "psql \"$DATABASE_URL\" -c \"delete from public.ingestion_task where job_id=<id> and id not in (select id from public.ingestion_task where job_id=<id> order by id asc limit 5);\""`
- Run worker:
  - `NODE_TLS_REJECT_UNAUTHORIZED=0 npm run run-worker -- --job <id> --concurrency 1`

## Summary

Infra, adapter, and jobs are in place; crawler validated on the live Dresses category. Task inserts didn’t persist despite no errors; likely env/TLS/role nuance. Apply TLS trust, add insert diagnostics, and consider a file‑based seeding path to unblock ingestion immediately.
