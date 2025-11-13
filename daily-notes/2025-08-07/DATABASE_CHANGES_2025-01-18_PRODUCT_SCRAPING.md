# Database Changes - January 18, 2025: Product Scraping Infrastructure

## Overview
Added comprehensive product scraping infrastructure to tailor3 database to support automated product data collection from e-commerce websites like Banana Republic, while maintaining full compatibility with existing manual product curation system.

## Date & Time
- **Date**: January 18, 2025
- **Applied**: ~2:30 PM EST
- **Database**: tailor3 (Supabase PostgreSQL)
- **Applied By**: Automated via terminal commands

---

## 1. Extended Existing Tables

### Products Table Extensions
Extended `public.products` table with 10 new columns to support scraped product data:

```sql
-- New columns added to public.products
ALTER TABLE public.products ADD COLUMN IF NOT EXISTS external_id VARCHAR(100);
ALTER TABLE public.products ADD COLUMN IF NOT EXISTS source_type VARCHAR(20) DEFAULT 'manual';
ALTER TABLE public.products ADD COLUMN IF NOT EXISTS original_price NUMERIC(10,2);
ALTER TABLE public.products ADD COLUMN IF NOT EXISTS discount_percentage INTEGER;
ALTER TABLE public.products ADD COLUMN IF NOT EXISTS sizes_available JSONB;
ALTER TABLE public.products ADD COLUMN IF NOT EXISTS colors_available JSONB;
ALTER TABLE public.products ADD COLUMN IF NOT EXISTS material VARCHAR(255);
ALTER TABLE public.products ADD COLUMN IF NOT EXISTS fit_type VARCHAR(100);
ALTER TABLE public.products ADD COLUMN IF NOT EXISTS last_scraped TIMESTAMP;
ALTER TABLE public.products ADD COLUMN IF NOT EXISTS scraping_metadata JSONB;
```

#### Column Descriptions
| Column | Type | Purpose | Default |
|--------|------|---------|---------|
| `external_id` | VARCHAR(100) | Product ID from source website | NULL |
| `source_type` | VARCHAR(20) | Distinguishes manual vs scraped products | 'manual' |
| `original_price` | NUMERIC(10,2) | Price before discounts | NULL |
| `discount_percentage` | INTEGER | Discount percentage if on sale | NULL |
| `sizes_available` | JSONB | Array of available sizes | NULL |
| `colors_available` | JSONB | Array of available colors/variants | NULL |
| `material` | VARCHAR(255) | Fabric/material composition | NULL |
| `fit_type` | VARCHAR(100) | Fit style (slim, regular, relaxed, etc.) | NULL |
| `last_scraped` | TIMESTAMP | When product was last scraped | NULL |
| `scraping_metadata` | JSONB | Raw scraping data for debugging | NULL |

### Constraints Added
```sql
-- Prevent duplicate products from same brand
ALTER TABLE public.products ADD CONSTRAINT unique_brand_external_id 
    UNIQUE(brand_id, external_id) DEFERRABLE INITIALLY DEFERRED;
```

---

## 2. New Schema: product_catalog

Created dedicated schema for scraping infrastructure to separate concerns while maintaining integration.

```sql
CREATE SCHEMA IF NOT EXISTS product_catalog;
```

---

## 3. New Tables

### 3.1 scraping_runs
Tracks performance and metadata for each scraping operation.

```sql
CREATE TABLE product_catalog.scraping_runs (
    id SERIAL PRIMARY KEY,
    brand_id INTEGER REFERENCES public.brands(id),
    category_id INTEGER REFERENCES public.categories(id),
    target_url TEXT NOT NULL,
    products_found INTEGER DEFAULT 0,
    products_updated INTEGER DEFAULT 0,
    products_added INTEGER DEFAULT 0,
    errors_count INTEGER DEFAULT 0,
    run_duration_seconds INTEGER,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'running',
    error_details JSONB,
    scraper_version VARCHAR(50)
);
```

**Purpose**: Monitor scraping performance, track success rates, identify issues.

### 3.2 scraper_configs
Stores brand-specific scraping configurations and CSS selectors.

```sql
CREATE TABLE product_catalog.scraper_configs (
    id SERIAL PRIMARY KEY,
    brand_id INTEGER REFERENCES public.brands(id),
    category_id INTEGER REFERENCES public.categories(id),
    base_url TEXT NOT NULL,
    selectors JSONB NOT NULL,
    pagination_config JSONB,
    rate_limit_ms INTEGER DEFAULT 1000,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose**: Configure scrapers for different brands/categories, store CSS selectors, manage rate limiting.

### 3.3 product_scraping_log
Detailed logging for individual product scraping attempts.

```sql
CREATE TABLE product_catalog.product_scraping_log (
    id SERIAL PRIMARY KEY,
    scraping_run_id INTEGER REFERENCES product_catalog.scraping_runs(id),
    product_id INTEGER REFERENCES public.products(id),
    external_id VARCHAR(100),
    product_url TEXT,
    action_type VARCHAR(20),
    error_message TEXT,
    scraped_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose**: Debug individual product issues, track what data was scraped, audit trail.

---

## 4. Performance Indexes

Added 6 new indexes for optimal query performance:

```sql
CREATE INDEX IF NOT EXISTS idx_scraping_runs_brand_category ON product_catalog.scraping_runs(brand_id, category_id);
CREATE INDEX IF NOT EXISTS idx_scraping_runs_status ON product_catalog.scraping_runs(status);
CREATE INDEX IF NOT EXISTS idx_product_scraping_log_run ON product_catalog.product_scraping_log(scraping_run_id);
CREATE INDEX IF NOT EXISTS idx_products_external_id ON public.products(external_id);
CREATE INDEX IF NOT EXISTS idx_products_source_type ON public.products(source_type);
CREATE INDEX IF NOT EXISTS idx_products_last_scraped ON public.products(last_scraped);
```

---

## 5. Integration with Existing System

### Backward Compatibility
- **100% backward compatible**: All existing functionality unchanged
- **Existing products**: Automatically have `source_type = 'manual'`
- **Existing queries**: Continue to work without modification

### Forward Integration
- **Fit analysis**: Works immediately with scraped products
- **Size guides**: Can link scraped products using existing `brand_id`
- **User feedback**: Users can rate scraped products same as manual ones
- **Recommendations**: Scraped products feed into existing recommendation engine

### Data Flow
```
Scraper → public.products (source_type='scraped') → Existing Fit Analysis → User Recommendations
```

---

## 6. Usage Examples

### Query All Scraped Products
```sql
SELECT 
    p.name,
    b.name as brand,
    p.price,
    p.original_price,
    p.discount_percentage,
    p.sizes_available,
    p.last_scraped
FROM public.products p
JOIN public.brands b ON p.brand_id = b.id
WHERE p.source_type = 'scraped'
ORDER BY p.last_scraped DESC;
```

### Check Scraping Performance
```sql
SELECT 
    b.name as brand,
    c.name as category,
    sr.products_found,
    sr.products_added,
    sr.run_duration_seconds,
    sr.started_at
FROM product_catalog.scraping_runs sr
JOIN public.brands b ON sr.brand_id = b.id
JOIN public.categories c ON sr.category_id = c.id
ORDER BY sr.started_at DESC;
```

### Find Products Needing Updates
```sql
SELECT 
    p.name,
    b.name as brand,
    p.last_scraped,
    EXTRACT(days FROM NOW() - p.last_scraped) as days_since_update
FROM public.products p
JOIN public.brands b ON p.brand_id = b.id
WHERE p.source_type = 'scraped'
  AND p.last_scraped < NOW() - INTERVAL '7 days'
ORDER BY p.last_scraped ASC;
```

---

## 7. Next Steps

### Immediate (Today)
1. ✅ Database schema complete
2. 🔄 Build Banana Republic scraper
3. 🔄 Test with sample products
4. 🔄 Validate integration with existing fit analysis

### Short Term (This Week)
- Create scraper configurations for Banana Republic
- Implement rate limiting and error handling
- Add data validation and quality checks
- Create monitoring dashboard

### Medium Term (Next 2 Weeks)
- Extend to additional brands (J.Crew, etc.)
- Add automated scheduling (daily/weekly scraping)
- Implement product change detection
- Add price tracking and alerts

---

## 8. Rollback Plan

If needed, changes can be rolled back with:

```sql
-- Remove new columns (WARNING: Data loss)
ALTER TABLE public.products DROP COLUMN IF EXISTS external_id;
ALTER TABLE public.products DROP COLUMN IF EXISTS source_type;
ALTER TABLE public.products DROP COLUMN IF EXISTS original_price;
ALTER TABLE public.products DROP COLUMN IF EXISTS discount_percentage;
ALTER TABLE public.products DROP COLUMN IF EXISTS sizes_available;
ALTER TABLE public.products DROP COLUMN IF EXISTS colors_available;
ALTER TABLE public.products DROP COLUMN IF EXISTS material;
ALTER TABLE public.products DROP COLUMN IF EXISTS fit_type;
ALTER TABLE public.products DROP COLUMN IF EXISTS last_scraped;
ALTER TABLE public.products DROP COLUMN IF EXISTS scraping_metadata;

-- Remove constraint
ALTER TABLE public.products DROP CONSTRAINT IF EXISTS unique_brand_external_id;

-- Remove schema (WARNING: All scraping data lost)
DROP SCHEMA IF EXISTS product_catalog CASCADE;
```

---

## 9. Technical Notes

### Database Version
- PostgreSQL 15.8 on Supabase
- Applied via direct psql commands
- All changes committed successfully

### Performance Impact
- Minimal impact on existing queries
- New indexes improve scraping-related queries
- JSONB columns use efficient storage

### Security Considerations
- Scraping metadata stored in JSONB for flexibility
- Rate limiting built into configuration
- External IDs prevent duplicate products
- Audit trail maintained in scraping logs

---

## 10. Files Modified/Created

### Database Changes
- Extended `public.products` table
- Created `product_catalog` schema
- Added 3 new tables
- Added 6 performance indexes
- Added 1 unique constraint

### Documentation
- This file: `database/DATABASE_CHANGES_2025-01-18_PRODUCT_SCRAPING.md`

---

**Change Summary**: Successfully extended tailor3 database with comprehensive product scraping infrastructure while maintaining 100% backward compatibility with existing manual product curation system. Ready for automated product data collection from major e-commerce brands.
