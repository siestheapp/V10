# V10 Database Schema Documentation (tailor3)

## Overview
This document describes the complete database schema for the V10 app (tailor3), including tables, relationships, and data structures. This schema is more normalized and scalable than tailor2, supporting richer ingestion, analytics, and future expansion.

## Database: `tailor3` (PostgreSQL)

---

### Core Tables

#### `users`
- `id` (SERIAL PRIMARY KEY)
- `email` (TEXT, UNIQUE, NOT NULL)
- `created_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
- `updated_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
- `gender` (TEXT, CHECK: 'Male', 'Female', 'Unisex', NOT NULL)
- `height_in` (NUMERIC)
- `preferred_units` (TEXT, CHECK: 'in', 'cm', DEFAULT 'in')
- `notes` (TEXT)

#### `admins`
- `id` (SERIAL PRIMARY KEY)
- `email` (TEXT, UNIQUE, NOT NULL)
- `name` (TEXT)
- `role` (TEXT, CHECK: 'admin', 'moderator', 'contributor', DEFAULT 'contributor')
- `created_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
- `notes` (TEXT)

#### `body_measurements`
- `id` (SERIAL PRIMARY KEY)
- `user_id` (INTEGER, REFERENCES users(id) ON DELETE CASCADE)
- `chest`, `waist`, `neck`, `sleeve`, `hip`, `inseam`, `length` (NUMERIC)
- `unit` (TEXT, CHECK: 'in', 'cm', DEFAULT 'in')
- `confidence_score` (NUMERIC)
- `notes` (TEXT)
- `source` (TEXT)
- `created_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
- `updated_at` (TIMESTAMP)

---

### Catalog & Ingestion Tables

#### `brands`
- `id` (SERIAL PRIMARY KEY)
- `name` (TEXT, UNIQUE, NOT NULL)
- `region` (TEXT)
- `default_unit` (TEXT, CHECK: 'in', 'cm', DEFAULT 'in')
- `created_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
- `created_by` (INTEGER, REFERENCES admins(id))
- `updated_at` (TIMESTAMP)
- `updated_by` (INTEGER, REFERENCES admins(id))
- `notes` (TEXT)

#### `categories`
- `id` (SERIAL PRIMARY KEY)
- `name` (TEXT, UNIQUE, NOT NULL)
- `description` (TEXT)
- `created_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
- `created_by` (INTEGER, REFERENCES admins(id))
- `updated_at` (TIMESTAMP)
- `updated_by` (INTEGER, REFERENCES admins(id))

#### `subcategories`
- `id` (SERIAL PRIMARY KEY)
- `category_id` (INTEGER, REFERENCES categories(id) ON DELETE CASCADE)
- `name` (TEXT, NOT NULL)
- `description` (TEXT)
- `created_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
- `created_by` (INTEGER, REFERENCES admins(id))
- `updated_at` (TIMESTAMP)
- `updated_by` (INTEGER, REFERENCES admins(id))
- **Unique:** (`category_id`, `name`)

#### `size_guides`
- `id` (SERIAL PRIMARY KEY)
- `brand_id` (INTEGER, REFERENCES brands(id) ON DELETE CASCADE)
- `gender` (TEXT, CHECK: 'Male', 'Female', 'Unisex', NOT NULL)
- `category_id` (INTEGER, REFERENCES categories(id))
- `subcategory_id` (INTEGER, REFERENCES subcategories(id))
- `fit_type` (TEXT, CHECK: 'Regular', 'Slim', 'Tall', DEFAULT 'Regular')
- `guide_level` (TEXT, CHECK: 'brand_level', 'category_level', 'product_level', DEFAULT 'brand_level')
- `version` (INTEGER, DEFAULT 1)
- `source_url` (TEXT)
- `size_guide_header` (TEXT)
- `notes` (TEXT)
- `created_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
- `created_by` (INTEGER, REFERENCES admins(id))
- `updated_at` (TIMESTAMP)
- `updated_by` (INTEGER, REFERENCES admins(id))
- `unit` (TEXT, CHECK: 'in', 'cm', DEFAULT 'in')
- **Unique:** (`brand_id`, `gender`, `category_id`, `fit_type`, `version`)

#### `size_guide_entries`
- `id` (SERIAL PRIMARY KEY)
- `size_guide_id` (INTEGER, REFERENCES size_guides(id) ON DELETE CASCADE)
- `size_label` (TEXT, NOT NULL)
- `chest_min`, `chest_max` (NUMERIC)
- `chest_range` (TEXT)
- `waist_min`, `waist_max` (NUMERIC)
- `waist_range` (TEXT)
- `sleeve_min`, `sleeve_max` (NUMERIC)
- `sleeve_range` (TEXT)
- `neck_min`, `neck_max` (NUMERIC)
- `neck_range` (TEXT)
- `center_back_length` (NUMERIC)
- `hip_min`, `hip_max` (NUMERIC)
- `hip_range` (TEXT)
- `notes` (TEXT)
- `created_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
- `created_by` (INTEGER, REFERENCES admins(id))
- `updated_at` (TIMESTAMP)
- `updated_by` (INTEGER, REFERENCES admins(id))
- **Unique:** (`size_guide_id`, `size_label`)

#### `raw_size_guides`
- `id` (SERIAL PRIMARY KEY)
- `brand_id` (INTEGER, REFERENCES brands(id) ON DELETE CASCADE)
- `gender` (TEXT, CHECK: 'Male', 'Female', 'Unisex')
- `category_id` (INTEGER, REFERENCES categories(id))
- `subcategory_id` (INTEGER, REFERENCES subcategories(id))
- `fit_type` (TEXT, CHECK: 'Regular', 'Slim', 'Tall', DEFAULT 'Regular')
- `source_url` (TEXT)
- `screenshot_path` (TEXT)
- `raw_text` (TEXT)
- `raw_table_json` (JSONB)
- `created_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
- `uploaded_by` (INTEGER, REFERENCES admins(id))

#### `standardization_log`
- `id` (SERIAL PRIMARY KEY)
- `brand_id` (INTEGER, REFERENCES brands(id))
- `original_term` (TEXT, NOT NULL)
- `standardized_term` (TEXT, NOT NULL)
- `source_table` (TEXT)
- `notes` (TEXT)
- `created_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
- `created_by` (INTEGER, REFERENCES admins(id))

---

### User Garment & Feedback Tables

#### `user_garments`
- `id` (SERIAL PRIMARY KEY)
- `user_id` (INTEGER, REFERENCES users(id) ON DELETE CASCADE)
- `brand_id` (INTEGER, REFERENCES brands(id))
- `category_id` (INTEGER, REFERENCES categories(id))
- `subcategory_id` (INTEGER, REFERENCES subcategories(id))
- `gender` (TEXT, CHECK: 'Male', 'Female', 'Unisex')
- `size_label` (TEXT, NOT NULL)
- `fit_type` (TEXT, CHECK: 'Regular', 'Slim', 'Tall', DEFAULT 'Regular')
- `unit` (TEXT, CHECK: 'in', 'cm', DEFAULT 'in')
- `product_name` (TEXT)
- `product_url` (TEXT)
- `product_code` (TEXT)
- `tag_photo_path` (TEXT)
- `owns_garment` (BOOLEAN, DEFAULT true)
- `size_guide_id` (INTEGER, REFERENCES size_guides(id))
- `size_guide_entry_id` (INTEGER, REFERENCES size_guide_entries(id))
- `fit_feedback` (TEXT)
- `feedback_timestamp` (TIMESTAMP)
- `notes` (TEXT)
- `created_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
- `created_by` (INTEGER, REFERENCES admins(id))
- `updated_at` (TIMESTAMP)
- `updated_by` (INTEGER, REFERENCES admins(id))

#### `user_garment_feedback`
- `id` (SERIAL PRIMARY KEY)
- `user_garment_id` (INTEGER, REFERENCES user_garments(id) ON DELETE CASCADE)
- `dimension` (TEXT, CHECK: 'overall', 'chest', 'waist', 'sleeve', 'neck', 'hip', 'length', NOT NULL)
- `feedback_code_id` (INTEGER, REFERENCES feedback_codes(id))
- `created_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
- `created_by` (INTEGER, REFERENCES admins(id))

#### `feedback_codes`
- `id` (SERIAL PRIMARY KEY)
- `feedback_text` (TEXT, UNIQUE, NOT NULL)
- `feedback_type` (TEXT, CHECK: 'fit', 'length', 'other', NOT NULL)
- `is_positive` (BOOLEAN)

---

### Fit & Analytics Tables

#### `fit_zones`
- `id` (SERIAL PRIMARY KEY)
- `user_id` (INTEGER, REFERENCES users(id) ON DELETE CASCADE)
- `category_id` (INTEGER, REFERENCES categories(id))
- `subcategory_id` (INTEGER, REFERENCES subcategories(id))
- `dimension` (TEXT, CHECK: 'chest', 'waist', 'neck', 'sleeve', 'hip', 'length', NOT NULL)
- `fit_type` (TEXT, CHECK: 'tight', 'perfect', 'relaxed', NOT NULL)
- `min_value` (NUMERIC)
- `max_value` (NUMERIC)
- `unit` (TEXT, CHECK: 'in', 'cm', DEFAULT 'in')
- `range_text` (TEXT)
- `notes` (TEXT)
- `created_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
- `updated_at` (TIMESTAMP)

---

## Key Schema Features

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

### Check Constraints
- Gender values: 'Male', 'Female', 'Unisex'
- Unit values: 'in', 'cm'
- Fit types: 'Regular', 'Slim', 'Tall' (for garments/guides), 'tight', 'perfect', 'relaxed' (for fit zones)
- Feedback types: 'fit', 'length', 'other'
- Admin roles: 'admin', 'moderator', 'contributor'
- Guide levels: 'brand_level', 'category_level', 'product_level'

---

## Known Issues & Limitations
- Some measurement types (e.g., shoulder, rise) not yet supported in all tables
- No historical tracking of measurement changes (except via snapshot scripts)
- Analytics tables are minimal; more user behavior tracking may be needed
- Size standardization is ongoing; mappings may be incomplete for some brands

## Future Improvements Needed
- Add more measurement types and garment attributes as needed
- Expand analytics and user event tracking
- Automate ingestion and mapping workflows
- Add audit/history tables for key entities
- Continue to normalize and modularize as new use cases arise

---

*Schema based on: `supabase/tailor3_schema_2025-06-29_231849_clean.sql`*

*For detailed constraints, triggers, and sample inserts, see also: DATABASE_CONSTRAINTS.md, SCHEMA_EVOLUTION.md, and session_log_tailor3.md.* 