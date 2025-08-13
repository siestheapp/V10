# App Code Migration Guide for Updated Database

## Overview
The database has been completely restructured with a unified measurement system. This guide shows what needs to be updated in the iOS app backend.

## Key Database Changes
1. **Removed `garment_id` from measurements** - All measurements now use `set_id`
2. **New unified structure:**
   - `measurement_sets` - Headers for both size guides and garment specs
   - `measurements` - All measurement data in one table
3. **Backward compatibility views available** for easier migration

## Required Code Changes

### 1. Update Size Guide Queries

**OLD CODE (app.py lines 1286-1290):**
```python
cur.execute("""
    SELECT DISTINCT category, measurements_available
    FROM size_guides_v2
    WHERE category ILIKE %s
""", ('%' + request.message.split()[0] + '%',))
```

**NEW CODE:**
```python
cur.execute("""
    SELECT DISTINCT 
        ms.category_id,
        c.name as category,
        array_agg(DISTINCT m.measurement_type) as measurements_available
    FROM measurement_sets ms
    JOIN measurements m ON m.set_id = ms.id
    JOIN categories c ON c.id = ms.category_id
    WHERE ms.scope = 'size_guide'
    AND c.name ILIKE %s
    GROUP BY ms.category_id, c.name
""", ('%' + request.message.split()[0] + '%',))
```

### 2. Get Brand Measurements (app.py lines 2273-2278)

**OLD CODE:**
```python
measurements = await conn.fetchrow("""
    SELECT 
        chest_min, chest_max,
        neck_min, neck_max,
        sleeve_min, sleeve_max,
        waist_min, waist_max
    FROM size_guides_v2 
    WHERE brand_id = $1 AND size_label = $2
""", brand_id, size_label)
```

**NEW CODE (Using View):**
```python
measurements = await conn.fetchrow("""
    SELECT 
        chest_min, chest_max,
        neck_min, neck_max,
        sleeve_min, sleeve_max,
        waist_min, waist_max
    FROM size_guide_entries_view sge
    JOIN size_guides_view sg ON sg.size_guide_id = sge.size_guide_id
    WHERE sg.brand_id = $1 AND sge.size_label = $2
""", brand_id, size_label)
```

**NEW CODE (Direct Query):**
```python
measurements = await conn.fetchrow("""
    WITH brand_measurements AS (
        SELECT 
            m.measurement_type,
            m.size_label,
            m.min_value,
            m.max_value
        FROM measurements m
        JOIN measurement_sets ms ON ms.id = m.set_id
        WHERE ms.brand_id = $1 
        AND ms.scope = 'size_guide'
        AND m.size_label = $2
    )
    SELECT 
        MAX(CASE WHEN measurement_type = 'body_chest' THEN min_value END) as chest_min,
        MAX(CASE WHEN measurement_type = 'body_chest' THEN max_value END) as chest_max,
        MAX(CASE WHEN measurement_type = 'body_neck' THEN min_value END) as neck_min,
        MAX(CASE WHEN measurement_type = 'body_neck' THEN max_value END) as neck_max,
        MAX(CASE WHEN measurement_type = 'body_sleeve' THEN min_value END) as sleeve_min,
        MAX(CASE WHEN measurement_type = 'body_sleeve' THEN max_value END) as sleeve_max
    FROM brand_measurements
""", brand_id, size_label)
```

### 3. Get Garment Measurements (app.py lines 2493-2543)

**OLD CODE:**
```python
cur.execute("""
    SELECT ... FROM user_garments ug
    LEFT JOIN size_guide_entries sge ON ug.size_guide_entry_id = sge.id
    WHERE ug.id = %s AND sge.chest_min IS NOT NULL
""", (garment_id,))
```

**NEW CODE:**
```python
cur.execute("""
    SELECT 
        mt.display_name as measurement_type,
        CASE 
            WHEN m.min_value = m.max_value THEN m.min_value::text
            ELSE m.min_value::text || '-' || m.max_value::text
        END as measurement_value,
        m.unit,
        'size_guide' as measurement_source
    FROM garments g
    JOIN measurement_sets ms ON ms.garment_id = g.id
    JOIN measurements m ON m.set_id = ms.id
    JOIN measurement_types mt ON mt.code = m.measurement_type
    WHERE g.id = %s
    AND ms.scope = 'garment_spec'
    ORDER BY mt.sort_order
""", (garment_id,))
```

### 4. Update Multi-Dimensional Analyzer (multiple files)

All queries joining `size_guide_entries` need updating:

**OLD PATTERN:**
```python
LEFT JOIN size_guide_entries sge ON ug.size_guide_entry_id = sge.id
```

**NEW PATTERN:**
```python
-- First, update user_garments to store set_id instead of size_guide_entry_id
-- Then join through measurement_sets and measurements
LEFT JOIN measurement_sets ms ON ug.measurement_set_id = ms.id
LEFT JOIN measurements m ON m.set_id = ms.id
```

### 5. Use Materialized View for Performance

For analytics and fast lookups, use the new materialized view:

```python
cur.execute("""
    SELECT 
        brand_name,
        size_label,
        measurement_type,
        value_cm,  -- Auto-converted to CM
        value_in   -- Auto-converted to inches
    FROM fit_measurements
    WHERE brand_id = %s
    AND measurement_type = %s
    ORDER BY size_label
""", (brand_id, 'body_chest'))
```

## Migration Strategy

### Phase 1: Use Backward Compatibility Views (Quick Fix)
- Replace `size_guides_v2` with `size_guides_view`
- Replace `size_guide_entries` with `size_guide_entries_view`
- This will work immediately with minimal changes

### Phase 2: Update to New Structure (Recommended)
- Update queries to use `measurement_sets` and `measurements`
- Take advantage of the controlled vocabulary in `measurement_types`
- Use the materialized view for performance

### Phase 3: Clean Up
- Remove references to deprecated tables
- Update user_garments schema if needed
- Optimize queries using new indexes

## New Features Available

1. **Controlled Vocabulary:**
   ```python
   # Get human-readable measurement names
   SELECT code, display_name, description 
   FROM measurement_types 
   WHERE is_active = TRUE
   ```

2. **Dual Unit Support:**
   ```python
   # Automatic unit conversion in materialized view
   SELECT value_cm, value_in FROM fit_measurements
   ```

3. **Measurement Grouping:**
   ```python
   # Get all chest-related measurements
   SELECT * FROM measurements m
   JOIN measurement_types mt ON mt.code = m.measurement_type
   WHERE mt.measurement_point = 'chest'
   ```

## Testing Checklist

- [ ] Brand list endpoint works
- [ ] Size guide queries return data
- [ ] Garment measurements display correctly
- [ ] User measurements calculate properly
- [ ] Fit recommendations work
- [ ] Chat measurements feature works
- [ ] All dimension analyzers function

## Database Connection Update

No changes needed to connection parameters, but ensure error handling for:
- Missing `garment_id` column (removed)
- New NOT NULL constraints on `set_id`, `measurement_type`, `size_label`
- Foreign key to `measurement_types` table
