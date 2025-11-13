### Query Reference (from code usage)

Representative queries used by the app and scripts. These illustrate expected shapes and join patterns.

#### Products and Variants

```sql
-- Lookup or create product_master
SELECT id FROM product_master WHERE brand_id = $1 AND product_code = $2;

INSERT INTO product_master (
  brand_id, product_code, base_name, materials, pricing_data
) VALUES ($1, $2, $3, $4, $5)
RETURNING id;

-- Variants under a product_master
SELECT id FROM product_variants WHERE product_master_id = $1 AND color_name = $2 AND fit_option = $3;

INSERT INTO product_variants (
  product_master_id, color_name, fit_option, variant_code
) VALUES ($1, $2, $3, $4);

-- Aggregate variants with master
SELECT pm.id, pm.product_code, pm.base_name,
       COUNT(pv.id) as variant_count
FROM product_master pm
LEFT JOIN product_variants pv ON pm.id = pv.product_master_id
GROUP BY pm.id;
```

#### J.Crew Cache Flow

```sql
-- Insert/update cache rows
INSERT INTO jcrew_product_cache (
  product_url, product_code, product_name, product_image, fit_options
) VALUES ($1, $2, $3, $4, $5)
ON CONFLICT (product_code) DO UPDATE SET
  product_url = EXCLUDED.product_url,
  product_name = EXCLUDED.product_name,
  product_image = EXCLUDED.product_image,
  fit_options = EXCLUDED.fit_options;

-- Validate/cleanup operations
DELETE FROM jcrew_product_cache WHERE product_code = $1;
SELECT COUNT(*), COUNT(DISTINCT product_code) FROM jcrew_product_cache;
```

#### User Garments and Feedback

```sql
-- Create a user garment
INSERT INTO user_garments (
  user_id, brand_id, product_master_id, product_name, size_label, owns_garment
) VALUES ($1, $2, $3, $4, $5, $6)
RETURNING id;

-- Latest dimensional feedback via subqueries
SELECT
  ug.id,
  (SELECT fc.feedback_text FROM user_garment_feedback ugf JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id 
   WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'overall' ORDER BY ugf.created_at DESC LIMIT 1) as overall_feedback,
  (SELECT fc.feedback_text FROM user_garment_feedback ugf JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id 
   WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'chest' ORDER BY ugf.created_at DESC LIMIT 1) as chest_feedback
FROM user_garments ug
WHERE ug.user_id = $1;

-- Insert feedback using normalized codes
INSERT INTO user_garment_feedback (user_garment_id, dimension, feedback_code_id, created_at)
VALUES ($1, $2, $3, NOW())
RETURNING id;

-- Lookup a feedback code id by text
SELECT id FROM feedback_codes WHERE feedback_text = $1;
```

#### User Actions (audit/activity)

```sql
INSERT INTO user_actions (
  user_id, action_type, target_table, target_id, metadata, created_at
) VALUES ($1, $2, $3, $4, $5, NOW())
RETURNING id;

SELECT action_type, created_at FROM user_actions ORDER BY created_at DESC LIMIT 3;
```

#### Measurements

```sql
-- Legacy size guides (still used in some paths)
SELECT sge.* FROM size_guide_entries sge
JOIN size_guides sg ON sge.size_guide_id = sg.id
WHERE sg.brand_id = $1 AND sge.size_label = $2;

-- Preferred: measurement_sets + measurements (see key_tables)
-- Patterns align to fetching set context, then dimension/size entries.
```

Notes:
- Use `brands.name` lookups to resolve `brand_id` when needed.
- Subqueries are used heavily to get "latest feedback per dimension"; consider window functions for future optimization.



