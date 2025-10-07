### Schema Overview (tailor3)

This is a high-level map of the current data model, with notes on deprecated parts. For full details, see `key_tables.md` and `daily-notes/2025-09-17/DATABASE_SCHEMA_ACTUAL.md`.

#### Current Systems

- Product catalog
  - `brands` → core list of brands
  - `product_master` → one row per base product code (e.g., BE996)
  - `product_variants` → color/fit variants tied to a `product_master`
  - `jcrew_product_cache` → scraped cache used to populate/consolidate into master/variants

- Measurements and guides
  - Preferred: `measurement_sets` + `measurements` (per latest docs)
  - Legacy still present/queried in places: `size_guides`, `size_guide_entries`

- User garments and feedback
  - `user_garments` → a user's owned/tried garments, ties to brand/product context
  - `user_garment_feedback` → dimensional feedback references `feedback_codes`
  - `feedback_codes` → normalized set of allowed feedback tokens/text
  - `user_actions` → activity log of user actions in the app

- Categorization
  - `categories`, `subcategories` referenced by `product_master`

#### Deprecated/Legacy

- `size_guides` + `size_guide_entries` — retained for back-compat and some queries; migrate to measurement sets when possible
- Local `tailor2` schemas — do not reference for new work

#### Notable Relationships

- `product_master (1) — (N) product_variants`
- `brands (1) — (N) product_master` and `brands (1) — (N) user_garments`
- `user_garments (1) — (N) user_garment_feedback` with `feedback_code_id` → `feedback_codes.id`

See: `DATABASE_SCHEMA_COMPLETE.md` and `daily-notes/2025-09-17/DATABASE_SCHEMA_ACTUAL.md` for column-level specifics.



