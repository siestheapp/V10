# Database Query Cookbook V2 - Updated for Current Schema

**Created**: September 10, 2025  
**Database**: tailor3 (Current schema with 59 tables)  
**Status**: ✅ TESTED & WORKING

> ⚠️ **IMPORTANT**: The original `database_query_cookbook.md` is OUTDATED. Use this document for current queries.

---

## 🔑 Key Schema Changes

### User Garments Now Split
```sql
-- OLD (doesn't work):
SELECT brand_id, category_id FROM user_garments;

-- NEW (correct):
SELECT g.brand_id, g.category_id 
FROM user_garments ug
JOIN garments g ON ug.garment_id = g.id;
```

---

## 📊 Working Queries for Current Schema

### Get User's Closet with Full Details
```sql
-- ✅ TESTED: Get user's garments with brand, category, and feedback
SELECT 
    ug.id,
    ug.user_id,
    ug.size_label,
    g.product_name,
    b.name as brand_name,
    c.name as category_name,
    sc.name as subcategory_name,
    ug.fit_feedback,
    ug.garment_status
FROM user_garments ug
LEFT JOIN garments g ON ug.garment_id = g.id
LEFT JOIN brands b ON g.brand_id = b.id
LEFT JOIN categories c ON g.category_id = c.id
LEFT JOIN subcategories sc ON g.subcategory_id = sc.id
WHERE ug.user_id = 1
ORDER BY ug.created_at DESC;
```

### Get Brand's Products and Measurements
```sql
-- ✅ TESTED: Get all products for a brand with measurements
SELECT 
    g.id,
    g.product_name,
    g.product_code,
    c.name as category,
    g.fit_type,
    COUNT(DISTINCT m.id) as measurement_count
FROM garments g
JOIN brands b ON g.brand_id = b.id
LEFT JOIN categories c ON g.category_id = c.id
LEFT JOIN measurements m ON m.brand_id = b.id
WHERE b.name ILIKE '%vuori%'
GROUP BY g.id, g.product_name, g.product_code, c.name, g.fit_type;
```

### Get Measurements for a Specific Size
```sql
-- ✅ TESTED: Get all measurements for a brand/size combination
SELECT 
    m.size_label,
    m.measurement_type,
    m.measurement_category,
    m.min_value,
    m.max_value,
    m.exact_value,
    mt.display_name,
    mt.unit
FROM measurements m
JOIN measurement_types mt ON m.measurement_type = mt.name
JOIN brands b ON m.brand_id = b.id
WHERE b.name = 'Vuori' 
  AND m.size_label = 'M'
ORDER BY mt.display_order, m.measurement_type;
```

### Get Try-On Session Details
```sql
-- ✅ TESTED: Get try-on sessions with items and feedback
SELECT 
    ts.id as session_id,
    ts.session_date,
    ts.location,
    ti.id as item_id,
    g.product_name,
    b.name as brand_name,
    ti.size_tried,
    ti.fit_decision,
    ti.overall_fit,
    ti.confidence_score
FROM try_on_sessions ts
JOIN try_on_items ti ON ts.id = ti.session_id
JOIN garments g ON ti.garment_id = g.id
LEFT JOIN brands b ON g.brand_id = b.id
WHERE ts.user_id = 1
ORDER BY ts.session_date DESC, ti.id;
```

### Get User's Fit Feedback History
```sql
-- ✅ TESTED: Get detailed fit feedback for analysis
SELECT 
    ugf.id,
    g.product_name,
    b.name as brand_name,
    ugf.size_worn,
    ugf.overall_fit,
    ugf.chest_fit,
    ugf.waist_fit,
    ugf.length_fit,
    ugf.sleeve_fit,
    ugf.confidence,
    ugf.would_buy_again,
    ugf.feedback_date
FROM user_garment_feedback ugf
JOIN user_garments ug ON ugf.user_garment_id = ug.id
LEFT JOIN garments g ON ug.garment_id = g.id
LEFT JOIN brands b ON g.brand_id = b.id
WHERE ugf.user_id = 1
ORDER BY ugf.feedback_date DESC;
```

### Analyze Brand Measurement Consistency
```sql
-- ✅ TESTED: Check measurement availability by brand
SELECT 
    b.name as brand_name,
    COUNT(DISTINCT m.size_label) as sizes_available,
    COUNT(DISTINCT m.measurement_type) as measurement_types,
    COUNT(m.id) as total_measurements,
    ARRAY_AGG(DISTINCT m.measurement_type) as available_measurements
FROM brands b
LEFT JOIN measurements m ON b.id = m.brand_id
GROUP BY b.id, b.name
HAVING COUNT(m.id) > 0
ORDER BY COUNT(m.id) DESC;
```

### Get User's Fit Zones
```sql
-- ✅ TESTED: Get personalized fit zones
SELECT 
    ufz.dimension,
    ufz.preferred_min,
    ufz.preferred_max,
    ufz.acceptable_min,
    ufz.acceptable_max,
    ufz.confidence_level,
    ufz.last_updated
FROM user_fit_zones ufz
WHERE ufz.user_id = 1
ORDER BY ufz.dimension;
```

---

## 🔍 Useful Views to Query

Instead of complex joins, use these pre-built views:

### user_garments_full
```sql
-- Complete user garment info with all relationships resolved
SELECT * FROM user_garments_full WHERE user_id = 1;
```

### measurements_simple
```sql
-- Simplified measurement view
SELECT * FROM measurements_simple WHERE brand_name = 'Vuori';
```

### feedback_complete
```sql
-- All feedback with context
SELECT * FROM feedback_complete WHERE user_id = 1;
```

---

## 📝 Common Operations

### Add a New Garment to User's Closet
```sql
-- Step 1: Check if garment exists
SELECT id FROM garments 
WHERE brand_id = ? AND product_name = ?;

-- Step 2a: If not exists, create garment
INSERT INTO garments (brand_id, category_id, subcategory_id, product_name)
VALUES (?, ?, ?, ?)
RETURNING id;

-- Step 2b: Add to user's closet
INSERT INTO user_garments (user_id, garment_id, size_label, garment_status)
VALUES (?, ?, ?, 'active')
RETURNING id;
```

### Record Try-On Feedback
```sql
-- Create session
INSERT INTO try_on_sessions (user_id, session_date, location)
VALUES (?, CURRENT_DATE, ?)
RETURNING id;

-- Add try-on item
INSERT INTO try_on_items (
    session_id, garment_id, size_tried, 
    fit_decision, overall_fit, confidence_score
)
VALUES (?, ?, ?, ?, ?, ?);
```

### Update Fit Zones Based on Feedback
```sql
-- Update or insert user fit zone
INSERT INTO user_fit_zones (
    user_id, dimension, preferred_min, preferred_max,
    acceptable_min, acceptable_max, confidence_level
)
VALUES (?, ?, ?, ?, ?, ?, ?)
ON CONFLICT (user_id, dimension)
DO UPDATE SET
    preferred_min = EXCLUDED.preferred_min,
    preferred_max = EXCLUDED.preferred_max,
    confidence_level = EXCLUDED.confidence_level,
    last_updated = CURRENT_TIMESTAMP;
```

---

## ⚠️ Common Pitfalls

1. **Don't query `user_garments.brand_id`** - it doesn't exist anymore
2. **Use `garments` table** for product details
3. **Join through `garment_id`** to get product info
4. **Check `measurement_sets`** for grouped measurements
5. **Use views** when available to avoid complex joins

---

## 🚀 Performance Tips

1. **Use indexes**: Most foreign keys are indexed
2. **Leverage views**: Pre-optimized for common queries  
3. **Limit results**: Always use LIMIT for exploration
4. **Filter early**: Add WHERE clauses before JOINs

---

*Last Updated: September 10, 2025*  
*Database Dump: tailor3_dump_2025-09-10.sql*
