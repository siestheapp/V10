### Schema Evolution and History

This section aggregates pointers and summaries of how the database has changed over time.

#### Sources of Truth

- Daily snapshots and actual-state doc:
  - `daily-notes/2025-09-17/DATABASE_SCHEMA_ACTUAL.md`
  - `DATABASE_SCHEMA_COMPLETE.md` (keep aligned; ACTUAL notes flagged inconsistencies)

- Tailor2 legacy evolution (for context only):
  - `archive/old_schemas/tailor2/SCHEMA_EVOLUTION.md`

- Automated tools:
  - `scripts/database/schema_evolution.py` — creates snapshots and diffs; updates a markdown log
  - `scripts/development/get_complete_schema.sh` — prints structures for all public tables
  - `scripts/database/db_snapshot.py` — JSON snapshot of counts and relationships

#### Major Transitions

- Migration from local `tailor2` to Supabase `tailor3` (production)
- Measurements system shift:
  - From `size_guides` + `size_guide_entries` (legacy)
  - To `measurement_sets` + `measurements` (preferred/current)
- Product modeling:
  - Establish `product_master` for base codes and `product_variants` for color/fit permutations
  - Introduce `jcrew_product_cache` as ingestion staging area
- Feedback normalization:
  - Use `feedback_codes` with `user_garment_feedback` for dimensional, deduped semantics
  - Track user activity via `user_actions`

#### How to Capture Future Changes

1. Run the evolution script after making schema changes:
   - `python3 scripts/database/schema_evolution.py`
2. Commit updated snapshots and the generated markdown entry.
3. Update `DATABASE_SCHEMA_COMPLETE.md` and reconcile with `DATABASE_SCHEMA_ACTUAL.md` when divergences appear.

#### Known Documentation Gaps

- Ensure columns for `measurement_sets`/`measurements` are fully documented in `DATABASE_SCHEMA_COMPLETE.md`.
- Audit any remaining code paths that still depend on `size_guides` and schedule migrations.



