# Database Query Cookbook - Tested & Working Examples

**Created**: January 19, 2025  
**Purpose**: Tested, working SQL queries for the tailor3 database  
**For**: AI assistants and developers who need reliable query examples  

> 🎯 **Every query in this file has been tested and confirmed working**  
> 🔍 **Use these as starting points - they handle the correct column names and table relationships**

---

## 🗄️ **Quick Table & Column Reference**

### Core Tables & Key Columns
```sql
-- ✅ TESTED: Essential columns to avoid KeyError issues
brands: id, name, region, default_unit, notes
categories: id, name, description
subcategories: id, name, category_id, description
user_garments: id, user_id, brand_id, category_id, subcategory_id, size_label, product_name, notes, image_url
size_guides: id, brand_id, gender, category_id, subcategory_id, fit_type, specificity, guide_level, unit, source_url, size_guide_header, notes
size_guide_entries: id, size_guide_id, size_label, chest_min, chest_max, waist_min, waist_max, neck_min, neck_max, measurements_available
raw_size_guides: id, brand_id, gender, category_id, subcategory_id, fit_type, source_url, screenshot_path, raw_text
users: id, email, gender, height, preferred_units
body_measurements: id, user_id, chest, waist, neck, sleeve_length
user_actions: id, user_id, action_type, target_table, created_at, is_undone
```

---

## 🏢 **Brand Operations**

### Get All Brands with Counts
```sql
-- ✅ TESTED: Shows all brands with garment and size guide counts
SELECT 
    b.id,
    b.name,
    b.region,
    b.default_unit,
    COUNT(DISTINCT ug.id) as garment_count,
    COUNT(DISTINCT sg.id) as size_guide_count
FROM brands b
LEFT JOIN user_garments ug ON b.id = ug.brand_id
LEFT JOIN size_guides sg ON b.id = sg.brand_id
GROUP BY b.id, b.name, b.region, b.default_unit
ORDER BY b.name;
```

### Find Specific Brand with Details
```sql
-- ✅ TESTED: Get complete brand information
SELECT * FROM brands WHERE name = 'Lacoste';
```

### Check Brand Data Completeness
```sql
-- ✅ TESTED: See what data exists for a brand
SELECT 
    b.name as brand_name,
    COUNT(DISTINCT sg.id) as size_guides,
    COUNT(DISTINCT sge.id) as size_entries,
    COUNT(DISTINCT ug.id) as user_garments
FROM brands b
LEFT JOIN size_guides sg ON b.id = sg.brand_id
LEFT JOIN size_guide_entries sge ON sg.id = sge.size_guide_id
LEFT JOIN user_garments ug ON b.id = ug.brand_id
WHERE b.name = 'Lacoste'
GROUP BY b.id, b.name;
```

### Check if Brand Exists Before Creation
```sql
-- ✅ TESTED: Prevent duplicate brand creation
SELECT id, name, region, default_unit 
FROM brands 
WHERE LOWER(name) = LOWER('Uniqlo');
```

### Create New Brand with RETURNING
```sql
-- ✅ TESTED: Create brand and get ID for immediate use
INSERT INTO brands (name, region, default_unit, notes) 
VALUES ('Uniqlo', 'Japan', 'in', 'Japanese fast fashion retailer with international presence') 
RETURNING id;
```

---

## 👔 **Garment Operations**

### Get User's Complete Closet
```sql
-- ✅ TESTED: Full closet view with brand and category names
SELECT 
    ug.id,
    ug.size_label,
    b.name as brand_name,
    c.name as category_name,
    sc.name as subcategory_name,
    ug.notes
FROM user_garments ug
JOIN brands b ON ug.brand_id = b.id
LEFT JOIN categories c ON ug.category_id = c.id
LEFT JOIN subcategories sc ON ug.subcategory_id = sc.id
WHERE ug.user_id = 1
ORDER BY b.name, ug.size_label;
```

### Find Garments by Brand
```sql
-- ✅ TESTED: All garments from specific brand
SELECT 
    ug.*,
    b.name as brand_name,
    c.name as category_name,
    sc.name as subcategory_name
FROM user_garments ug
JOIN brands b ON ug.brand_id = b.id
LEFT JOIN categories c ON ug.category_id = c.id
LEFT JOIN subcategories sc ON ug.subcategory_id = sc.id
WHERE b.name = 'Lacoste';
```

### Get Garment with Size Guide Data
```sql
-- ✅ TESTED: Garment with corresponding size guide measurements
SELECT 
    ug.size_label,
    b.name as brand,
    sge.chest_min, sge.chest_max,
    sge.waist_min, sge.waist_max,
    sge.neck_min, sge.neck_max
FROM user_garments ug
JOIN brands b ON ug.brand_id = b.id
JOIN size_guides sg ON (b.id = sg.brand_id AND ug.category_id = sg.category_id)
JOIN size_guide_entries sge ON (sg.id = sge.size_guide_id AND ug.size_label = sge.size_label)
WHERE ug.id = 17;  -- Replace with specific garment ID
```

---

## 📏 **Size Guide Operations**

### Get Complete Size Guide for Brand
```sql
-- ✅ TESTED: Full size chart with all measurements
SELECT 
    sg.id as guide_id,
    sg.gender,
    sg.fit_type,
    sg.specificity,
    sge.size_label,
    sge.chest_min, sge.chest_max,
    sge.waist_min, sge.waist_max,
    sge.neck_min, sge.neck_max,
    sge.measurements_available
FROM size_guides sg
JOIN size_guide_entries sge ON sg.id = sge.size_guide_id
JOIN brands b ON sg.brand_id = b.id
WHERE b.name = 'Lacoste'
ORDER BY sge.size_label;
```

### Count Size Entries by Brand
```sql
-- ✅ TESTED: How many sizes each brand has
SELECT 
    b.name as brand_name,
    sg.gender,
    sg.fit_type,
    COUNT(sge.id) as size_count
FROM brands b
JOIN size_guides sg ON b.id = sg.brand_id
JOIN size_guide_entries sge ON sg.id = sge.size_guide_id
GROUP BY b.name, sg.gender, sg.fit_type
ORDER BY b.name;
```

### Find Size Guide by Specificity
```sql
-- ✅ TESTED: Get guides by how specific they are
SELECT 
    b.name as brand,
    sg.specificity,
    sg.gender,
    sg.fit_type,
    c.name as category,
    sc.name as subcategory
FROM size_guides sg
JOIN brands b ON sg.brand_id = b.id
LEFT JOIN categories c ON sg.category_id = c.id
LEFT JOIN subcategories sc ON sg.subcategory_id = sc.id
WHERE sg.specificity = 'specific'
ORDER BY b.name;
```

### Create Complete Size Guide with Metadata
```sql
-- ✅ TESTED: Create size guide with all required fields including specificity
INSERT INTO size_guides (
    brand_id, gender, category_id, subcategory_id, fit_type,
    guide_level, specificity, unit, source_url, size_guide_header, notes
) VALUES (
    12, 'Male', 1, NULL, 'NA',
    'category_level', 'broad', 'in', 
    'https://www.uniqlo.com/us/en/size-guide',
    'MEN Body dimensions', 
    'Universal size guide for all men''s tops. Labeled as "Common" indicating broad applicability across all men''s top categories.'
) RETURNING id;
```

### Create Raw Size Guide Documentation
```sql
-- ✅ TESTED: Store source documentation for size guide ingestion
INSERT INTO raw_size_guides (
    brand_id, gender, category_id, subcategory_id, fit_type,
    source_url, screenshot_path, raw_text
) VALUES (
    12, 'Male', 1, NULL, 'Unspecified',
    'https://www.uniqlo.com/us/en/size-guide',
    'User provided screenshot of Uniqlo MEN Body dimensions size guide',
    'MEN Body dimensions - Common size guide showing Height (feet/cm), Chest (inch/cm), Waist (inch/cm) for sizes XXS through 4XL'
);
```

---

## 🔍 **Fit Analysis Queries**

### Compare User Measurements to Size Guide
```sql
-- ✅ TESTED: See how user measurements compare to garment sizes
SELECT 
    bm.chest as user_chest,
    bm.waist as user_waist,
    bm.neck as user_neck,
    sge.size_label,
    sge.chest_min, sge.chest_max,
    sge.waist_min, sge.waist_max,
    sge.neck_min, sge.neck_max,
    CASE 
        WHEN bm.chest BETWEEN sge.chest_min AND sge.chest_max THEN 'FITS'
        WHEN bm.chest < sge.chest_min THEN 'TOO_BIG'
        ELSE 'TOO_SMALL'
    END as chest_fit
FROM body_measurements bm
CROSS JOIN size_guide_entries sge
JOIN size_guides sg ON sge.size_guide_id = sg.id
JOIN brands b ON sg.brand_id = b.id
WHERE bm.user_id = 1 AND b.name = 'Lacoste';
```

### Find Best Size for User
```sql
-- ✅ TESTED: Recommend best size based on measurements
SELECT 
    b.name as brand,
    sge.size_label,
    ABS(bm.chest - (sge.chest_min + sge.chest_max)/2) as chest_diff,
    ABS(bm.waist - (sge.waist_min + sge.waist_max)/2) as waist_diff,
    sge.chest_min, sge.chest_max,
    sge.waist_min, sge.waist_max
FROM body_measurements bm
CROSS JOIN size_guide_entries sge
JOIN size_guides sg ON sge.size_guide_id = sg.id
JOIN brands b ON sg.brand_id = b.id
WHERE bm.user_id = 1 AND b.name = 'J.Crew'
ORDER BY (ABS(bm.chest - (sge.chest_min + sge.chest_max)/2) + 
          ABS(bm.waist - (sge.waist_min + sge.waist_max)/2))
LIMIT 3;
```

---

## 📊 **Analytics & Reporting**

### Database Overview Stats
```sql
-- ✅ TESTED: Complete database statistics
SELECT 
    'Brands' as table_name, COUNT(*) as count FROM brands
UNION ALL
SELECT 'Categories', COUNT(*) FROM categories
UNION ALL
SELECT 'Subcategories', COUNT(*) FROM subcategories
UNION ALL
SELECT 'Size Guides', COUNT(*) FROM size_guides
UNION ALL
SELECT 'Size Entries', COUNT(*) FROM size_guide_entries
UNION ALL
SELECT 'User Garments', COUNT(*) FROM user_garments
UNION ALL
SELECT 'Users', COUNT(*) FROM users
ORDER BY table_name;
```

### Recent Activity Summary
```sql
-- ✅ TESTED: What happened recently
SELECT 
    action_type,
    target_table,
    COUNT(*) as count,
    MAX(created_at) as latest
FROM user_actions
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY action_type, target_table
ORDER BY latest DESC;
```

### Brand Coverage Analysis
```sql
-- ✅ TESTED: Which brands have complete data
SELECT 
    b.name,
    b.region,
    CASE WHEN COUNT(sg.id) > 0 THEN 'YES' ELSE 'NO' END as has_size_guide,
    CASE WHEN COUNT(ug.id) > 0 THEN 'YES' ELSE 'NO' END as has_garments,
    COUNT(DISTINCT sge.size_label) as size_count
FROM brands b
LEFT JOIN size_guides sg ON b.id = sg.brand_id
LEFT JOIN size_guide_entries sge ON sg.id = sge.size_guide_id
LEFT JOIN user_garments ug ON b.id = ug.brand_id
GROUP BY b.id, b.name, b.region
ORDER BY b.name;
```

### Comprehensive Size Guide Verification
```sql
-- ✅ TESTED: Complete verification of size guide ingestion with all joins
SELECT 
    sg.id, sg.brand_id, b.name as brand_name, sg.gender, sg.specificity, 
    sg.guide_level, sg.size_guide_header, sg.notes
FROM size_guides sg 
JOIN brands b ON sg.brand_id = b.id 
WHERE sg.id = 14;  -- Replace with specific size guide ID
```

### Size Entry Quality Check with Progression
```sql
-- ✅ TESTED: Verify size entries with logical ordering
SELECT 
    size_label, chest_min, chest_max, chest_range, 
    waist_min, waist_max, waist_range
FROM size_guide_entries 
WHERE size_guide_id = 14 
ORDER BY 
    CASE 
        WHEN size_label = 'XXS' THEN 1
        WHEN size_label = 'XS' THEN 2
        WHEN size_label = 'S' THEN 3
        WHEN size_label = 'M' THEN 4
        WHEN size_label = 'L' THEN 5
        WHEN size_label = 'XL' THEN 6
        WHEN size_label = 'XXL' THEN 7
        WHEN size_label = '3XL' THEN 8
        WHEN size_label = '4XL' THEN 9
    END;
```

### Measurement Progression Analysis
```sql
-- ✅ TESTED: Check for overlaps in measurement ranges
SELECT 
    size_label, chest_min, chest_max,
    LAG(chest_max) OVER (ORDER BY chest_min) as prev_max,
    CASE 
        WHEN chest_min < LAG(chest_max) OVER (ORDER BY chest_min) 
        THEN 'OVERLAP' 
        ELSE 'OK' 
    END as overlap_status
FROM size_guide_entries 
WHERE size_guide_id = 14 AND chest_min IS NOT NULL
ORDER BY chest_min;
```

---

## 🔧 **System Maintenance**

### Check Table Column Names (Avoid KeyErrors)
```sql
-- ✅ TESTED: Get actual column names for any table
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'user_garments'  -- Change table name as needed
ORDER BY ordinal_position;
```

### Audit Trail Analysis
```sql
-- ✅ TESTED: See what changes were made
SELECT 
    created_at,
    action_type,
    target_table,
    CASE 
        WHEN LENGTH(sql_command) > 50 
        THEN LEFT(sql_command, 50) || '...'
        ELSE sql_command
    END as sql_preview
FROM user_actions
WHERE is_undone = false
ORDER BY created_at DESC
LIMIT 20;
```

### Find Orphaned Records
```sql
-- ✅ TESTED: Check for data integrity issues
SELECT 'user_garments without brands' as issue, COUNT(*) as count
FROM user_garments ug
LEFT JOIN brands b ON ug.brand_id = b.id
WHERE b.id IS NULL
UNION ALL
SELECT 'size_guides without brands', COUNT(*)
FROM size_guides sg
LEFT JOIN brands b ON sg.brand_id = b.id
WHERE b.id IS NULL;
```

---

## 🚀 **Quick Connection Test**

### Verify Database Connection
```sql
-- ✅ TESTED: Simple connection test
SELECT 
    'Database Connected' as status,
    CURRENT_TIMESTAMP as timestamp,
    CURRENT_USER as user;
```

---

## 📝 **Usage Notes**

### For AI Assistants:
1. **Always use these exact column names** - they're tested and current
2. **Start with simple queries** - build complexity gradually  
3. **Test before adding new queries** - only add confirmed working examples
4. **Use the column reference** - check actual column names if unsure

### For Developers:
1. **Copy-paste ready** - all queries work as-is
2. **Replace placeholder values** - like user IDs, brand names, garment IDs
3. **Extend carefully** - maintain the same patterns for consistency

---

**Last Updated**: January 20, 2025  
**Next Update**: Add queries as they're tested and confirmed working

**Recent Additions (Jan 20, 2025)**:
- Brand existence checking and creation patterns with RETURNING
- Complete size guide creation with specificity field
- Raw size guide documentation storage
- Comprehensive verification queries with joins
- Size progression analysis with overlap detection

