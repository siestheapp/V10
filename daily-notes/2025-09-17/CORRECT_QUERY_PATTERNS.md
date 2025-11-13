# V10 Database - Correct Query Patterns
> Quick reference to avoid schema errors

## ✅ ALWAYS USE THESE PATTERNS

### 1. Get User's Fit Feedback
```sql
SELECT 
    ugf.id,
    ugf.dimension,           -- 'chest', 'neck', 'sleeve', etc.
    ugf.feedback_code_id,    -- Links to feedback_codes table
    fc.description,          -- Actual feedback text
    ug.fit_feedback,         -- Overall fit (from user_garments)
    ug.size_label           -- Size worn (NOT size_purchased)
FROM user_garment_feedback ugf
JOIN user_garments ug ON ugf.user_garment_id = ug.id
LEFT JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
WHERE ug.user_id = ?
```

### 2. Get Product Info from User Garments
```sql
SELECT 
    ug.id,
    ug.size_label,           -- NOT size_purchased
    ug.fit_feedback,         -- Overall fit assessment
    pm.base_name,            -- NOT product_name
    pm.product_code,
    b.name as brand_name,    -- NOT b.brand_name
    pv.color_name,           -- NOT color
    pv.fit_option           -- NOT fit_type
FROM user_garments ug
LEFT JOIN product_master pm ON ug.product_master_id = pm.id
LEFT JOIN product_variants pv ON ug.product_variant_id = pv.id
LEFT JOIN brands b ON pm.brand_id = b.id
```

### 3. Link Feedback to Products
```sql
-- To link existing feedback to a product:
UPDATE user_garments 
SET 
    product_master_id = ?,   -- From product_master.id
    product_variant_id = ?    -- From product_variants.id
WHERE id = ?
```

### 4. Check if Product Exists
```sql
SELECT 
    pm.id as product_master_id,
    pv.id as product_variant_id,
    pm.base_name,
    pv.color_name,
    pv.fit_option
FROM product_master pm
LEFT JOIN product_variants pv ON pv.product_master_id = pm.id
WHERE pm.product_code = ? 
  AND pm.brand_id = ?  -- J.Crew=1, Reiss=10
```

## ❌ NEVER USE THESE (They Don't Exist)

### In user_garments:
- ❌ `brand_id` - Get via JOIN to product_master
- ❌ `product_code` - Get via JOIN to product_master  
- ❌ `garment_name` - Use product_master.base_name
- ❌ `category` - Get via JOIN to product_master
- ❌ `size_purchased` - Use `size_label` instead

### In user_garment_feedback:
- ❌ `feedback_type` - Use `dimension` instead
- ❌ `fit_assessment` - This is in user_garments.fit_feedback
- ❌ `overall_fit` - This is in user_garments.fit_feedback
- ❌ `rating`, `notes`, `comfort_rating` - Don't exist
- ❌ `feedback_date` - Use `created_at` instead

## 🔑 KEY FOREIGN KEYS

```
user_garments:
  user_id -> users.id
  product_master_id -> product_master.id  
  product_variant_id -> product_variants.id
  garment_id -> garments.id (old system)
  
user_garment_feedback:
  user_garment_id -> user_garments.id
  feedback_code_id -> feedback_codes.id
  
product_master:
  brand_id -> brands.id
  
product_variants:
  product_master_id -> product_master.id
  brand_id -> brands.id
```

## 📝 BRAND IDs
- J.Crew = 1
- Reiss = 10
- Uniqlo = 1 (check this)
- Banana Republic = 5
- Theory = 9

## 🚫 DEPRECATED/EMPTY TABLES (Don't Use)
- jcrew_backup_* (any backup tables)
- jcrew_test_results
- body_measurements (empty)
- brand_product_cache (empty)
- try_on_items (empty)
- try_on_sessions (empty) 
- user_preferences (empty)
