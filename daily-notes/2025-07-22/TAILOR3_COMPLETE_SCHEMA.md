# Tailor3 Database Schema - Complete Table Structure

## Database: tailor3 (Supabase)

**Connection Details:**
- Host: aws-0-us-east-2.pooler.supabase.com:6543
- Database: postgres
- User: postgres.lbilxlkchzpducggkrxx

---

## Table: `admin_activity_log`

**Columns:**
- `id` (integer) (NOT NULL) (DEFAULT: nextval('admin_activity_log_id_seq'::regclass))
- `admin_id` (integer)
- `action_type` (text) (NOT NULL)
- `table_name` (text)
- `record_id` (integer)
- `description` (text)
- `details` (jsonb)
- `created_at` (timestamp without time zone)

**Constraints:**
- PRIMARY KEY: `admin_activity_log_pkey` (btree) on `id`
- FOREIGN KEY: `admin_activity_log_admin_id_fkey` (`admin_id`) REFERENCES `admins(id)`

---

## Table: `admins`

**Columns:**
- `id` (integer) (NOT NULL) (DEFAULT: nextval('admins_id_seq'::regclass))
- `email` (text) (NOT NULL)
- `name` (text)
- `role` (text)
- `created_at` (timestamp without time zone)
- `notes` (text)

**Constraints:**
- PRIMARY KEY: `admins_pkey` (btree) on `id`
- UNIQUE: `admins_email_key` (btree) on `email`
- CHECK: `admins_role_check` CHECK (role = ANY (ARRAY['admin'::text, 'moderator'::text, 'contributor'::text]))

---

## Table: `body_measurements`

**Columns:**
- `id` (integer) (NOT NULL) (DEFAULT: nextval('body_measurements_id_seq'::regclass))
- `user_id` (integer)
- `chest` (numeric)
- `waist` (numeric)
- `neck` (numeric)
- `sleeve` (numeric)
- `hip` (numeric)
- `inseam` (numeric)
- `length` (numeric)
- `unit` (text)
- `confidence_score` (numeric)
- `notes` (text)
- `source` (text)
- `created_at` (timestamp without time zone)
- `updated_at` (timestamp without time zone)

**Constraints:**
- PRIMARY KEY: `body_measurements_pkey` (btree) on `id`
- FOREIGN KEY: `body_measurements_user_id_fkey` (`user_id`) REFERENCES `users(id)` ON DELETE CASCADE
- CHECK: `body_measurements_unit_check` CHECK (unit = ANY (ARRAY['in'::text, 'cm'::text]))

---

## Table: `brands`

**Columns:**
- `id` (integer) (NOT NULL) (DEFAULT: nextval('brands_id_seq'::regclass))
- `name` (text) (NOT NULL)
- `region` (text)
- `default_unit` (text)
- `created_at` (timestamp without time zone)
- `created_by` (integer)
- `updated_at` (timestamp without time zone)
- `updated_by` (integer)
- `notes` (text)

**Constraints:**
- PRIMARY KEY: `brands_pkey` (btree) on `id`
- UNIQUE: `brands_name_key` (btree) on `name`
- FOREIGN KEY: `brands_created_by_fkey` (`created_by`) REFERENCES `admins(id)`
- FOREIGN KEY: `brands_updated_by_fkey` (`updated_by`) REFERENCES `admins(id)`
- CHECK: `brands_default_unit_check` CHECK (default_unit = ANY (ARRAY['in'::text, 'cm'::text]))

---

## Table: `categories`

**Columns:**
- `id` (integer) (NOT NULL) (DEFAULT: nextval('categories_id_seq'::regclass))
- `name` (text) (NOT NULL)
- `description` (text)
- `created_at` (timestamp without time zone)
- `created_by` (integer)
- `updated_at` (timestamp without time zone)
- `updated_by` (integer)

**Constraints:**
- PRIMARY KEY: `categories_pkey` (btree) on `id`
- UNIQUE: `categories_name_key` (btree) on `name`
- FOREIGN KEY: `categories_created_by_fkey` (`created_by`) REFERENCES `admins(id)`
- FOREIGN KEY: `categories_updated_by_fkey` (`updated_by`) REFERENCES `admins(id)`

---

## Table: `feedback_codes`

**Columns:**
- `id` (integer) (NOT NULL) (DEFAULT: nextval('feedback_codes_id_seq'::regclass))
- `feedback_text` (text) (NOT NULL)
- `feedback_type` (text) (NOT NULL)
- `is_positive` (boolean)

**Constraints:**
- PRIMARY KEY: `feedback_codes_pkey` (btree) on `id`
- UNIQUE: `feedback_codes_feedback_text_key` (btree) on `feedback_text`
- CHECK: `feedback_codes_feedback_type_check` CHECK (feedback_type = ANY (ARRAY['fit'::text, 'length'::text, 'other'::text]))

---

## Table: `fit_zones`

**Columns:**
- `id` (integer) (NOT NULL) (DEFAULT: nextval('fit_zones_id_seq'::regclass))
- `user_id` (integer)
- `category_id` (integer)
- `subcategory_id` (integer)
- `dimension` (text) (NOT NULL)
- `fit_type` (text) (NOT NULL)
- `min_value` (numeric)
- `max_value` (numeric)
- `unit` (text)
- `range_text` (text)
- `notes` (text)
- `created_at` (timestamp without time zone)
- `updated_at` (timestamp without time zone)

**Constraints:**
- PRIMARY KEY: `fit_zones_pkey` (btree) on `id`
- FOREIGN KEY: `fit_zones_user_id_fkey` (`user_id`) REFERENCES `users(id)` ON DELETE CASCADE
- FOREIGN KEY: `fit_zones_category_id_fkey` (`category_id`) REFERENCES `categories(id)`
- FOREIGN KEY: `fit_zones_subcategory_id_fkey` (`subcategory_id`) REFERENCES `subcategories(id)`
- CHECK: `fit_zones_dimension_check` CHECK (dimension = ANY (ARRAY['chest'::text, 'waist'::text, 'neck'::text, 'sleeve'::text, 'hip'::text, 'length'::text]))
- CHECK: `fit_zones_fit_type_check` CHECK (fit_type = ANY (ARRAY['tight'::text, 'perfect'::text, 'relaxed'::text]))
- CHECK: `fit_zones_unit_check` CHECK (unit = ANY (ARRAY['in'::text, 'cm'::text]))

---

## Table: `measurement_instructions`

**Columns:**
- `id` (integer) (NOT NULL) (DEFAULT: nextval('measurement_instructions_id_seq'::regclass))
- `measurement_type` (text) (NOT NULL)
- `instructions` (text) (NOT NULL)
- `created_at` (timestamp without time zone)
- `created_by` (integer)
- `updated_at` (timestamp without time zone)
- `updated_by` (integer)

**Constraints:**
- PRIMARY KEY: `measurement_instructions_pkey` (btree) on `id`
- FOREIGN KEY: `measurement_instructions_created_by_fkey` (`created_by`) REFERENCES `admins(id)`
- FOREIGN KEY: `measurement_instructions_updated_by_fkey` (`updated_by`) REFERENCES `admins(id)`

---

## Table: `raw_size_guides`

**Columns:**
- `id` (integer) (NOT NULL) (DEFAULT: nextval('raw_size_guides_id_seq'::regclass))
- `brand_id` (integer)
- `gender` (text)
- `category_id` (integer)
- `subcategory_id` (integer)
- `fit_type` (text)
- `source_url` (text)
- `screenshot_path` (text)
- `raw_text` (text)
- `raw_table_json` (jsonb)
- `created_at` (timestamp without time zone)
- `uploaded_by` (integer)

**Constraints:**
- PRIMARY KEY: `raw_size_guides_pkey` (btree) on `id`
- FOREIGN KEY: `raw_size_guides_brand_id_fkey` (`brand_id`) REFERENCES `brands(id)` ON DELETE CASCADE
- FOREIGN KEY: `raw_size_guides_category_id_fkey` (`category_id`) REFERENCES `categories(id)`
- FOREIGN KEY: `raw_size_guides_subcategory_id_fkey` (`subcategory_id`) REFERENCES `subcategories(id)`
- FOREIGN KEY: `raw_size_guides_uploaded_by_fkey` (`uploaded_by`) REFERENCES `admins(id)`
- CHECK: `raw_size_guides_gender_check` CHECK (gender = ANY (ARRAY['Male'::text, 'Female'::text, 'Unisex'::text]))
- CHECK: `raw_size_guides_fit_type_check` CHECK (fit_type = ANY (ARRAY['Regular'::text, 'Slim'::text, 'Tall'::text]))

---

## Table: `size_guide_entries`

**Columns:**
- `id` (integer) (NOT NULL) (DEFAULT: nextval('size_guide_entries_id_seq'::regclass))
- `size_guide_id` (integer)
- `size_label` (text) (NOT NULL)
- `chest_min` (numeric)
- `chest_max` (numeric)
- `chest_range` (text)
- `waist_min` (numeric)
- `waist_max` (numeric)
- `waist_range` (text)
- `sleeve_min` (numeric)
- `sleeve_max` (numeric)
- `sleeve_range` (text)
- `neck_min` (numeric)
- `neck_max` (numeric)
- `neck_range` (text)
- `center_back_length` (numeric)
- `hip_min` (numeric)
- `hip_max` (numeric)
- `hip_range` (text)
- `notes` (text)
- `created_at` (timestamp without time zone)
- `created_by` (integer)
- `updated_at` (timestamp without time zone)
- `updated_by` (integer)

**Constraints:**
- PRIMARY KEY: `size_guide_entries_pkey` (btree) on `id`
- FOREIGN KEY: `size_guide_entries_size_guide_id_fkey` (`size_guide_id`) REFERENCES `size_guides(id)` ON DELETE CASCADE
- FOREIGN KEY: `size_guide_entries_created_by_fkey` (`created_by`) REFERENCES `admins(id)`
- FOREIGN KEY: `size_guide_entries_updated_by_fkey` (`updated_by`) REFERENCES `admins(id)`
- UNIQUE: `size_guide_entries_size_guide_id_size_label_key` (btree) on `size_guide_id`, `size_label`

---

## Table: `size_guides`

**Columns:**
- `id` (integer) (NOT NULL) (DEFAULT: nextval('size_guides_id_seq'::regclass))
- `brand_id` (integer)
- `gender` (text) (NOT NULL)
- `category_id` (integer)
- `subcategory_id` (integer)
- `fit_type` (text)
- `guide_level` (text)
- `version` (integer)
- `source_url` (text)
- `size_guide_header` (text)
- `notes` (text)
- `created_at` (timestamp without time zone)
- `created_by` (integer)
- `updated_at` (timestamp without time zone)
- `updated_by` (integer)
- `unit` (text)

**Constraints:**
- PRIMARY KEY: `size_guides_pkey` (btree) on `id`
- FOREIGN KEY: `size_guides_brand_id_fkey` (`brand_id`) REFERENCES `brands(id)` ON DELETE CASCADE
- FOREIGN KEY: `size_guides_category_id_fkey` (`category_id`) REFERENCES `categories(id)`
- FOREIGN KEY: `size_guides_subcategory_id_fkey` (`subcategory_id`) REFERENCES `subcategories(id)`
- FOREIGN KEY: `size_guides_created_by_fkey` (`created_by`) REFERENCES `admins(id)`
- FOREIGN KEY: `size_guides_updated_by_fkey` (`updated_by`) REFERENCES `admins(id)`
- CHECK: `size_guides_gender_check` CHECK (gender = ANY (ARRAY['Male'::text, 'Female'::text, 'Unisex'::text]))
- CHECK: `size_guides_fit_type_check` CHECK (fit_type = ANY (ARRAY['Regular'::text, 'Slim'::text, 'Tall'::text]))
- CHECK: `size_guides_guide_level_check` CHECK (guide_level = ANY (ARRAY['brand_level'::text, 'category_level'::text, 'product_level'::text]))
- CHECK: `size_guides_unit_check` CHECK (unit = ANY (ARRAY['in'::text, 'cm'::text]))
- UNIQUE: `size_guides_brand_id_gender_category_id_fit_type_version_key` (btree) on `brand_id`, `gender`, `category_id`, `fit_type`, `version`

---

## Table: `standardization_log`

**Columns:**
- `id` (integer) (NOT NULL) (DEFAULT: nextval('standardization_log_id_seq'::regclass))
- `brand_id` (integer)
- `original_term` (text) (NOT NULL)
- `standardized_term` (text) (NOT NULL)
- `source_table` (text)
- `notes` (text)
- `created_at` (timestamp without time zone)
- `created_by` (integer)

**Constraints:**
- PRIMARY KEY: `standardization_log_pkey` (btree) on `id`
- FOREIGN KEY: `standardization_log_brand_id_fkey` (`brand_id`) REFERENCES `brands(id)`
- FOREIGN KEY: `standardization_log_created_by_fkey` (`created_by`) REFERENCES `admins(id)`

---

## Table: `subcategories`

**Columns:**
- `id` (integer) (NOT NULL) (DEFAULT: nextval('subcategories_id_seq'::regclass))
- `category_id` (integer)
- `name` (text) (NOT NULL)
- `description` (text)
- `created_at` (timestamp without time zone)
- `created_by` (integer)
- `updated_at` (timestamp without time zone)
- `updated_by` (integer)

**Constraints:**
- PRIMARY KEY: `subcategories_pkey` (btree) on `id`
- FOREIGN KEY: `subcategories_category_id_fkey` (`category_id`) REFERENCES `categories(id)` ON DELETE CASCADE
- FOREIGN KEY: `subcategories_created_by_fkey` (`created_by`) REFERENCES `admins(id)`
- FOREIGN KEY: `subcategories_updated_by_fkey` (`updated_by`) REFERENCES `admins(id)`
- UNIQUE: `subcategories_category_id_name_key` (btree) on `category_id`, `name`

---

## Table: `user_garment_feedback`

**Columns:**
- `id` (integer) (NOT NULL) (DEFAULT: nextval('user_garment_feedback_id_seq'::regclass))
- `user_garment_id` (integer)
- `dimension` (text) (NOT NULL)
- `feedback_code_id` (integer)
- `created_at` (timestamp without time zone)
- `created_by` (integer)

**Constraints:**
- PRIMARY KEY: `user_garment_feedback_pkey` (btree) on `id`
- FOREIGN KEY: `user_garment_feedback_created_by_fkey` (`created_by`) REFERENCES `admins(id)`
- FOREIGN KEY: `user_garment_feedback_feedback_code_id_fkey` (`feedback_code_id`) REFERENCES `feedback_codes(id)`
- FOREIGN KEY: `user_garment_feedback_user_garment_id_fkey` (`user_garment_id`) REFERENCES `user_garments(id)` ON DELETE CASCADE
- CHECK: `user_garment_feedback_dimension_check` CHECK (dimension = ANY (ARRAY['overall'::text, 'chest'::text, 'waist'::text, 'sleeve'::text, 'neck'::text, 'hip'::text, 'length'::text]))

---

## Table: `user_garments`

**Columns:**
- `id` (integer) (NOT NULL) (DEFAULT: nextval('user_garments_id_seq'::regclass))
- `user_id` (integer)
- `brand_id` (integer)
- `category_id` (integer)
- `subcategory_id` (integer)
- `gender` (text)
- `size_label` (text) (NOT NULL)
- `fit_type` (text)
- `unit` (text)
- `product_name` (text)
- `product_url` (text)
- `product_code` (text)
- `tag_photo_path` (text)
- `owns_garment` (boolean)
- `size_guide_id` (integer)
- `size_guide_entry_id` (integer)
- `fit_feedback` (text)
- `feedback_timestamp` (timestamp without time zone)
- `notes` (text)
- `created_at` (timestamp without time zone)
- `created_by` (integer)
- `updated_at` (timestamp without time zone)
- `updated_by` (integer)

**Constraints:**
- PRIMARY KEY: `user_garments_pkey` (btree) on `id`
- FOREIGN KEY: `user_garments_brand_id_fkey` (`brand_id`) REFERENCES `brands(id)`
- FOREIGN KEY: `user_garments_category_id_fkey` (`category_id`) REFERENCES `categories(id)`
- FOREIGN KEY: `user_garments_created_by_fkey` (`created_by`) REFERENCES `admins(id)`
- FOREIGN KEY: `user_garments_size_guide_entry_id_fkey` (`size_guide_entry_id`) REFERENCES `size_guide_entries(id)`
- FOREIGN KEY: `user_garments_size_guide_id_fkey` (`size_guide_id`) REFERENCES `size_guides(id)`
- FOREIGN KEY: `user_garments_subcategory_id_fkey` (`subcategory_id`) REFERENCES `subcategories(id)`
- FOREIGN KEY: `user_garments_updated_by_fkey` (`updated_by`) REFERENCES `admins(id)`
- FOREIGN KEY: `user_garments_user_id_fkey` (`user_id`) REFERENCES `users(id)` ON DELETE CASCADE
- CHECK: `user_garments_fit_type_check` CHECK (fit_type = ANY (ARRAY['Regular'::text, 'Slim'::text, 'Tall'::text, 'NA'::text]))
- CHECK: `user_garments_gender_check` CHECK (gender = ANY (ARRAY['Male'::text, 'Female'::text, 'Unisex'::text]))
- CHECK: `user_garments_unit_check` CHECK (unit = ANY (ARRAY['in'::text, 'cm'::text]))

---

## Table: `users`

**Columns:**
- `id` (integer) (NOT NULL) (DEFAULT: nextval('users_id_seq'::regclass))
- `email` (text) (NOT NULL)
- `created_at` (timestamp without time zone)
- `updated_at` (timestamp without time zone)
- `gender` (text) (NOT NULL)
- `height_in` (numeric)
- `preferred_units` (text)
- `notes` (text)

**Constraints:**
- PRIMARY KEY: `users_pkey` (btree) on `id`
- UNIQUE: `users_email_key` (btree) on `email`
- CHECK: `users_gender_check` CHECK (gender = ANY (ARRAY['Male'::text, 'Female'::text, 'Unisex'::text]))
- CHECK: `users_preferred_units_check` CHECK (preferred_units = ANY (ARRAY['in'::text, 'cm'::text]))

---

## Views

### `size_guide_entries_with_brand`
- Joins size guide entries with brand information

### `user_garments_simple`
- Basic user garments view with essential information

### `user_garments_actual_feedback`
- Detailed view showing only feedback dimensions that actually exist

### `user_garments_feedback_summary`
- Statistics view showing feedback counts and analytics

---

## Key Constraints Summary

### Check Constraints
- **Gender values**: 'Male', 'Female', 'Unisex'
- **Unit values**: 'in', 'cm'
- **Fit types**: 'Regular', 'Slim', 'Tall', 'NA' (for garments/guides), 'tight', 'perfect', 'relaxed' (for fit zones)
- **Feedback types**: 'fit', 'length', 'other'
- **Admin roles**: 'admin', 'moderator', 'contributor'
- **Guide levels**: 'brand_level', 'category_level', 'product_level'
- **Feedback dimensions**: 'overall', 'chest', 'waist', 'sleeve', 'neck', 'hip', 'length'

### Unique Constraints
- **Brands:** `name` must be unique
- **Categories:** `name` must be unique  
- **Subcategories:** `(category_id, name)` combination must be unique
- **Size Guides:** `(brand_id, gender, category_id, fit_type, version)` combination must be unique
- **Size Guide Entries:** `(size_guide_id, size_label)` combination must be unique
- **Users:** `email` must be unique
- **Admins:** `email` must be unique
- **Feedback Codes:** `feedback_text` must be unique

### Foreign Key Relationships
- All user-related tables cascade delete when user is deleted
- Size guide entries cascade delete when size guide is deleted
- Subcategories cascade delete when category is deleted
- Raw size guides cascade delete when brand is deleted
- All admin-created content references admin users for audit trail

