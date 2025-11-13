### Freestyle (V10) — Database One-Pager (Supabase tailor3)

#### App purpose (context for schema)

Freestyle helps users log in-store try-ons and owned garments to learn their best sizes and fits across brands. The app:
- Captures what the user tried/owns (`user_garments`), including brand, product, size, and photos
- Records dimensional fit feedback (e.g., chest tight/loose) via `user_garment_feedback` using normalized `feedback_codes`
- Uses brand size guides/measurements to infer fit zones and make cross-brand recommendations

#### Where the database connects to the codebase

- Primary backend service: `src/ios_app/Backend/app.py` and `src/ios_app/Backend/fit_zone_service.py`
  - Uses `psycopg2` and `asyncpg` with connection info from environment or `db_config.py`
  - Pooled async connections for heavier endpoints
- Shared configuration: `db_config.py` defines `DB_CONFIG` and a `psql` helper
- Data ingestion and maintenance scripts under `scripts/` (e.g., J.Crew cache to master/variants, cleanup, snapshots)

#### Current model overview (high-level)

- Products and variants
  - `brands` — canonical brands
  - `product_master` — one row per base product code (e.g., BE996)
  - `product_variants` — color/fit variants under a master record
  - `jcrew_product_cache` — scraped cache used to populate/consolidate

- Measurements and size guides
  - Preferred direction: `measurement_sets` + `measurements` (unified system)
  - Legacy (heavily referenced in code today): `size_guides` + `size_guide_entries`
    - App frequently joins `user_garments.size_guide_entry_id -> size_guide_entries.id`
    - Brand-level measurements and size availability are often sourced from size guide tables

- Users, feedback, and activity
  - `user_garments` — a user's owned/tried garments; references brand and optionally a product/master
  - `user_garment_feedback` — per-dimension feedback; normalized via `feedback_codes`
  - `user_actions` — activity/audit trail (submit/update feedback, scans, etc.)

See also: `supabase/schema_overview.md` and `supabase/key_tables.md` for details, and `daily-notes/2025-09-17/DATABASE_SCHEMA_ACTUAL.md` for the latest, exhaustive view.

#### Key size guide usage patterns in code (why it matters for redesign)

- Latest dimensional feedback via subqueries that fall back to guide data when available
- Joins like:
  - `LEFT JOIN size_guide_entries sge ON user_garments.size_guide_entry_id = sge.id`
  - Fetch brand-size ranges: `FROM size_guides sg JOIN size_guide_entries sge ON sge.size_guide_id = sg.id WHERE sg.brand_id = $1 AND sge.size_label = $2`
- Brand measurements often accessed as columns like `chest_min/chest_max`, `waist_min/waist_max`, `sleeve_min/sleeve_max`, `neck_min/neck_max`

Implication: Even as `measurement_sets`/`measurements` become the primary model, many endpoints and analyses still depend on `size_guides`/`size_guide_entries` columns and IDs.

#### Guidance for schema redesign (products-focused while preserving size guides)

Goal: Introduce a richer product schema without losing existing size-guide-powered features.

Recommended approach:
1) Keep legacy size guide tables online during transition
   - Maintain `size_guides` and `size_guide_entries` to avoid breaking existing flows
   - Provide a compatibility view layer if needed (e.g., views that map from new measurement storage back to the legacy column shapes)

2) Land the new product schema alongside existing tables
   - Extend or refactor `product_master` and `product_variants` with normalized product attributes, taxonomy, and materials
   - Add tables for product attributes, options, and media as needed (e.g., `product_attributes`, `product_media`, `option_values`)

3) Converge measurements under `measurement_sets`/`measurements`
   - Define set context: brand, category/subcategory, fit, garment type, unit
   - Store per-dimension ranges per size in `measurements`
   - Backfill from `size_guide_entries` and maintain forward compatibility via views

4) Introduce reference integrity and lookup helpers
   - Ensure `user_garments` can link to either a legacy size guide entry or a `measurement_set` + size row
   - Add helper functions (SQL or server-side) to resolve “latest feedback per dimension” using window functions instead of repeated subqueries

5) Plan deprecation
   - Once endpoints are migrated to the new measurement model, phase out direct reads from `size_guide_entries`
   - Freeze writes to legacy tables and remove triggers after a stabilization period

#### Quick reference

- Connection: see `db_config.py` and `supabase/operations.md`
- Active schema docs: `daily-notes/2025-09-17/DATABASE_SCHEMA_ACTUAL.md`
- Overview: `supabase/schema_overview.md`, `supabase/key_tables.md`
- Queries: `supabase/query_reference.md`
- Evolution: `supabase/schema_evolution.md` and `scripts/database/schema_evolution.py`


