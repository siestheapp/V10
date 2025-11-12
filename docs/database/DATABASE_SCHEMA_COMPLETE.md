# V10 Database Schema Documentation

> **Last Updated**: September 17, 2025  
> **Database**: PostgreSQL (Supabase)  
> **Connection**: Use `DB_CONFIG` from `db_config.py`

## Critical Tables for Product Management

### 1. `brands` Table
Primary table for brand information.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| **id** | integer | NO | nextval | Primary key |
| name | text | YES | | Brand name (e.g., 'J.Crew', 'Reiss') |
| region | text | YES | | Region code (e.g., 'US') |
| default_unit | text | YES | | Default measurement unit ('in', 'cm') |
| created_at | timestamp | YES | | |
| created_by | integer | YES | | |
| updated_at | timestamp | YES | | |
| updated_by | integer | YES | | |
| notes | text | YES | | |
| original_measurement_unit | text | YES | | |

**Key Points:**
- Use `name` not `brand_name` when querying
- J.Crew has id=1, Reiss has id=10

---

### 2. `product_master` Table
Master product records - one per unique product code.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| **id** | integer | NO | nextval | Primary key |
| brand_id | integer | YES | | Foreign key to brands.id |
| product_code | varchar(50) | YES | | Unique product identifier (e.g., 'BE996', 'D43750') |
| base_name | text | YES | | Full product name |
| materials | jsonb | YES | | Material composition |
| care_instructions | text[] | YES | | Array of care instructions |
| construction_details | jsonb | YES | | Construction details |
| technical_features | text[] | YES | | Technical features array |
| sustainability | jsonb | YES | | Sustainability info |
| description_texts | text[] | YES | | Product descriptions |
| styling_notes | text[] | YES | | Styling suggestions |
| product_details | text[] | YES | | Additional details |
| fit_information | jsonb | YES | | Fit details JSON |
| measurements_guide | jsonb | YES | | Measurement guide |
| category_id | integer | YES | | Category reference |
| subcategory_id | integer | YES | | Subcategory reference |
| created_at | timestamp | YES | | |
| updated_at | timestamp | YES | | |
| last_scraped | timestamp | YES | | Last scrape time |
| product_ratings | jsonb | YES | | Ratings data |
| fit_feedback | jsonb | YES | | Fit feedback |
| pricing_data | jsonb | YES | | Pricing information |
| fabric_technology | text[] | YES | | Fabric tech features |

**Important Notes:**
- No `product_name`, `style_family`, or `base_price` columns
- Use `base_name` for product name
- Use `pricing_data` JSONB for price information
- Use `fit_information` JSONB for fit details

---

### 3. `product_variants` Table
Individual SKUs/variants - colors, fits, etc.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| **id** | integer | NO | nextval | Primary key (not variant_id!) |
| product_master_id | integer | YES | | Foreign key to product_master.id |
| brand_id | integer | YES | | Brand ID (denormalized) |
| sku | varchar(100) | YES | | SKU identifier |
| variant_code | varchar(50) | YES | | Variant-specific code |
| color_name | varchar(100) | YES | | Color name (not 'color'!) |
| color_code | varchar(50) | YES | | Color code |
| color_hex | varchar(7) | YES | | Hex color value |
| color_swatch_url | text | YES | | Swatch image URL |
| color_family | varchar(50) | YES | | Color family |
| fit_option | varchar(50) | YES | | Fit type (not 'fit_type'!) |
| current_price | numeric(10,2) | YES | | Current price |
| original_price | numeric(10,2) | YES | | Original price |
| sale_percentage | integer | YES | | Discount percentage |
| currency | varchar(3) | YES | 'USD' | Currency code |
| in_stock | boolean | YES | true | Stock status |
| sizes_available | text[] | YES | | Array of available sizes |
| sizes_in_stock | text[] | YES | | Array of in-stock sizes |
| images | jsonb | YES | | Image URLs JSON |
| variant_url | text | YES | | Product URL |
| last_checked | timestamp | YES | | Last check time |
| availability_status | varchar(50) | YES | | Availability status |
| created_at | timestamp | YES | CURRENT_TIMESTAMP | |
| updated_at | timestamp | YES | CURRENT_TIMESTAMP | |

**Critical Column Names:**
- Use `color_name` NOT `color`
- Use `fit_option` NOT `fit_type`
- Use `sizes_available` NOT `sizes`
- Use `current_price` NOT `price`
- Primary key is `id` NOT `variant_id`

---

### 4. `jcrew_product_cache` Table
J.Crew specific product cache.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| **id** | integer | NO | nextval | Primary key |
| product_code | varchar(20) | NO | | Product code |
| product_data | jsonb | YES | | Full product data |
| scraped_at | timestamp | YES | CURRENT_TIMESTAMP | |
| url | text | YES | | Product URL |
| category | varchar(100) | YES | | Category |
| subcategory | varchar(100) | YES | | Subcategory |

**Constraints:**
- UNIQUE on product_code

---

## User and Garment Tables

### 5. `users` Table
| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| **id** | integer | NO | nextval |
| email | varchar(255) | NO | |
| username | varchar(50) | YES | |
| created_at | timestamp | YES | CURRENT_TIMESTAMP |
| last_login | timestamp | YES | |
| preferences | jsonb | YES | |
| profile_data | jsonb | YES | |

### 6. `user_garments` Table
| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| **id** | integer | NO | nextval |
| user_id | integer | NO | |
| brand_id | integer | YES | |
| product_code | varchar(50) | YES | |
| garment_name | text | YES | |
| category | varchar(100) | YES | |
| size_purchased | varchar(20) | YES | |
| fit_feedback | jsonb | YES | |
| measurements | jsonb | YES | |
| created_at | timestamp | YES | CURRENT_TIMESTAMP |
| updated_at | timestamp | YES | |

### 7. `user_garment_feedback` Table
| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| **id** | integer | NO | nextval |
| user_garment_id | integer | NO | |
| feedback_date | timestamp | YES | CURRENT_TIMESTAMP |
| overall_fit | varchar(50) | YES | |
| specific_feedback | jsonb | YES | |
| wear_context | varchar(100) | YES | |
| comfort_rating | integer | YES | |
| would_recommend | boolean | YES | |

---

## Size Guide Tables

### 8. `size_guides` Table
| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| **id** | integer | NO | nextval |
| brand_id | integer | YES | |
| category | varchar(100) | YES | |
| subcategory | varchar(100) | YES | |
| guide_name | varchar(255) | YES | |
| created_at | timestamp | YES | CURRENT_TIMESTAMP |
| updated_at | timestamp | YES | |

### 9. `size_guide_entries` Table
| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| **id** | integer | NO | nextval |
| guide_id | integer | YES | |
| size_label | varchar(20) | YES | |
| measurements | jsonb | YES | |
| size_order | integer | YES | |

---

## Common Query Patterns

### Get all products for a brand:
```sql
SELECT pm.*, pv.*
FROM product_master pm
JOIN product_variants pv ON pm.id = pv.product_master_id
WHERE pm.brand_id = (SELECT id FROM brands WHERE name = 'Reiss');
```

### Insert new Reiss product:
```sql
-- 1. Insert into product_master
INSERT INTO product_master (
    brand_id, product_code, base_name,
    fit_information, pricing_data,
    created_at, updated_at, last_scraped
) VALUES (
    10, 'PRODUCT_CODE', 'Product Name',
    '{"fit_type": "slim"}', '{"base_price": 155, "currency": "USD"}',
    NOW(), NOW(), NOW()
) RETURNING id;

-- 2. Insert into product_variants
INSERT INTO product_variants (
    product_master_id, brand_id, sku, variant_code,
    color_name, fit_option,
    current_price, original_price, currency,
    sizes_available, in_stock, images, variant_url,
    created_at, updated_at, last_checked
) VALUES (
    <master_id>, 10, 'SKU', 'VARIANT_CODE',
    'Navy', 'Slim',
    155.00, 155.00, 'USD',
    ARRAY['S', 'M', 'L', 'XL'], true, '{"main": "url"}', 'product_url',
    NOW(), NOW(), NOW()
) RETURNING id;
```

### Check if product exists:
```sql
SELECT id FROM product_master 
WHERE product_code = 'PRODUCT_CODE' AND brand_id = 10;
```

---

## Important Reminders

### Column Name Gotchas:
- ❌ `product_master.product_master_id` → ✅ `product_master.id`
- ❌ `product_variants.variant_id` → ✅ `product_variants.id`
- ❌ `product_variants.color` → ✅ `product_variants.color_name`
- ❌ `product_variants.fit_type` → ✅ `product_variants.fit_option`
- ❌ `product_variants.sizes` → ✅ `product_variants.sizes_available`
- ❌ `product_variants.price` → ✅ `product_variants.current_price`
- ❌ `brands.brand_name` → ✅ `brands.name`
- ❌ `brands.brand_id` → ✅ `brands.id`

### Database Connection:
```python
import psycopg2
from db_config import DB_CONFIG

conn = psycopg2.connect(**DB_CONFIG)
cursor = conn.cursor()
# Always use %s placeholders, never f-strings for queries!
cursor.execute("SELECT * FROM brands WHERE name = %s", ('Reiss',))
```

### Brand IDs:
- J.Crew: 1
- Banana Republic: 2
- Theory: 3
- Everlane: 4
- Bonobos: 5
- Buck Mason: 6
- Outerknown: 7
- Taylor Stitch: 8
- Asket: 9
- Reiss: 10

---

## Index Information

### product_master indexes:
- PRIMARY KEY on id
- INDEX on brand_id
- INDEX on product_code
- UNIQUE on (brand_id, product_code)

### product_variants indexes:
- PRIMARY KEY on id
- INDEX on product_master_id
- INDEX on sku
- INDEX on variant_code

---

## Notes

1. **JSONB Columns**: Many columns use JSONB for flexibility. Always use `json.dumps()` when inserting Python dicts.

2. **Array Columns**: PostgreSQL arrays are used for sizes, care instructions, etc. Pass Python lists directly.

3. **Timestamps**: Most tables have created_at/updated_at. Use `NOW()` in SQL or `datetime.now()` in Python.

4. **Foreign Keys**: Always check parent record exists before inserting child records.

5. **Transactions**: Use transactions for multi-table inserts to maintain consistency.

---

*This document should be the single source of truth for database schema. Update it whenever schema changes are made.*
