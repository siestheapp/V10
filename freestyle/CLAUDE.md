# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Freestyle is a fashion product catalog and size twin recommendation platform consisting of:
- **FreestyleDB**: PostgreSQL database on Supabase containing product catalog (brands, styles, variants, prices, images)
- **Mobile app**: Expo/React Native app for discovering "size twins" (users who own same items in same size)
- **Ingestion pipeline**: Playwright-based web scrapers for product data ingestion
- **Autocrop pipeline**: Image processing for product hero images
- **Static mockups**: HTML/CSS prototypes for design validation

## Architecture

### Database Structure (Supabase PostgreSQL)

**Connection Details:**
- Host: `db.ymncgfobqwhkekbydyjx.supabase.co:6543`
- Database: `postgres`
- Connection string stored in: `DATABASE_CONNECTION_GUIDE.md`

**Schema Organization:**
- `public.*` - Production catalog (21 tables: brand, category, style, variant, product_url, product_image, price_history, etc.)
- `demo.*` - Safe sandbox for demo app (mirrors public structure + user tables)
- `auth.*` - Supabase authentication (managed)
- `storage.*` - Supabase storage (managed)

**Entity Hierarchy:**
```
brand → category → style → variant
                      ↓
         [product_url, product_image, price_history, variant_code]
```

**Key Tables:**
- `brand` - Brand/retailer information
- `category` - Product categories (shirts, pants, dresses)
- `style` - Base product (unique per brand+name+category)
- `variant` - Color/fabric/fit variations of a style
- `color_catalog`, `fabric_catalog`, `fit_catalog` - Normalized attributes
- `product_image` - Product photos
- `product_url` - Retailer URLs
- `price_history` - Time-series price tracking
- `ingestion_job`, `ingestion_task` - Ingestion queue and tracking

### Mobile App (`/mobile`)

**Tech Stack:**
- Expo SDK ~51.0.0 (managed workflow)
- React Native 0.74.5
- TypeScript
- Expo Router (file-based routing)
- Supabase client for data access

**App Structure:**
- `app/(tabs)/home` - Feed showing size twins
- `app/add-item` - Add product URL
- `app/confirm-item` - Confirm product and select size
- `app/auth/signin` - Demo authentication (Google OAuth setup in progress)
- `src/` - Shared utilities and API calls
- `features/` - Feature-specific components
- `components/` - Reusable UI components
- `theme/` - Design tokens and theme config

**Data Flow:**
1. User pastes product URL → `demo.api_resolve_by_url(p_url)` RPC
2. Returns variant details from `public.*` catalog
3. User selects size → `demo.api_claim(p_user_id, p_variant_id, p_size_label, p_url)` RPC
4. Writes to `demo.user_owned_variant`
5. Feed queries `demo.api_feed(p_user_id)` → returns proxy cards via `demo.v_proxy_feed` view

**Important:** Mobile app only writes to `demo.*` schema (safe sandbox). Production catalog is read-only.

### Ingestion Pipeline (`/ingest/playwright`)

**Purpose:** Scrape fashion brand websites to populate product catalog

**Tech Stack:**
- Playwright (Chromium automation)
- TypeScript
- Node.js pg client
- Zod for validation

**Architecture:**
1. `init-job` - Creates ingestion job for brand/category URL
2. `seed-tasks` - Crawls category page, extracts PDP URLs, creates tasks
3. `run-worker` - Processes tasks (scrape PDP → parse → upsert to DB)

**Adapter Pattern:**
- `src/adapters/reformation.ts` - Brand-specific scraping logic
- Handles cookie acceptance, infinite scroll, PDP parsing
- Extracts: name, description, colors, sizes, prices, images

**Database Integration:**
- `src/db/upsert.ts` - Implements PRODUCT_INGESTION_GUIDE.md workflow
- Resolves/creates: brand → category → catalogs → style → variant
- Upserts: images, URLs, prices, variant codes
- Uses transactions for atomicity

**Current Status (per INGESTION_STATUS.md):**
- Crawler validated (65 PDPs found for Reformation dresses)
- TLS workaround needed: `NODE_TLS_REJECT_UNAUTHORIZED=0`
- Task seeding issue: inserts not persisting (debugging in progress)

### Autocrop Pipeline (`/scripts`)

**Purpose:** Convert uploaded photos into hero-ready crops for product cards

**Features:**
- Drag-and-drop workflow (file-based or web UI)
- Smart cropping with attention detection (Sharp) or SmartCrop
- Outputs 2:3 portrait ratios at 1x/2x/3x densities (354×520 base)
- Formats: WebP and JPG

**Directories:**
- `_autocrop/in/` - Drop images here
- `_autocrop/out/` - Processed crops
- `_autocrop/archive/` - Originals after processing

**Config:** `scripts/autocrop.config.json`

## Common Commands

### Database Access

**Read-only queries (MCP in Cursor):**
```
/db list tables
/db describe table <table_name>
```

**Write operations (psql):**
```bash
psql "postgres://postgres:efvTower1211@db.ymncgfobqwhkekbydyjx.supabase.co:6543/postgres" -c "YOUR_SQL_HERE"
```

**Important:** MCP is read-only. Use psql for schema changes, inserts, or migrations.

### Mobile App

**Install dependencies:**
```bash
cd mobile
npm install
```

**Run development builds:**
```bash
npm run ios          # iOS simulator
npm run android      # Android emulator
npm run web          # Web browser (testing only)
npm start            # Expo dev server (choose platform)
npm run start:clear  # Clear cache and start
```

**Environment setup:**
- Copy `mobile/.env` and add `EXPO_PUBLIC_SUPABASE_ANON_KEY`
- See `mobile/DEMO_SETUP.md` for detailed instructions

### Ingestion Pipeline

**Install dependencies:**
```bash
cd ingest/playwright
npm install
npm run pw-install  # Install Chromium
```

**Run ingestion:**
```bash
# 1. Create job
NODE_TLS_REJECT_UNAUTHORIZED=0 npm run init-job -- --category "https://www.thereformation.com/dresses" --brand "Reformation"

# 2. Seed tasks (crawl category page)
NODE_TLS_REJECT_UNAUTHORIZED=0 npm run seed-tasks -- --job <job_id>

# 3. Run worker (process tasks)
NODE_TLS_REJECT_UNAUTHORIZED=0 npm run run-worker -- --job <job_id> --concurrency 1

# Debug crawler only (no DB writes)
npx ts-node scripts/debug-crawl.ts <category_url>
```

**Preflight check:**
```bash
npm run preflight  # Verify DB connection and schema
```

### Autocrop Pipeline

**File-based workflow:**
```bash
npm install
npm run autocrop:watch   # Watch mode: drag files to _autocrop/in
npm run autocrop         # Process existing files once
npm run autocrop:clean   # Clean output directory
```

**Web UI workflow:**
```bash
npm run autocrop:web
# Open http://localhost:5173
# Drag images into browser
```

### Development Utilities

**Kill ports (if dev servers conflict):**
```bash
./kill-ports.sh
```

## Important Patterns

### Product Ingestion Workflow

Follow the exact order in `PRODUCT_INGESTION_GUIDE.md`:
1. Resolve/create brand
2. Resolve/create category
3. Resolve/create catalog entries (color, fabric, fit)
4. Resolve/create style (check uniqueness: brand_id + name + category_id)
5. Resolve/create variant (check uniqueness: style_id + color_id + fit_id + fabric_id)
6. Upsert product images (ON CONFLICT on style_id + variant_id + url)
7. Upsert product URLs (ON CONFLICT on url)
8. Insert price history (time-series data)
9. Insert variant codes (SKUs, UPCs)

**Key Principles:**
- **Idempotency**: Safe to re-run (use ON CONFLICT)
- **Atomicity**: Wrap in transactions
- **Normalization**: Reuse existing catalog entries
- **Traceability**: Log ingestion runs

### Database Queries

**Find variant by URL:**
```sql
SELECT variant_id FROM public.product_url
WHERE url = 'https://...' AND is_current = true
LIMIT 1;
```

**Get product details:**
```sql
SELECT s.name, b.name as brand, c.canonical as color
FROM variant v
JOIN style s ON v.style_id = s.id
JOIN brand b ON s.brand_id = b.id
LEFT JOIN color_catalog c ON v.color_id = c.id
WHERE v.id = <variant_id>;
```

**Latest price:**
```sql
SELECT list_price, sale_price, captured_at
FROM price_history
WHERE variant_id = <variant_id> AND region = 'US'
ORDER BY captured_at DESC
LIMIT 1;
```

### Mobile App RPC Calls

**Sign up demo user:**
```typescript
const { data } = await supabase.rpc('api_signup', {
  p_username: 'user123'
});
```

**Resolve product URL:**
```typescript
const { data } = await supabase.rpc('api_resolve_by_url', {
  p_url: 'https://...'
});
```

**Claim ownership:**
```typescript
const { data } = await supabase.rpc('api_claim', {
  p_user_id: userId,
  p_variant_id: variantId,
  p_size_label: 'S',
  p_url: 'https://...'
});
```

**Get feed:**
```typescript
const { data } = await supabase.rpc('api_feed', {
  p_user_id: userId
});
```

### Design Tokens

Design system tokens are in `freestyle-tokens.css` and `freestyle-tokens.json`:
- Colors: Champagne (#F8F9FA), Black Bean (#0B0F14), Mineral (#B8C5D0)
- Typography: Source Serif 4 (serif), Inter (sans)
- Spacing: 4px base unit

See `design-system/` for comprehensive guidance.

## Testing & Debugging

### Verify Database Connection

```bash
# From any directory with .env
npx dotenv -e .env -- sh -c 'psql "$DATABASE_URL" -c "SELECT current_database(), current_user;"'
```

### Check Tables

```bash
psql "<connection_string>" -c "\dt public.*"
psql "<connection_string>" -c "\dt demo.*"
```

### Mobile App Testing

1. Create 2+ demo users (different devices/sessions)
2. Both add same product with same size
3. Verify both see each other in feed
4. Pull to refresh to update

### Debug Ingestion

**Check job status:**
```sql
SELECT * FROM public.ingestion_job ORDER BY created_at DESC LIMIT 5;
```

**Check tasks:**
```sql
SELECT status, COUNT(*) FROM public.ingestion_task
WHERE job_id = <id> GROUP BY status;
```

**View recent inserts:**
```sql
SELECT s.name, b.name as brand, v.id as variant_id, v.created_at
FROM variant v
JOIN style s ON v.style_id = s.id
JOIN brand b ON s.brand_id = b.id
ORDER BY v.created_at DESC LIMIT 10;
```

## Known Issues

### Ingestion TLS Issue
- **Problem:** Node.js pg client requires TLS cert override
- **Workaround:** `NODE_TLS_REJECT_UNAUTHORIZED=0` prefix
- **Permanent fix:** Install CA certs: `brew install ca-certificates` + set `NODE_EXTRA_CA_CERTS`

### Task Seeding Issue
- **Problem:** `ingestion_task` inserts not persisting despite no errors
- **Debug steps:** Check RLS policies, verify DATABASE_URL at runtime, add insert diagnostics
- **Workaround:** Consider file-based seeding (newline-delimited PDP URLs)

### Mobile App Environment Variables
- **Problem:** Missing Supabase anon key
- **Fix:** Create `mobile/.env` with `EXPO_PUBLIC_SUPABASE_ANON_KEY`
- **Note:** Restart Expo dev server after changing `.env`

## File Structure

```
/
├── mobile/                    # Expo/React Native app
│   ├── app/                   # Expo Router pages
│   ├── src/                   # API utilities
│   ├── components/            # UI components
│   ├── features/              # Feature modules
│   ├── theme/                 # Design tokens
│   └── DEMO_SETUP.md          # Setup guide
├── ingest/playwright/         # Product ingestion pipeline
│   ├── src/                   # TypeScript source
│   │   ├── adapters/          # Brand scrapers
│   │   ├── db/                # Database utilities
│   │   ├── jobs/              # Job management
│   │   └── index.ts           # CLI entry point
│   ├── scripts/               # Utility scripts
│   └── sql/                   # Migrations
├── scripts/                   # Autocrop and utilities
│   ├── autocrop.js            # File-based autocrop
│   ├── autocrop-server.js     # Web UI autocrop
│   └── autocrop.config.json   # Crop config
├── _autocrop/                 # Autocrop I/O directories
│   ├── in/                    # Input images
│   ├── out/                   # Processed crops
│   └── archive/               # Originals
├── design-system/             # Design tokens and docs
├── freestyle-october/         # Static HTML mockups
├── archive/                   # Legacy mockups
├── DATABASE_CONNECTION_GUIDE.md
├── PRODUCT_INGESTION_GUIDE.md
└── FUTURE_DATA_STAGING.md     # Structured data for future use
```

## Key Documentation Files

- `DATABASE_CONNECTION_GUIDE.md` - How to connect to Supabase (MCP vs psql)
- `PRODUCT_INGESTION_GUIDE.md` - Complete ingestion workflow (step-by-step SQL)
- `mobile/DEMO_SETUP.md` - Mobile app setup and testing
- `mobile/GOOGLE_OAUTH_SETUP.md` - OAuth configuration
- `ingest/playwright/INGESTION_STATUS.md` - Current pipeline status and issues
- `FUTURE_DATA_STAGING.md` - Extracted data not yet in schema (size guides, care instructions)
- `design-system/Freestyle_Design_System_Unified.md` - Design system overview
