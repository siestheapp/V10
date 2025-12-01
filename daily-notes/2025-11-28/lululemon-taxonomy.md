## 2025-11-28 – Lululemon taxonomy + color support

### Schema changes (executed directly in fs-core)
- Added `core.categories` (id serial PK, slug unique, optional `parent_id`, `metadata`, `created_at`).
- Added `core.subcategories` (id serial PK, FK to `core.categories`, unique per `(category_id, slug)`).
- Attached FKs from `core.brand_category_map.category_id` → `core.categories.id` (cascade) and `subcategory_id` → `core.subcategories.id` (set null).
- Added `UNIQUE (brand_id, source_category)` to `core.brand_category_map` for deterministic upserts.
- Added `core.colors` unique index on `canonical_name`.
- Added unique index on `core.brand_colors (brand_id, color_code)`.

### Seed data
- Categories: `menswear` (root) → `mens-shirts`.
- Subcategories under `mens-shirts`: `button-down-shirts`, `broken-in-oxford`, `linen-shirts`, `dress-shirts`.
- Brand mappings:
  - J.Crew → each of the four subcategories above (so legacy data resolves cleanly).
  - Lululemon → `Button Down Shirts` → `mens-shirts` / `button-down-shirts`.
- Canonical colors inserted (`blue`, `green`, `grey`, `white`, `pink`) plus Lululemon brand-color rows for codes `36865/49106/64917/73731/73732` including swatch URLs + normalized families.

### Next steps
- Extend `core.resolve_product_by_url` for Lululemon PDP structures.
- Wire the category ingest/crawler to call `lululemon_full_ingest` and automatically populate `brand_category_map` entries for any new source labels that appear.





