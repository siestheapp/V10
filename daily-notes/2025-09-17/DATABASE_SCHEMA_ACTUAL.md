# V10 Database Schema - ACTUAL STATE
> **Generated**: 2025-09-17  
> **Database**: PostgreSQL (Supabase)  
> **Total Tables**: 45 tables + 25 views  
> **Connection**: Use `DB_CONFIG` from `db_config.py`

## ⚠️ CRITICAL: Documentation Issues

**DATABASE_SCHEMA_COMPLETE.md is OUTDATED** - It contains incorrect schemas for many tables, especially:
- `user_garments` - completely different columns
- `user_garment_feedback` - completely different structure
- References deprecated `size_guides` instead of `measurement_sets`

## 🎯 CURRENT vs DEPRECATED Systems

### Size Guide System
- **❌ OLD/DEPRECATED**: `size_guides` + `size_guide_entries` (still has data but being phased out)
- **✅ CURRENT**: `measurement_sets` + `measurements` (active system)

### Feedback System  
- **✅ CURRENT**: `user_garment_feedback` with `dimension` and `feedback_code_id`
- **❌ WRONG DOCS**: Documentation incorrectly shows columns like `feedback_type`, `rating`, etc.

---

## 📊 ACTIVE TABLES (Currently Used)

### 1. Core Product Tables

#### `brands` (11 rows)
```sql
id                    INTEGER (PK)
name                  TEXT NOT NULL        -- Use 'name' not 'brand_name'!
region                TEXT
default_unit          TEXT DEFAULT 'in'
original_measurement_unit TEXT
-- metadata columns
```
**Key brands**: J.Crew=1, Reiss=10, Banana Republic=5, Theory=9

#### `product_master` (57 rows)
```sql
id                    INTEGER (PK)
brand_id              INTEGER -> brands.id
product_code          VARCHAR(50) NOT NULL  -- e.g., 'BE996', 'CM389'
base_name             TEXT NOT NULL         -- Use 'base_name' not 'product_name'!
materials             JSONB
care_instructions     TEXT[]
fit_information       JSONB
category_id           INTEGER -> categories.id
subcategory_id        INTEGER -> subcategories.id
created_at            TIMESTAMP
last_scraped          TIMESTAMP
-- plus other metadata
```

#### `product_variants` (275 rows)
```sql
id                    INTEGER (PK)         -- Use 'id' not 'variant_id'!
product_master_id     INTEGER -> product_master.id
brand_id              INTEGER -> brands.id
sku                   VARCHAR(100)
color_name            VARCHAR(100)         -- Use 'color_name' not 'color'!
color_code            VARCHAR(50)
fit_option            VARCHAR(50)          -- Use 'fit_option' not 'fit_type'!
current_price         NUMERIC(10,2)        -- Use 'current_price' not 'price'!
sizes_available       TEXT[]               -- Array of sizes
in_stock              BOOLEAN DEFAULT true
variant_url           TEXT
-- plus other fields
```

### 2. User & Garment Tables

#### `user_garments` (31 rows) - ACTUAL SCHEMA
```sql
id                    INTEGER (PK)
user_id               INTEGER -> users.id
size_label            TEXT NOT NULL        -- NOT 'size_purchased'!
product_master_id     INTEGER -> product_master.id
product_variant_id    INTEGER -> product_variants.id
fit_feedback          TEXT                 -- Overall fit assessment
garment_status        VARCHAR(50) DEFAULT 'owned'
color                 VARCHAR(100)
link_provided         TEXT
input_method          TEXT
-- Legacy columns (being phased out):
size_guide_id         INTEGER -> size_guides.id
size_guide_entry_id   INTEGER -> size_guide_entries.id
garment_id            INTEGER -> garments.id
measurement_set_id    INTEGER -> measurement_sets.id
-- metadata columns
```
**❌ DOES NOT HAVE**: `brand_id`, `product_code`, `garment_name`, `category`, `size_purchased`

#### `user_garment_feedback` (89 rows) - ACTUAL SCHEMA
```sql
id                    INTEGER (PK)
user_garment_id       INTEGER -> user_garments.id
dimension             TEXT NOT NULL        -- 'chest', 'neck', 'sleeve', etc.
feedback_code_id      INTEGER -> feedback_codes.id
measurement_source    TEXT DEFAULT 'size_guide'
measurement_id        INTEGER
created_at            TIMESTAMP
created_by            INTEGER -> admins.id
```
**❌ DOES NOT HAVE**: `feedback_type`, `fit_assessment`, `rating`, `notes`, `overall_fit`, `comfort_rating`

### 3. Current Measurement System

#### `measurement_sets` (14 rows) - CURRENT SIZE GUIDE SYSTEM
```sql
id                    BIGINT (PK)
brand_id              BIGINT -> brands.id
category_id           BIGINT -> categories.id
scope                 TEXT NOT NULL        -- 'size_guide' or 'garment_spec'
fit_type              TEXT DEFAULT 'Regular'
gender                TEXT
unit                  TEXT DEFAULT 'in'
source                TEXT
is_active             BOOLEAN DEFAULT true
-- metadata columns
```

#### `measurements` (277 rows) - ACTUAL MEASUREMENT DATA
```sql
id                    INTEGER (PK)
set_id                BIGINT -> measurement_sets.id  -- Links to measurement_sets!
brand_id              INTEGER -> brands.id
size_label            TEXT NOT NULL        -- 'S', 'M', 'L', etc.
measurement_type      TEXT NOT NULL        -- 'body_chest', 'garment_chest_width', etc.
measurement_category  TEXT (generated)     -- 'body' or 'garment'
exact_value           NUMERIC
min_value             NUMERIC
max_value             NUMERIC
midpoint_value        NUMERIC (generated)
range_text            TEXT (generated)
unit                  TEXT DEFAULT 'in'
confidence_score      DOUBLE PRECISION
-- metadata columns
```

### 4. Supporting Tables

#### `feedback_codes` (13 rows)
```sql
id                    INTEGER (PK)
description           TEXT                 -- 'Too Tight', 'Too Loose', etc.
```

#### `categories` (4 rows)
```sql
id                    INTEGER (PK)
name                  TEXT
```

#### `subcategories` (6 rows)
```sql
id                    INTEGER (PK)
category_id           INTEGER -> categories.id
name                  TEXT
```

---

## 🚫 DEPRECATED TABLES (Do Not Use)

### Explicitly Deprecated
- `jcrew_backup_20250916_134019` - Backup table
- `jcrew_test_results` - Test table (empty)
- `size_guides_v2` - Old version (is a VIEW)

### Legacy Size Guide System (Being Phased Out)
- `size_guides` (10 rows) - OLD SYSTEM, use `measurement_sets`
- `size_guide_entries` (67 rows) - OLD SYSTEM, use `measurements`

### Empty/Unused Tables
- `body_measurements` (0 rows)
- `brand_product_cache` (0 rows)
- `dimension_feedback_sequence` (0 rows)
- `try_on_items` (0 rows)
- `try_on_sessions` (0 rows)
- `user_preferences` (0 rows)

---

## 👁️ VIEWS (25 total - Computed, not physical tables)

These are read-only computed views:
- `user_garments_full` - Joins user_garments with related data
- `product_catalog` - Product listing view
- `measurements_simple` - Simplified measurements
- `feedback_complete` - Complete feedback with joins
- `size_guides_v2` - VIEW not a table!
- Plus 20 others...

---

## ✅ CORRECT QUERY PATTERNS

### Get User's Fit Feedback
```sql
-- CORRECT - uses actual schema
SELECT 
    ugf.dimension,
    ugf.feedback_code_id,
    fc.description as feedback_text,
    ug.fit_feedback as overall_fit,  -- From user_garments
    ug.size_label                    -- NOT size_purchased
FROM user_garment_feedback ugf
JOIN user_garments ug ON ugf.user_garment_id = ug.id
LEFT JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
```

### Get Product Information
```sql
-- CORRECT - proper joins and column names
SELECT 
    pm.base_name,            -- NOT product_name
    pm.product_code,
    b.name as brand_name,    -- NOT b.brand_name
    pv.color_name,           -- NOT color
    pv.fit_option,          -- NOT fit_type
    pv.current_price        -- NOT price
FROM user_garments ug
LEFT JOIN product_master pm ON ug.product_master_id = pm.id
LEFT JOIN product_variants pv ON ug.product_variant_id = pv.id
LEFT JOIN brands b ON pm.brand_id = b.id
```

### Get Size Guide Data (Current System)
```sql
-- CORRECT - uses measurement_sets + measurements
SELECT 
    m.size_label,
    m.measurement_type,
    m.exact_value,
    m.unit
FROM measurements m
JOIN measurement_sets ms ON m.set_id = ms.id
WHERE m.brand_id = 10  -- Reiss
```

---

## 🔗 KEY FOREIGN KEY RELATIONSHIPS

```
user_garments:
    user_id -> users.id
    product_master_id -> product_master.id
    product_variant_id -> product_variants.id
    
user_garment_feedback:
    user_garment_id -> user_garments.id
    feedback_code_id -> feedback_codes.id
    
product_master:
    brand_id -> brands.id
    category_id -> categories.id
    subcategory_id -> subcategories.id
    
product_variants:
    product_master_id -> product_master.id
    brand_id -> brands.id
    
measurements:
    set_id -> measurement_sets.id  -- NOT measurement_set_id!
    brand_id -> brands.id
```

---

## 🎯 MIGRATION NOTES

### From Old to New Size Guide System
```sql
-- OLD (deprecated):
SELECT * FROM size_guides sg
JOIN size_guide_entries sge ON sge.size_guide_id = sg.id

-- NEW (current):
SELECT * FROM measurement_sets ms
JOIN measurements m ON m.set_id = ms.id
```

### Common Mistakes to Avoid
1. **NEVER** query `user_garments.brand_id` - it doesn't exist! Use JOIN to `product_master`
2. **NEVER** use `size_purchased` - use `size_label`
3. **NEVER** query `user_garment_feedback.overall_fit` - it's in `user_garments.fit_feedback`
4. **ALWAYS** verify column names with `information_schema.columns` if unsure

---

## 📝 BRAND IDs Reference
```
J.Crew          = 1
Patagonia       = 2  
Banana Republic = 5
Faherty         = 8
Theory          = 9
Reiss           = 10
NN.07           = 12
Lacoste         = (check)
Lululemon       = (check)
Uniqlo          = (check)
```

---

## 🛠️ USEFUL QUERIES

### Check if a column exists
```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'user_garments'
ORDER BY ordinal_position;
```

### Find foreign keys for a table
```sql
SELECT
    kcu.column_name,
    ccu.table_name AS references_table,
    ccu.column_name AS references_column
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY' 
    AND tc.table_name = 'user_garments';
```

---

## ⚠️ FINAL WARNING

**DO NOT TRUST DATABASE_SCHEMA_COMPLETE.md** - It contains numerous errors and outdated information. Always:
1. Use this document (DATABASE_SCHEMA_ACTUAL.md) for reference
2. Verify with `information_schema` when in doubt
3. Test queries before assuming column names
4. Remember that documentation may lag behind actual schema changes
