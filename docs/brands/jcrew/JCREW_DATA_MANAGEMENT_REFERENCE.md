# J.Crew Data Management Complete Reference Guide

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [The Data Corruption Problem](#the-data-corruption-problem)
3. [Product Variant Strategy](#product-variant-strategy)
4. [Data Protection Framework](#data-protection-framework)
5. [Validation System](#validation-system)
6. [Safe Import Process](#safe-import-process)
7. [Scraping Strategy](#scraping-strategy)
8. [Database Schema](#database-schema)
9. [Critical Code Files](#critical-code-files)
10. [Operational Procedures](#operational-procedures)
11. [Troubleshooting Guide](#troubleshooting-guide)
12. [Lessons Learned](#lessons-learned)

---

## Executive Summary

This document captures the complete J.Crew data management system developed in September 2025, including solutions to data corruption, product variant handling, and a comprehensive protection framework inspired by enterprise-grade testing systems.

### Key Achievements
- ✅ Solved data corruption that affected 95 products
- ✅ Implemented compound code strategy preventing duplicates
- ✅ Built SQL validation framework with 5+ test functions
- ✅ Created protection triggers blocking invalid data
- ✅ Established staging import process with rollback
- ✅ Documented all patterns and solutions

---

## The Data Corruption Problem

### What Happened (September 15, 2025)

An AI-assisted scraping session corrupted the J.Crew product cache:

**Before:** 47 products with correct or null fit data
**After:** 95 products with corrupted fit data

### Root Cause Analysis (via ChatGPT Investigation)

1. **Indiscriminate Scraping**: The scraper grabbed ANY text containing fit-related words
   - Example: Stored "Favorite 770™ Straight-fit stretch chino pant" as a fit option for a shirt
   - Captured text from recommended products, reviews, unrelated page sections

2. **Direct Database Writes**: No validation before writing to production
   - Immediately overwrote correct data with garbage
   - No staging or review process

3. **No Protection**: Database had no constraints or triggers
   - Accepted any text as "fit options"
   - No validation against allowed values

### The Fix

1. **Created Selenium-based targeted scrapers** that only extract from specific DOM elements
2. **Implemented validation framework** with fit option whitelist
3. **Added protection triggers** to prevent invalid data
4. **Established staging import** process

---

## Product Variant Strategy

### The Challenge

J.Crew uses the same product in multiple colors/patterns, each with a unique variant code:

```
Base Product: ME053 (Cotton-cashmere shirt)
├── Color 1: CC100 (Dark Chocolate)
└── Color 2: CC101 (Elias Khaki Multi)
```

### Our Solution: Compound Codes

**Format:** `[BASE_CODE]-[VARIANT_CODE]`

**Examples:**
- `ME053-CC100` → Cotton-cashmere shirt in Dark Chocolate
- `ME053-CC101` → Cotton-cashmere shirt in Elias Khaki Multi
- `BE996` → Product without variants (base code only)

### Why This Works

1. **Prevents Duplicates**: Each variant gets unique entry
2. **Preserves Relationships**: Can query all variants of a base product
3. **Matches J.Crew URLs**: Aligns with `colorProductCode` parameter
4. **Supports Inventory**: Different colors may have different availability

### Implementation

```python
# From jcrew_variant_crawler.py
def extract_product_codes(url):
    base_code = 'ME053'  # from URL path
    variant_code = 'CC100'  # from colorProductCode param
    
    if variant_code:
        compound_code = f"{base_code}-{variant_code}"
    else:
        compound_code = base_code
    
    return compound_code
```

---

## Data Protection Framework

### Components

#### 1. Database Backups
- **Table backup**: `jcrew_backup_YYYYMMDD_HHMMSS`
- **JSON export**: `jcrew_backup_YYYYMMDD_HHMMSS.json`
- **Snapshot function**: `create_jcrew_snapshot()`

#### 2. Validation Functions (SQL)
```sql
-- Core validation functions
validate_jcrew_fit_options()     -- Validates against whitelist
check_jcrew_data_quality()        -- Comprehensive quality checks
validate_critical_products()      -- Ensures key products correct
run_jcrew_data_tests()           -- Full test suite
validate_staging_import()         -- Pre-import validation
```

#### 3. Protection Triggers
```sql
-- Active triggers
prevent_jcrew_data_corruption    -- Blocks invalid data
jcrew_audit_changes              -- Logs all changes

-- What they prevent:
❌ Duplicate product codes
❌ Invalid fit options (not in whitelist)
❌ Suspicious text (pant, skirt, $, unavailable)
❌ Removing existing fit data without override
❌ Empty product codes
```

#### 4. Allowed Fit Options (Whitelist)
```python
VALID_FITS = [
    'Classic',
    'Slim',
    'Tall',
    'Relaxed',
    'Slim Untucked',
    'Untucked',
    'Regular',
    'Athletic',
    'Traditional',
    'Big',
    'Big & Tall'
]
```

#### 5. Critical Products (Always Validated)
```
BE996: ['Classic', 'Slim', 'Slim Untucked', 'Tall', 'Relaxed']
ME681: ['Classic', 'Tall']
BM492: ['Classic', 'Slim']
MP235: ['Classic', 'Slim', 'Tall']
```

---

## Validation System

### Test Suite Components

1. **No duplicate product codes** - UNIQUE constraint enforced
2. **All fit options valid** - Checked against whitelist
3. **Critical products correct** - 4 products always validated
4. **No ghost products** - Must have name OR URL
5. **Reasonable fit coverage** - At least 30% should have fits

### Running Validation

```bash
# Run full test suite
python scripts/run_validation_tests.py

# Check data quality
SELECT * FROM check_jcrew_data_quality();

# Validate critical products
SELECT * FROM validate_critical_products();
```

### Expected Results
- ✅ All 5 tests should pass
- ✅ No data quality alerts at ERROR level
- ✅ Critical products all correct

---

## Safe Import Process

### Staging Import Workflow

```python
# 1. Create staging table
staging_table = f"jcrew_staging_{timestamp}"

# 2. Import to staging (no validation yet)
INSERT INTO staging_table ...

# 3. Validate staging data
SELECT * FROM validate_staging_import('staging_table')

# 4. Check for regressions
# Products losing fit data are flagged

# 5. Merge to production (skip regressions)
INSERT INTO jcrew_product_cache ... 
ON CONFLICT (product_code) DO UPDATE ...

# 6. Cleanup
DROP TABLE staging_table
```

### Using SafeJCrewImporter

```python
from scripts.create_staging_process import SafeJCrewImporter

importer = SafeJCrewImporter()
importer.safe_import_process('new_products.json')
```

---

## Scraping Strategy

### Best Practices

1. **Use Selenium for dynamic content**
   ```python
   options.add_argument('--disable-blink-features=AutomationControlled')
   driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
   ```

2. **Target specific DOM elements**
   ```python
   # Good: Specific fit selector
   fit_list = driver.find_element(By.CSS_SELECTOR, 'ul[aria-label="Fit List"]')
   
   # Bad: Generic text search
   if 'slim' in page_text.lower():  # DON'T DO THIS
   ```

3. **Handle product variants**
   ```python
   base_code = extract_from_url_path()
   variant_code = extract_colorProductCode()
   compound_code = f"{base_code}-{variant_code}" if variant_code else base_code
   ```

4. **Validate before writing**
   - Use staging tables
   - Run validation functions
   - Check for regressions

### Scraper Files

- `scripts/jcrew_fit_crawler.py` - Extracts fit options
- `scripts/jcrew_variant_crawler.py` - Handles color variants
- `scripts/jcrew_full_crawler.py` - Complete product data

---

## Database Schema

### Table: jcrew_product_cache

```sql
CREATE TABLE jcrew_product_cache (
    id SERIAL PRIMARY KEY,
    product_code VARCHAR(50) UNIQUE NOT NULL,  -- Compound code
    product_name VARCHAR(255),
    product_url TEXT,
    fit_options TEXT[],          -- Array of valid fits
    colors_available TEXT[],     -- Array of color names
    sizes_available TEXT[],      -- Array of sizes
    category VARCHAR(100),
    subcategory VARCHAR(100),
    material TEXT,
    price DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    cache_key VARCHAR(255) UNIQUE
);

-- Constraints
UNIQUE(product_code)  -- No duplicates
UNIQUE(cache_key)     -- Alternative unique key
```

### Audit Table

```sql
CREATE TABLE jcrew_audit_log (
    audit_id UUID PRIMARY KEY,
    operation VARCHAR(10),      -- INSERT/UPDATE/DELETE
    product_code VARCHAR(50),
    old_data JSONB,
    new_data JSONB,
    changed_fields TEXT[],
    changed_by VARCHAR(100),
    changed_at TIMESTAMP
);
```

---

## Critical Code Files

### Protection & Validation
- `scripts/jcrew_validation_framework.sql` - All validation SQL functions
- `scripts/create_protection_triggers.sql` - Protection triggers
- `scripts/run_validation_tests.py` - Test runner
- `scripts/backup_jcrew_data.py` - Backup utility
- `scripts/create_staging_process.py` - Safe import class

### Scrapers
- `scripts/jcrew_fit_crawler.py` - Fit option extraction
- `scripts/jcrew_variant_crawler.py` - Variant handling
- `scripts/jcrew_full_crawler.py` - Complete scraper

### Documentation
- `JCREW_PRODUCT_VARIANT_STRATEGY.md` - Variant code strategy
- `JCREW_DATA_MANAGEMENT_REFERENCE.md` - This document
- `daily-notes/2025-09-16/` - Implementation notes

---

## Operational Procedures

### Daily Operations

#### To Add New Products
```bash
# 1. Backup first
python scripts/backup_jcrew_data.py

# 2. Scrape with validation
python scripts/jcrew_variant_crawler.py --staging --validate

# 3. Review and import
python scripts/create_staging_process.py
```

#### To Fix Data Issues
```bash
# 1. Run validation
python scripts/run_validation_tests.py

# 2. Fix specific issues
UPDATE jcrew_product_cache 
SET fit_options = ARRAY['Classic', 'Slim']
WHERE product_code = 'XXXXX';

# 3. Verify fixes
SELECT * FROM validate_critical_products();
```

### Emergency Procedures

#### Disable Protection (Emergency Only)
```sql
SELECT disable_jcrew_protection();
-- Make emergency fixes
SELECT enable_jcrew_protection();
```

#### Restore from Backup
```sql
-- Restore from snapshot
SELECT restore_jcrew_snapshot('jcrew_backup_20250916_134019');

-- Or restore from JSON
python scripts/restore_from_json.py jcrew_backup_20250916_134019.json
```

#### Review Recent Changes
```sql
-- See all changes in last 24 hours
SELECT * FROM review_jcrew_changes(24);

-- Check audit log
SELECT * FROM jcrew_audit_log 
WHERE changed_at > NOW() - INTERVAL '1 day'
ORDER BY changed_at DESC;
```

---

## Troubleshooting Guide

### Common Issues

#### 1. "Invalid fit options" Error
**Cause:** Trying to insert fit not in whitelist
**Solution:** Check `VALID_FITS` list, add to whitelist if legitimate

#### 2. "Duplicate product code" Error  
**Cause:** Product already exists
**Solution:** Use UPDATE instead of INSERT, or check for variants

#### 3. Scraper Timeout
**Cause:** J.Crew blocking or slow response
**Solution:** Add delays, rotate user agents, use headless=False for debugging

#### 4. Missing Fit Data After Scrape
**Cause:** Fits loaded dynamically or in different DOM location
**Solution:** Update selector in scraper, check for JavaScript rendering

### Validation Failures

#### Test: "No duplicate product codes" FAILS
```sql
-- Find duplicates
SELECT product_code, COUNT(*) 
FROM jcrew_product_cache 
GROUP BY product_code 
HAVING COUNT(*) > 1;

-- Fix by deleting newer duplicate
DELETE FROM jcrew_product_cache 
WHERE ctid NOT IN (
    SELECT MIN(ctid) 
    FROM jcrew_product_cache 
    GROUP BY product_code
);
```

#### Test: "All fit options valid" FAILS
```sql
-- Find invalid fits
SELECT product_code, fit_options 
FROM jcrew_product_cache
WHERE NOT validate_jcrew_fit_options(product_code, fit_options);

-- Fix by updating to valid fits or NULL
UPDATE jcrew_product_cache 
SET fit_options = NULL 
WHERE product_code = 'XXXXX';
```

---

## Lessons Learned

### What Went Wrong (Pre-Framework)

1. **Trusted AI blindly** - AI agent made destructive changes without validation
2. **No staging process** - Direct writes to production
3. **No validation** - Accepted any text as valid data
4. **No backups** - Couldn't easily recover
5. **Generic scraping** - Grabbed text from entire page

### What We Did Right (Post-Framework)

1. **Built comprehensive protection** - Triggers, validation, constraints
2. **Implemented staging** - Test before production
3. **Created whitelist** - Only valid fits allowed
4. **Regular backups** - Multiple recovery options
5. **Targeted scraping** - Extract from specific elements

### Key Insights

1. **Database changes need more protection than code** - Can't just `git revert`
2. **AI assistants need guardrails** - Validate their output
3. **Staging is essential** - Never write directly to production
4. **Compound codes work** - Solves J.Crew's variant challenge
5. **Validation at every level** - Database, application, import process

### Best Practices Established

1. **Always backup before bulk operations**
2. **Use staging tables for imports**
3. **Validate against whitelist**
4. **Keep audit trail of all changes**
5. **Test with known-good products**
6. **Document everything** (this document!)

---

## Future Enhancements

### Potential Improvements

1. **Add base_product_code field** - Easier variant queries
2. **Create product_families table** - Group variants
3. **Implement version control** - Track all historical changes
4. **Add automated testing** - Run tests on schedule
5. **Build admin interface** - Non-technical data management

### Scaling Considerations

- Current system handles 100s of products well
- For 1000s+, consider:
  - Partitioning by brand or category
  - Caching layer for read performance
  - Queue system for import processing
  - Dedicated scraping infrastructure

---

## Summary

This J.Crew data management system provides:

✅ **Data Integrity** - Protection against corruption
✅ **Audit Trail** - Complete change history  
✅ **Validation** - Multi-level data quality checks
✅ **Recovery** - Multiple backup/restore options
✅ **Scalability** - Handles variants and growth
✅ **Documentation** - Comprehensive reference

The system successfully recovered from data corruption and now prevents future issues through validation, protection triggers, and staging imports. The compound code strategy elegantly handles J.Crew's product variant system while preventing duplicates.

---

## Quick Reference Commands

```bash
# Backup
python scripts/backup_jcrew_data.py

# Validate
python scripts/run_validation_tests.py

# Scrape safely
python scripts/jcrew_variant_crawler.py --staging

# Import safely
python scripts/create_staging_process.py

# Check specific product
SELECT * FROM jcrew_product_cache WHERE product_code = 'ME053-CC100';

# Run all tests
SELECT * FROM run_jcrew_data_tests();

# Review changes
SELECT * FROM review_jcrew_changes(24);
```

---

*Last Updated: September 16, 2025*
*System Status: ✅ Fully Operational*
*Data Quality: 100% Validated*
