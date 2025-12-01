# Database Schema Guide - Size Guides & Measurements

## ⚠️ CRITICAL: Current vs Deprecated Schema

### ✅ **CURRENT SCHEMA (USE THESE TABLES)**

#### 1. `measurement_sets` - Main size guide container
```sql
-- Example: Adding a new fit type for a brand
INSERT INTO measurement_sets (
    brand_id, category_id, gender, fit_type, scope, unit,
    header, notes, is_active, created_at, updated_at
) VALUES (
    4,              -- J.Crew brand_id
    1,              -- Tops category_id  
    'male',         -- gender
    'tall',         -- fit_type
    'size_guide',   -- scope (REQUIRED for size guides)
    'in',           -- unit
    'Mens Tops - Tall Fit',
    '2 inches longer sleeves than regular',
    true,           -- is_active
    NOW(), NOW()
);
```

**Key Constraints:**
- `scope = 'size_guide'` AND `garment_id = NULL` (enforced by constraint)
- `brand_id` and `category_id` are required
- `fit_type` differentiates between Regular, Slim, Tall, etc.

#### 2. `measurements` - Individual size measurements
```sql
-- Example: Adding measurements for each size
INSERT INTO measurements (
    set_id,              -- From measurement_sets.id
    brand_id,            -- Same as measurement_set
    size_label,          -- 'S', 'M', 'L', etc.
    measurement_type,    -- 'body_chest', 'body_sleeve', etc.
    min_value,           -- 35.0
    max_value,           -- 37.0
    unit,                -- 'in'
    source_type,         -- 'size_guide'
    created_at, created_by
) VALUES (...);
```

**Auto-Generated Fields (DO NOT INSERT):**
- `measurement_category` - Auto-generated from `measurement_type` prefix
- `range_text` - Auto-generated from min/max values (e.g., "35-37")
- `midpoint_value` - Auto-calculated average

---

### ❌ **DEPRECATED SCHEMA (DO NOT USE)**

These tables contain legacy data but should **NOT** be used for new entries:

- `size_guides` - **DEPRECATED** (10 legacy rows)
- `size_guide_entries` - **DEPRECATED** (67 legacy rows)  
- `sizes` - **DOES NOT EXIST**

**Why deprecated?**
- Old schema design
- Missing modern features (fit types, better constraints)
- Not integrated with current measurement system

---

## 🔄 **Correct Workflow for Adding Size Guides**

### Step 1: Create Measurement Set
```python
# Check existing sets first
cur.execute("""
    SELECT id, fit_type FROM measurement_sets 
    WHERE brand_id = %s AND category_id = %s
""", (brand_id, category_id))

# Add new measurement set
cur.execute("""
    INSERT INTO measurement_sets (
        brand_id, category_id, gender, fit_type, scope, unit,
        header, notes, is_active, created_at, updated_at
    ) VALUES (%s, %s, %s, %s, 'size_guide', %s, %s, %s, true, NOW(), NOW())
    RETURNING id
""", (brand_id, category_id, gender, fit_type, unit, header, notes))

set_id = cur.fetchone()[0]
```

### Step 2: Add Measurements for Each Size
```python
# For each size (S, M, L, XL, etc.)
for size_data in size_measurements:
    size_label, chest_min, chest_max, neck_min, neck_max, ... = size_data
    
    # Add each measurement type
    measurements = [
        ('body_chest', chest_min, chest_max),
        ('body_neck', neck_min, neck_max),
        ('body_waist', waist_min, waist_max),
        ('body_sleeve', sleeve_min, sleeve_max)
    ]
    
    for measurement_type, min_val, max_val in measurements:
        cur.execute("""
            INSERT INTO measurements (
                set_id, brand_id, size_label, measurement_type,
                min_value, max_value, unit, source_type,
                created_at, created_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s)
        """, (set_id, brand_id, size_label, measurement_type,
              min_val, max_val, unit, 'size_guide', user_id))
```

---

## 🛡️ **Safeguards & Best Practices**

### 1. Always Check Current Schema First
```python
# Before adding size guides, verify current structure
cur.execute("SELECT COUNT(*) FROM measurement_sets WHERE brand_id = %s", (brand_id,))
existing_count = cur.fetchone()[0]
print(f"Brand has {existing_count} existing measurement sets")
```

### 2. Use Proper Constraint Values
- `scope = 'size_guide'` (not 'brand_category_fit' or other values)
- `garment_id = NULL` for size guides
- `source_type = 'size_guide'` in measurements table

### 3. Measurement Type Naming Convention
- **Body measurements:** `body_chest`, `body_neck`, `body_sleeve`, `body_waist`
- **Garment measurements:** `garment_chest`, `garment_length`, etc.
- Prefix determines auto-generated `measurement_category`

### 4. Generated Columns
Never insert into these columns (they're auto-calculated):
- `measurement_category`
- `range_text` 
- `midpoint_value`

---

## 📊 **Current Brand Status**

### J.Crew (brand_id: 4)
- ✅ **Regular fit:** measurement_sets ID 26 & 7 (28 measurements each)
- ✅ **Tall fit:** measurement_sets ID 28 (24 measurements)
- **Supported categories:** Tops (category_id: 1)
- **Unit:** inches (in)

### Adding New Brands
1. Ensure brand exists in `brands` table
2. Check `categories` table for appropriate category_id
3. Follow the measurement_sets → measurements workflow above

---

## 🚨 **Emergency Recovery**

If you accidentally add to deprecated tables:

```sql
-- Remove from deprecated size_guides
DELETE FROM size_guides WHERE id = [incorrect_id];

-- Remove from deprecated size_guide_entries  
DELETE FROM size_guide_entries WHERE size_guide_id = [incorrect_id];

-- Then follow correct workflow above
```

---

**Last Updated:** September 12, 2025  
**Schema Version:** measurement_sets/measurements (current)  
**Deprecated Since:** [Unknown - legacy tables still contain data]

