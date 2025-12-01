# Database Hardening & Credential Rotation – 2025-11-28

## Objectives
- Move every service (backend, scripts, iOS helpers) onto the fs-core connection string.
- Replace the leaked Tailor3 `postgres.lbilxlkchzpducggkrxx / efvTower1211` credentials with a scoped login.
- Bring `core.products` up to the Tailor3 schema (base name, updated timestamps, uniqueness).
- Document outstanding work so we can resume after pausing for scraper tasks.

## Work Completed Today
### Centralized configuration
- `.env` now points to the fs-core host (`aws-1-us-east-1.pooler.supabase.com:5432`) and keeps the existing superuser credentials for now.
- `scripts/database/db_config.py` now validates that **all** env vars are set and exports a single `DB_CONFIG`.
- Both FastAPI backends (`src/ios_app/Backend/app.py` and `main.py`) import `DB_CONFIG`, so they cannot silently fall back to Tailor3 defaults.
- Bulk search-and-replace removed the old Tailor3 host/user/port/password defaults across active code directories; sample scripts now default to `fs_core_rw` + `CHANGE_ME`.

### Schema tightening
- Added `base_name` (NOT NULL), `updated_at` (default `now()`), and the `(brand_id, product_code)` unique constraint to `core.products`.
- Added `core.set_products_updated_at()` trigger so `updated_at` stays accurate.
- Enforced NOT NULL on `brand_id`, `product_code`, and backfilled `base_name`.

### Credential rotation groundwork
- Created a new Postgres role `fs_core_rw_app`, granted it login rights, and made it inherit the existing `fs_core_rw` privileges (`grant fs_core_rw to fs_core_rw_app;`).
- Confirmed Supabase CLI v2.62.10 is installed and project `rybsqzlqywjcvoxsymsi` is linked.
- Attempted to register the new login with the shared pooler; CLI reports that `db pooler` subcommands are unavailable and the dashboard lacks a “Manage pooler users” UI.

## Current Roadblocks
- **Pooler registration**: PgBouncer still rejects `fs_core_rw_app` (`Tenant or user not found`). Supabase must add this login to the pooler allow-list manually because neither the dashboard nor CLI exposes that control for this project.
- Until the new login is recognized, `.env` must keep `postgres.rybsqzlqywjcvoxsymsi / efvTower1211` so scrapers continue working.

## Next Steps (when we return)
1. Open a Supabase support ticket requesting that `fs_core_rw_app` with password `fs_core` be added to the pooler for project `rybsqzlqywjcvoxsymsi`.
2. Once support confirms, rerun:  
   `psql "postgres://fs_core_rw_app:fs_core@aws-1-us-east-1.pooler.supabase.com:5432/postgres" -c "select current_user;"`.
3. Update `.env` and any secrets managers to `DB_USER=fs_core_rw_app`, `DB_PASSWORD=fs_core`, restart services, and verify ingestion works.
4. After the rotation succeeds, scrub the old password from `.env`, secrets, and documentation, then resume category scraping.

## Notes for Scraper Work
- `scripts/jcrew_category_ingest.py` is ready; Ludlow run succeeded with fs-core credentials earlier.
- Once credentials rotate, re-test one PDP ingest to confirm nothing else regressed.

This doc captures the checkpoint so we can jump back to scraping after support registers the pooler login.





