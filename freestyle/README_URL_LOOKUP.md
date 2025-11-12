# Adding J.Crew Products to FreestyleDB with URL Lookup

This guide shows how to add J.Crew products to FreestyleDB and enable URL lookup like Tailor3.

## Overview

FreestyleDB has a normalized structure but lacks optimized URL lookup. This guide:
1. Shows how to add products to FreestyleDB's normalized structure
2. Adds URL lookup optimization (indexes + RPC function)
3. Makes URL lookup work like Tailor3

## Quick Start

### Step 1: Add URL Lookup Optimization

Run the migration to add indexes and RPC function:

```bash
psql -h your-host -U your-user -d your-database -f freestyle/migrations/add_url_lookup_optimization.sql
```

This adds:
- `pg_trgm` extension for fuzzy matching
- Direct URL index (`idx_product_url_url`)
- Trigram index (`idx_product_url_url_trgm`) for prefix matching
- `product_lookup()` RPC function (similar to Tailor3)

### Step 2: Add Your J.Crew Product

You have two options:

#### Option A: Manual SQL (Recommended for testing)

Edit `freestyle/migrations/add_jcrew_be996_example.sql` with your product details and run:

```bash
psql -h your-host -U your-user -d your-database -f freestyle/migrations/add_jcrew_be996_example.sql
```

#### Option B: Python Script (For bulk imports)

1. Update `FREESTYLEDB_CONFIG` in `scripts/add_jcrew_to_freestyledb.py` with your database credentials
2. Run the script:

```bash
python scripts/add_jcrew_to_freestyledb.py
```

### Step 3: Test URL Lookup

After adding products, test the lookup:

```sql
-- Test exact URL match
SELECT * FROM product_lookup('https://www.jcrew.com/p/mens/categories/clothing/shirts/broken-in-oxford/broken-in-organic-cotton-oxford-shirt/BE996');

-- Test with query params (should still work)
SELECT * FROM product_lookup('https://www.jcrew.com/p/mens/categories/clothing/shirts/broken-in-oxford/broken-in-organic-cotton-oxford-shirt/BE996?colorProductCode=CC100');

-- Test with trailing slash
SELECT * FROM product_lookup('https://www.jcrew.com/p/mens/categories/clothing/shirts/broken-in-oxford/broken-in-organic-cotton-oxford-shirt/BE996/');
```

## How It Works

### FreestyleDB Structure

FreestyleDB uses a normalized structure:
- `brand` → `style` → `variant` → `product_url`
- Each level normalized (colors, fits, fabrics in separate tables)

### URL Lookup Strategy

The `product_lookup()` function uses a multi-tier strategy (like Tailor3):

1. **Exact match**: Tries exact URL match (fastest)
2. **Prefix match**: Uses trigram index for URL variations
3. **Style code match**: Extracts product code from URL and matches style_code

### Example: Adding BE996

For the J.Crew BE996 shirt:

1. **Brand**: J.Crew (already exists or create it)
2. **Category**: Shirts (already exists or create it)
3. **Style**: "Broken-in organic cotton oxford shirt"
   - Links to brand and category
   - Has gender = 'Men'
4. **Style Code**: BE996
   - Stores in `style_code` table
   - Links to style
5. **Variant**: Default variant (or create variants for each color)
   - Links to style
   - Can link to color, fit, fabric
6. **Product URL**: The full URL
   - Links to both style and variant
   - Has `is_current = true` flag
7. **Price**: Optional price history entry

## Adding Multiple Variants

For products with multiple colors/fits, create multiple variants:

```sql
-- For each color, create a variant
INSERT INTO variant (style_id, color_id, fit_id, is_active)
VALUES (
    (SELECT id FROM style WHERE name = 'Broken-in organic cotton oxford shirt'),
    (SELECT id FROM color_catalog WHERE canonical = 'White'),
    (SELECT id FROM fit_catalog WHERE name = 'Classic'),
    true
);

-- Add URL for this variant
INSERT INTO product_url (style_id, variant_id, region, url, is_current)
VALUES (
    (SELECT id FROM style WHERE name = 'Broken-in organic cotton oxford shirt'),
    (SELECT id FROM variant WHERE ...), -- variant you just created
    'US',
    'https://www.jcrew.com/p/.../BE996?colorProductCode=CC100',
    true
);
```

## Comparison with Tailor3

### Tailor3 Approach
- Denormalized structure
- URLs directly in `product_variants.variant_url`
- Direct indexes on URL columns
- `product_lookup()` RPC function

### FreestyleDB Approach (After This Migration)
- Normalized structure (better for scaling)
- URLs in separate `product_url` table
- Same indexes + RPC function
- **Same URL lookup performance** ✅

## Troubleshooting

### URL lookup returns no results
1. Check if product_url exists: `SELECT * FROM product_url WHERE url LIKE '%BE996%';`
2. Check if `is_current = true`: `SELECT * FROM product_url WHERE url = 'your-url' AND is_current = true;`
3. Check indexes: `\d product_url` (should show `idx_product_url_url` and `idx_product_url_url_trgm`)

### Slow queries
1. Make sure indexes exist: `SELECT * FROM pg_indexes WHERE tablename = 'product_url';`
2. Run `ANALYZE product_url;` to update statistics
3. Check query plan: `EXPLAIN ANALYZE SELECT * FROM product_lookup('your-url');`

### Duplicate products
- The `product_lookup()` function returns up to 50 results
- If you have multiple variants with similar URLs, they'll all be returned
- Filter by `variant_id` if you need a specific variant

## Next Steps

1. **Add more products**: Use the Python script or SQL template
2. **Bulk import**: Modify the script to scrape and import multiple products
3. **Add variants**: Create variants for all colors/fits of each product
4. **Update prices**: Add price_history entries when prices change
5. **Add images**: Use `media_asset` table to store product images

## Files Created

- `scripts/add_jcrew_to_freestyledb.py` - Python script to add products
- `freestyle/migrations/add_url_lookup_optimization.sql` - SQL migration for URL lookup
- `freestyle/migrations/add_jcrew_be996_example.sql` - Example SQL for adding BE996
- `freestyle/README_URL_LOOKUP.md` - This file

## Summary

You can now:
✅ Add products to FreestyleDB's normalized structure
✅ Look up products by URL (just like Tailor3)
✅ Get the benefits of both: normalized structure + fast URL lookup

The key is adding the indexes and RPC function, which make FreestyleDB's URL lookup just as fast as Tailor3's!





