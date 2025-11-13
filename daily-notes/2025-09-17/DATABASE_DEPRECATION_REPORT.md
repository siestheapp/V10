# Database Deprecation & Schema Accuracy Report
> Generated: 2025-09-17
> Purpose: Identify deprecated tables, schema mismatches, and prevent future query errors

## 🚨 CRITICAL SCHEMA MISMATCHES

### ❌ user_garments Table - DOCUMENTATION IS WRONG
**Documentation claims these columns exist, but they DON'T:**
- `brand_id` - ❌ DOES NOT EXIST
- `product_code` - ❌ DOES NOT EXIST  
- `garment_name` - ❌ DOES NOT EXIST
- `category` - ❌ DOES NOT EXIST
- `size_purchased` - ❌ DOES NOT EXIST (use `size_label` instead)

**Actual columns in user_garments:**
```sql
id                  INTEGER (PK)
user_id             INTEGER -> users.id
size_label          TEXT (this is what we called size_purchased)
product_master_id   INTEGER -> product_master.id (for linking products)
product_variant_id  INTEGER -> product_variants.id (for specific variant)
fit_feedback        TEXT (overall fit assessment)
garment_id          INTEGER -> garments.id
-- plus metadata columns
```

### ❌ user_garment_feedback Table - COMPLETELY DIFFERENT SCHEMA
**Documentation is completely wrong. The actual table has:**
```sql
id                  INTEGER (PK)
user_garment_id     INTEGER -> user_garments.id
dimension           TEXT (e.g., 'chest', 'neck', 'sleeve')
feedback_code_id    INTEGER -> feedback_codes.id
measurement_source  TEXT
measurement_id      INTEGER
created_at          TIMESTAMP
created_by          INTEGER -> admins.id
```

**Documentation incorrectly lists these columns that DON'T EXIST:**
- `feedback_type` ❌
- `fit_assessment` ❌
- `fit_zones` ❌
- `dimensional_feedback` ❌
- `rating` ❌
- `notes` ❌
- `overall_fit` ❌ (this is in user_garments.fit_feedback)
- `specific_feedback` ❌
- `wear_context` ❌
- `comfort_rating` ❌
- `would_recommend` ❌
- `feedback_date` ❌ (use `created_at` instead)

## 🗑️ DEPRECATED TABLES

### Confirmed Deprecated (by naming pattern):
1. **jcrew_backup_20250916_134019** - Backup table with timestamp
2. **jcrew_test_results** - Test table (also empty)
3. **size_guides_v2** - Old version (is a VIEW, not a table)

### Empty Tables (likely deprecated or not yet implemented):
1. **body_measurements** - 0 rows, but has 4 constraints
2. **brand_product_cache** - 0 rows, caching not implemented
3. **dimension_feedback_sequence** - 0 rows, 5 constraints
4. **try_on_items** - 0 rows, part of unused try-on system
5. **try_on_sessions** - 0 rows, part of unused try-on system
6. **user_preferences** - 0 rows, preferences not implemented

## 📊 VIEWS (Often Confused with Tables)

These are VIEWS, not tables - they're computed from other tables:
- `user_garments_full` - Joins user_garments with related data
- `try_on_summary` - Summary view (empty because base tables empty)
- `size_guides_v2` - View, not a table
- `product_catalog` - Product listing view
- `measurements_simple` - Simplified measurements view
- `feedback_complete` - Complete feedback view

## ✅ CORRECT USAGE PATTERNS

### When querying user feedback:
```python
# CORRECT - use actual schema
cur.execute('''
    SELECT 
        ugf.dimension,
        ugf.feedback_code_id,
        fc.description as feedback_desc,
        ug.fit_feedback as overall_fit,
        ug.size_label
    FROM user_garment_feedback ugf
    JOIN user_garments ug ON ugf.user_garment_id = ug.id
    LEFT JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
    WHERE ug.user_id = %s
''', (user_id,))
```

### When linking products:
```python
# CORRECT - use product_master_id and product_variant_id
cur.execute('''
    SELECT 
        ug.id,
        pm.base_name,      -- NOT product_name
        pv.color_name,     -- NOT color
        pv.fit_option,     -- NOT fit_type
        b.name as brand    -- NOT brand_name in brands table
    FROM user_garments ug
    LEFT JOIN product_master pm ON ug.product_master_id = pm.id
    LEFT JOIN product_variants pv ON ug.product_variant_id = pv.id
    LEFT JOIN brands b ON pm.brand_id = b.id
''')
```

## 🔧 RECOMMENDATIONS

### Immediate Actions:
1. **Update DATABASE_SCHEMA_COMPLETE.md** to reflect actual schema
2. **Stop using deprecated column names** in queries
3. **Use foreign keys** instead of denormalized data:
   - Get brand via: `user_garments -> product_master -> brands`
   - Get product info via: `user_garments -> product_master`

### Tables to Avoid:
- Any table ending in `_backup`, `_test`, `_old`, `_v1`, `_v2`
- Empty tables unless implementing new features
- Views when you need to write data

### Key Reminders:
- **brands table**: Use `name` not `brand_name`, use `id` not `brand_id`
- **product_master**: Use `base_name` not `product_name`
- **product_variants**: Use `color_name` not `color`, `fit_option` not `fit_type`
- **J.Crew brand_id = 1**, **Reiss brand_id = 10**
- Always use `DB_CONFIG` from `db_config.py` for connections

## 📝 MEMORY UPDATE NEEDED

The memory ID 9015374 about DATABASE_SCHEMA_COMPLETE.md is now known to be INCORRECT for:
- user_garments schema
- user_garment_feedback schema

These tables have completely different schemas than documented.
