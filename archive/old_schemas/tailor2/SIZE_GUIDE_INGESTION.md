# Size Guide Ingestion Process

This document describes the step-by-step process for adding a new size guide (from any brand) to the database, ensuring all data is standardized and all constraints are respected.

---

## 1. Brand Check

- **Step 1:** Check if the brand exists in the `brands` table.
  ```sql
  SELECT id, name FROM brands WHERE LOWER(name) LIKE '%<brand_name>%';
  ```
- **Step 2:** If not found, insert the brand:
  ```sql
  INSERT INTO brands (name, measurement_type) VALUES ('<Brand Name>', '<brand_level|product_level>') RETURNING id;
  ```
  - Use allowed values for `measurement_type` (see `DATABASE_CONSTRAINTS.md`).

---

## 2. Column Mapping

- **Step 3:** Standardize the size guide columns to match the database schema.
  - Example: "collar" in the guide → "neck_min" and "neck_max" in the database.
  - Use the constraints file for required columns and allowed values.
  - If a column is missing in the guide, use NULL or omit if allowed.

---

## 3. SQL Insert

- **Step 4:** Prepare the SQL insert statement using the correct columns and values.
  - Use the "Sample Valid Insert" from the constraints file as a template.
  - Fill in all NOT NULL columns.
  - Example:
    ```sql
    INSERT INTO size_guides_v2
    (brand, brand_id, gender, category, size_label, chest_min, chest_max, neck_min, neck_max, waist_min, waist_max, unit)
    VALUES
    ('Brand', <brand_id>, 'Men', 'Menswear', 'M', 38, 38, 15.5, 15.5, 32, 32, 'in');
    ```

- **Step 5:** For every new brand-specific term mapping (e.g., "collar" → "neck"), also provide the corresponding `brand_automap` insert command:
  - Example:
    ```sql
    INSERT INTO brand_automap (brand_id, raw_term, standardized_term)
    VALUES (<brand_id>, '<original_term>', '<standardized_term>');
    ```
  - This ensures all new mappings are tracked and standardized for future ingestions.

---

## 4. Special Notes

- **Mapping:** "collar" (size guide) = "neck" (database)
- **Always include:** `brand`, `brand_id`, `gender`, `category`, `size_label`, `unit`
- **If a column is missing in the guide, use NULL or omit if allowed**
- **Check `DATABASE_CONSTRAINTS.md` for up-to-date required columns and valid values**

---

## 5. Example Workflow

1. Paste screenshot of Abercrombie Mens Tops size guide.
2. Check if "Abercrombie" is in the brands table.
3. If not, insert it and get the new `brand_id`.
4. Map all columns (e.g., "collar" → "neck").
5. Generate and run the SQL insert.

---

**See also:**  
- `DATABASE_CONSTRAINTS.md` for required columns and valid values  
- `SCHEMA_*.sql` for full schema details 