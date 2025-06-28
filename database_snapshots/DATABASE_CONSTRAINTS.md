# DATABASE_CONSTRAINTS.md

This file summarizes key check constraints and allowed values for important tables in the `tailor2` database. Use this as a quick reference for SQL generation, migrations, and AI analysis.

---

## brands Table

- **default_unit:** Allowed values: `'in'`, `'cm'`
- **gender:** Allowed values: `'Men'`, `'Women'`, `'Unisex'`
- **measurement_type:** Allowed values: `'brand_level'`, `'product_level'`

**Source:** See `SCHEMA_20250628_001920.sql` for the full CREATE TABLE statement and all constraints.

---

## size_guides_v2 Table

- **Columns:**
  - brand, brand_id, gender, category, size_label, unit, data_quality
  - chest_min, chest_max
  - sleeve_min, sleeve_max
  - neck_min, neck_max
  - waist_min, waist_max
  - hip_min, hip_max
  - measurements_available (text[])
- **Check constraints:**
  - `chest_max >= chest_min`
  - `waist_max >= waist_min`
  - `sleeve_max >= sleeve_min`
  - `neck_max >= neck_min`
  - `hip_max >= hip_min`

**Sample Valid Insert:**
```sql
INSERT INTO size_guides_v2
(brand, brand_id, gender, category, size_label, chest_min, chest_max, waist_min, waist_max, unit)
VALUES
('Ted Baker', 16, 'Men', 'Menswear', 'XS', 34, 34, 28, 28, 'in'),
('Ted Baker', 16, 'Men', 'Menswear', 'S', 36, 36, 30, 30, 'in'),
('Ted Baker', 16, 'Men', 'Menswear', 'M', 38, 38, 32, 32, 'in'),
('Ted Baker', 16, 'Men', 'Menswear', 'L', 40, 40, 34, 34, 'in'),
('Ted Baker', 16, 'Men', 'Menswear', 'XL', 42, 42, 36, 36, 'in'),
('Ted Baker', 16, 'Men', 'Menswear', 'XXL', 44, 44, 38, 38, 'in'),
('Ted Baker', 16, 'Men', 'Menswear', 'XXXL', 46, 46, 40, 40, 'in');
```

**Source:** See `SCHEMA_20250628_001920.sql` for the full CREATE TABLE statement and all constraints.

---

## brand_automap Table

- **Columns:**
  - id (integer, primary key)
  - raw_term (text, not null): brand-specific/original term as it appears in the size guide
  - standardized_term (text, not null): standardized term used in the database
  - transform_factor (numeric, default 1): optional, for scaling/conversion
  - mapped_at (timestamp, default CURRENT_TIMESTAMP): when the mapping was created
  - brand_id (integer, FK to brands)
- **Unique constraint:** (brand_id, raw_term)
- **Foreign key:** brand_id references brands(id)

**Sample Valid Insert:**
```sql
INSERT INTO brand_automap (brand_id, raw_term, standardized_term)
VALUES (16, 'collar', 'neck');
```

**Purpose:**
- Use this table to track and standardize brand-specific terms for size guide ingestion.
- Example: Map 'collar' (Ted Baker) to 'neck' (database standard).

**Source:** See `SCHEMA_20250628_001920.sql` for the full CREATE TABLE statement and all constraints.

---

(Add other tables and constraints as needed) 