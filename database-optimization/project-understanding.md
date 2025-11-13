# Project Understanding (Living Doc)

This file captures the evolving understanding and decisions for the unified fs-core database and how it supports the product’s three phases and both existing apps (V10, Freestyle). It will be updated as we refine requirements and wire up the new Expo app to fs-core.

## Objective

- Build a single Supabase (Postgres) database, fs-core, that:
  - Supports LOGGER first: try-on logging via pasted product URLs, records size and fit feedback, optional photos.
  - Extends to SIES: normalized, versioned size guides and per-size measurements; derive user measurement profiles.
  - Extends to PROXI: social discovery based on shared sizes and inferred measurements; future follows/likes/saves/messaging.

## Current Databases and Roles

- tailor3 (reference only): richer product cache for J.Crew (colors, fits, sizes), measurement_sets/measurements, detailed try-on models (`user_garments`, `user_garment_feedback`). Good pattern source for structured product and measurement modeling.
- freestyledb (reference only): catalog ingestion and URL canonicalization primitives; user_closet + fit_feedback (simpler). Good source for URL→variant resolution and catalog helpers.
- fs-core (target): new unified DB on Supabase; LOGGER base schema running (users, brands, products, user_garments, user_fit_feedback, media) with RLS and auth trigger. Variants/URLs pack and BE996 seed to be completed next.

## Data Model Direction (fs-core)

- Catalog
  - `core.brands` (name/slug; unique on slug).
  - `core.products` (brand, product_code, name/title, category/subcategory; raw JSONB).
  - `core.product_variants` (product_id, color_name, fit_name, generated normalized keys; unique on (product_id, color_name_norm, fit_name_norm); SKU/URL/attrs).
  - `core.product_urls` (style-level and optional variant-level canonical URLs; resolver function).
  - `core.product_images` (variant images with “one primary per variant” constraint).
- LOGGER
  - `core.user_garments` (user, product/variant, size_label, owns/status, notes, product_url, raw, timestamps).
  - `core.user_fit_feedback` (per-dimension codes and notes; linked to user_garment).
  - `content.media` (image/video refs stored in Supabase Storage; URL + metadata).
- SIES
  - `guides.measurement_sets` (brand/category/gender/fit scope; versioned; is_active).
  - `guides.measurements` (set_id, size_label, measurement_type, min/max/exact, unit; indexed for fast lookup).
  - `core.user_measurements` + `core.measurement_estimates` (canonical values and estimator outputs).
- PROXI
  - `core.user_size_profiles` (denormalized numeric profile for fast matching; optional vector field later).
  - Future social tables: follows, likes/saves, messaging (separate schema), with RLS.

## Security and Operations

- Supabase Auth as source of truth; trigger mirrors `auth.users` → `core.users` (UUID).
- RLS enabled on user-owned tables (`core.users`, `core.user_garments`, `core.user_fit_feedback`, `content.media`). Policies bind to `auth.uid()` via `core.current_user_v`.
- Indexing: B-tree on FKs; generated columns on normalized variant names; partial unique index for primary images; GIN for JSONB as needed.
- Scaling: single DB with read replicas; consider hash partitioning by `user_id` for `core.user_garments` at larger scale. Later peel off search/messaging/analytics if metrics warrant.

## Alignment with Existing Apps

- V10 (LOGGER + advanced backend features)
  - Needs: paste product URL → resolve style/variants; present size options; capture fit feedback; attach photos; later use measurement inference (SIES) and robust product cache.
  - fs-core coverage: `core.product_urls` + resolver, `core.product_variants`, LOGGER tables, measurement_sets/measurements for SIES.
- Freestyle (catalog ingest + social concepts)
  - Needs: URL canonicalization, upsert helpers, simple user closet + feedback, media, and proxy-style discovery.
  - fs-core coverage: helpers and URL resolver (ported), unified try-on logging model, social scaffolding planned.

## Near-Term Tasks (DB)

- Complete variants/URLs pack in fs-core:
  - Ensure `core.product_variants` exists with generated normalized columns and unique (product_id, color_name_norm, fit_name_norm).
  - Ensure `core.product_urls`, resolver function, and `core.product_images` (with primary-image unique index) exist.
- Seed J.Crew BE996 with full fits/colors and a canonical PDP URL; verify resolver returns (product_id, variant_id).
- Draft SIES tables (`guides.measurement_sets`, `guides.measurements`) and indices per plan; add minimal seed guides for target brands/categories.

## Near-Term Tasks (App)

- Inventory feature needs from V10 and Freestyle Expo apps:
  - LOGGER screens: URL paste, size selection, fit feedback form, closet view, photo upload.
  - Data flows: endpoints for brand/product/variant upsert, URL resolution, try-on creation, feedback creation, media attach.
- Map endpoints to fs-core tables and propose a phased API checklist for the new Expo app.

## Open Questions / Decisions

- Category taxonomy: confirm final approach (two tables categories/subcategories vs self-referential). Current plan favors two tables.
- Measurement types: maintain reference table vs enum. Current plan favors a reference table for flexibility.
- Social scope: defer table creation until ready, or scaffold early in a separate schema?

## References

- `database-optimization/db-plan.md` — detailed migration and ops plan.
- `database-optimization/db-plan-0.md` — concise schema spec (consistent with db-plan.md).
- Dumps: `tailor3_dump_…`, `freestyledb_plain_dump_…` — reference only for patterns.

---

Last updated: initial draft. This is a living document; we will evolve it as we finalize schema, apply seeds/migrations, and align the new Expo app with fs-core.

## fs-core Production Plan

### Goals
- Production-ready LOGGER now, with clean paths to SIES and PROXI without schema rewrites.
- Supabase-first: Auth integration, RLS, Storage, SQL-only deploys, and safe migrations.

### Target Schema Layout
- Schemas: `core` (catalog, users, logger), `guides` (size guides), `content` (media), `social` (future follows/likes/messages), `ops` (jobs/audit; optional).
- Core catalog:
  - `core.brands (id, name, slug unique, aliases[], metadata, created_at)`
  - `core.products (id, brand_id, product_code, name/title, category_id, subcategory_id, gender, raw, created_at, unique (brand_id, product_code))`
  - `core.product_variants (id, product_id, color_name, fit_name, color_name_norm gen, fit_name_norm gen, variant_sku, variant_url, attrs, unique (product_id, color_name_norm, fit_name_norm))`
  - `core.product_urls (product_id, variant_id?, region, url, is_current, created_at)` with resolver `core.resolve_product_by_url(text)` and `public.canonicalize_url(text)`
  - `core.product_images (variant_id, url, is_primary, position, metadata)` with partial unique index on `(variant_id) where is_primary`
- Logger:
  - `core.users (id, uuid, email, display_name, metadata)` + trigger to mirror `auth.users`
  - `core.user_garments (user_id, product_id?, brand_id?, size_label, product_url, owns_garment, garment_status, notes, raw, created_at)`
  - `core.user_fit_feedback (user_garment_id, dimension, feedback_code_id?, notes, created_at)` and `core.feedback_codes` ref
  - `content.media (user_id, user_garment_id?, kind, url, width/height/duration, variant, checksum, metadata, uploaded_at)`
- SIES:
  - `guides.measurement_sets (id, scope: size_guide|garment_spec, brand_id, category_id, gender?, fit_type?, unit, version, is_active, source_url, notes, timestamps)`
  - `guides.measurements (id, set_id, size_label, measurement_type, min_value, max_value, exact_value, unit, confidence, notes)`
  - `core.measurement_types` reference (dimension codes; body vs garment) for consistency
  - `core.user_measurements`, `core.measurement_estimates` (estimator outputs)
- PROXI:
  - `core.user_size_profiles (user_id unique, chest/sleeve/waist/neck, confidence, measurements jsonb, updated_at)`
  - `social.*` (follows, likes/saves, messages) — add when needed.

### Security & Auth
- Trigger: `public.handle_new_user()` inserts into `core.users` on `auth.users` insert.
- Enable RLS on: `core.users`, `core.user_garments`, `core.user_fit_feedback`, `content.media`.
- Policies use `auth.uid()` via `core.current_user_v (id, uuid)`:
  - Users: select/update self by uuid
  - Garments: CRUD when `user_id = current_user_v.id`
  - Feedback: enforce ownership via parent `user_garments`
  - Media: CRUD when `user_id = current_user_v.id`

### Indexing & Constraints
- Variants: generated normalized columns and unique composite key `(product_id, color_name_norm, fit_name_norm)`; indexes on product_id and normalized fields.
- Product URLs: index `(product_id, is_current)`, resolver uses canonicalized URL equality and a folder fallback.
- Images: partial unique index for one primary per variant.
- Guides: unique active selection for size guides and garment specs, e.g. unique (brand_id, category_id, coalesce(gender,''), coalesce(fit_type,''), coalesce(version,'')) where scope='size_guide' and is_active.
- Measurements: indexes on `(set_id)`, `(set_id, measurement_type, size_label)`, and search helpers by type/range.
- Logger: indexes on `user_garments(user_id)`, `(brand_id, size_label)`, `(created_at)`; feedback indices on `(user_garment_id)`.

### LOGGER Readiness Checklist
- [ ] Ensure `core.product_variants` exists with generated columns and unique composite key.
- [ ] Ensure `core.product_urls`, `public.canonicalize_url(text)`, `core.resolve_product_by_url(text)` are present.
- [ ] Ensure `core.product_images` exists and partial unique index `(variant_id) where is_primary` created.
- [ ] Confirm RLS policies are installed and `auth.users` trigger synced to `core.users`.
- [ ] Seed a real product end-to-end (J.Crew BE996): brand, product, canonical PDP URL, full color×fit variants, one primary image; verify `resolve_product_by_url` returns `(product_id, variant_id)`.

### SIES Build-out
- [ ] Create `guides.measurement_sets` and `guides.measurements` with indexes and unique active selectors.
- [ ] Add `core.measurement_types` and (optional) brand `measurement_mappings` and `measurement_instructions`.
- [ ] Add `core.user_measurements` and `core.measurement_estimates`; define minimal estimator write path.
- [ ] Seed at least one active size guide per brand/category in scope (e.g., J.Crew Shirts), then validate lookups by brand/category/fit/gender.

### PROXI Scaffolding
- [ ] Create `core.user_size_profiles` (simple numeric columns + JSONB map); backfill/maintain from estimates.
- [ ] Defer social tables (`social.follows/likes/messages`) until feature launch; predefine names and FK patterns.

### Operations & Quality
- Backups: nightly logical backups; keep migration files in version control; avoid ad-hoc DDL in production.
- Migrations: Supabase migrations/Alembic/Flyway; avoid `IF NOT EXISTS` on policies in Supabase v15 (use guarded DO $$ blocks).
- Environments: staging project mirrors production schema; run schema/seed in staging first.
- Observability: enable pg_stat_statements/pg_stat_monitor; track slow queries on variants/urls/resolver and logger writes.
- Validation suite:
  - Catalog: select counts, uniqueness checks for variants and URLs.
  - Resolver: golden URL set → expected (product_id, variant_id) pairs.
  - Logger: owner-only RLS tests for select/insert/update/delete.
  - Guides: active uniqueness and measurement numeric checks (`min <= max`), unit normalization.

### Rollout Sequence
1) LOGGER base (already live): users/brands/products/garments/feedback/media + RLS.
2) Variants/URLs pack + resolver + BE996 seed; verify end-to-end URL→variant→log.
3) SIES tables and minimal seeds; wire estimator outputs into `core.measurement_estimates` and optional `core.user_measurements`.
4) Profiles table for PROXI; background job to maintain profiles; add social schema when building discovery features.
5) Performance hardening as data grows: additional indexes; consider hash partitioning `core.user_garments` by `user_id` at high scale.

## Current Data Seed and Ingestion (J.Crew BE996)

- Source PDP: `https://www.jcrew.com/p/mens/categories/clothing/shirts/broken-in-oxford/broken-in-organic-cotton-oxford-shirt/BE996`
- Stored in core:
  - `core.products`: product_code=BE996, title “Broken-in organic cotton oxford shirt”, brand “J.Crew”
  - `core.product_urls`: canonical PDP URL; `core.resolve_product_by_url(text)` resolves URL → `(product_id, variant_id)`
  - `core.product_variants`: 105 variants (color × fit) seeded; normalized `color_name_norm`/`fit_name_norm` enforce uniqueness
  - `core.variant_sizes`: XS, S, M, L, XL, XXL for each variant (630 rows)
  - `core.product_images`: swatches and primary images with metadata; default primary set to “Ray White Multi” for all its fits

### Swatch and Primary Image Pipeline
- Scraper for approval (no DB writes): `scripts/jcrew_swatches_playwright.py`
  - Headless Chromium (Playwright) extracts swatches from `section#c-product__price-colors` (data-name + swatch `<img src>`)
  - Run:
    - `pip install playwright bs4 && playwright install chromium`
    - `python scripts/jcrew_swatches_playwright.py --url "<PDP_URL>" --json`
  - Output: list of `{ color, swatch_url }` for user approval in-app
- DB helpers (per approved item):
  - `core.add_color_swatch_image(product_id, color, swatch_url)`
    - Inserts a “swatch” image row for all variants of that color (metadata.kind=swatch; preserves display casing for app)
  - `core.add_variant_primary_image(product_id, color, fit, url)`
    - Sets/updates the primary image for that color+fit (metadata.kind=primary); used as the hero image
- Current default image: “Ray White Multi” marked with `metadata.default=true` on its primaries; serves as the default when color/fit not yet selected.

### App Flow (Dry Run for BE996)
- User pastes PDP URL → backend resolves via `core.resolve_product_by_url` to `product_id`.
- Screen shows:
  - Brand and title: J.Crew — “Broken-in organic cotton oxford shirt”
  - Default image: Ray White Multi primary image
  - Fit types: Classic, Slim, Slim Untucked, Tall, Relaxed
  - Colors: 19 options (e.g., Classic Blue Oxford, Ryan White Peri, Jarvis White Brown, …) with swatch thumbnails
  - Sizes: XS, S, M, L, XL, XXL
- User confirms color + fit + size, then answers fit questions (overall, chest, sleeve, length, etc.).
- Stored to LOGGER:
  - `core.user_garments` (user_id, product_id/variant_id, size_label, product_url, notes/raw)
  - `core.user_fit_feedback` (per-dimension feedback; standardized codes ready when we add the codes table)
  - `content.media` (optional photos/videos by user)

### What to Use Next for Additional J.Crew Shirts
- Use the same pipeline:
  1) Add/resolve product via `core.products` + `core.product_urls`.
  2) Create variants (`core.product_variants`), sizes (`core.variant_sizes`).
  3) Run `scripts/jcrew_swatches_playwright.py --url "<PDP>" --json`, approve in-app.
  4) Insert via `core.add_color_swatch_image` and `core.add_variant_primary_image`.
  5) Optionally set a default primary color by toggling `metadata.default=true` on that color’s primaries.


