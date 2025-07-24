# V10 Database Schema Documentation (tailor3)

## Overview
This document describes the complete database schema for the V10 app (tailor3), including tables, relationships, and data structures. This schema is more normalized and scalable than tailor2, supporting richer ingestion, analytics, user action tracking with undo functionality, and future expansion.

**Current Status**: 18 tables, 7 views, with comprehensive action tracking and undo capabilities.

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

### User Action Tracking Tables

#### `user_sessions`
- `id` (SERIAL PRIMARY KEY)
- `user_id` (INTEGER, REFERENCES users(id) ON DELETE CASCADE)
- `session_id` (UUID, DEFAULT gen_random_uuid())
- `device_type` (TEXT, CHECK: 'iOS', 'Android', 'Web', 'Unknown')
- `app_version` (TEXT)
- `started_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
- `ended_at` (TIMESTAMP)
- `action_count` (INTEGER, DEFAULT 0)
- `duration_seconds` (INTEGER)

#### `user_actions`
- `id` (SERIAL PRIMARY KEY)
- `user_id` (INTEGER, REFERENCES users(id) ON DELETE CASCADE)
- `session_id` (UUID)
- `action_type` (TEXT, NOT NULL, CHECK: 'submit_feedback', 'update_feedback', 'delete_feedback', 'add_garment', 'update_garment', 'delete_garment', 'view_garment', 'view_closet', 'app_open', 'app_close', 'scan_item', 'view_product', 'search', 'filter', 'undo_action')
- `target_table` (TEXT) -- 'user_garment_feedback', 'user_garments', etc.
- `target_id` (INTEGER) -- record ID that was changed
- `previous_values` (JSONB) -- what it was before (for undo)
- `new_values` (JSONB) -- what it became
- `metadata` (JSONB) -- extra context (screen, duration, etc.)
- `is_undone` (BOOLEAN, DEFAULT FALSE)
- `undone_at` (TIMESTAMP)
- `undone_by_action_id` (INTEGER, REFERENCES user_actions(id))
- `created_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)

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
- `image_url` (TEXT)
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

### Views

#### `user_action_history`
A comprehensive view for querying user actions with human-readable descriptions:
- Joins `user_actions` with `users` table
- Includes user email and action descriptions
- Ordered by creation time (most recent first)
- Used for action history lookups and undo functionality

#### `size_guide_entries_with_brand`
Joins size guide entries with brand information for easier querying.

#### `user_feedback_by_dimension`
Provides user feedback organized by dimension for analysis.

#### `user_garments_actual_feedback`
Shows user garments with their actual feedback values.

#### `user_garments_feedback_summary`
Summarizes feedback data for user garments.

#### `user_garments_simple`
Simplified view of user garments for basic queries.

#### `user_latest_feedback_by_dimension`
Shows the most recent feedback by dimension for each user garment.

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
- User actions and sessions cascade delete when user is deleted
- User actions can reference other actions for undo tracking (self-referencing)

### Check Constraints
- Gender values: 'Male', 'Female', 'Unisex'
- Unit values: 'in', 'cm'
- Fit types: 'Regular', 'Slim', 'Tall' (for garments/guides), 'tight', 'perfect', 'relaxed' (for fit zones)
- Feedback types: 'fit', 'length', 'other'
- Admin roles: 'admin', 'moderator', 'contributor'
- Guide levels: 'brand_level', 'category_level', 'product_level'
- Device types: 'iOS', 'Android', 'Web', 'Unknown'
- Action types: 'submit_feedback', 'update_feedback', 'delete_feedback', 'add_garment', 'update_garment', 'delete_garment', 'view_garment', 'view_closet', 'app_open', 'app_close', 'scan_item', 'view_product', 'search', 'filter', 'undo_action'

### Performance Indexes
- **user_actions**: 
  - `idx_user_actions_user_created` on (user_id, created_at DESC) for recent action lookups
  - `idx_user_actions_target` on (target_table, target_id) for finding actions on specific records
  - `idx_user_actions_undone` on (is_undone) WHERE is_undone = FALSE for finding undoable actions
- **user_sessions**:
  - `idx_user_sessions_user_started` on (user_id, started_at DESC) for session history

---

## Known Issues & Limitations
- Some measurement types (e.g., shoulder, rise) not yet supported in all tables
- Size standardization is ongoing; mappings may be incomplete for some brands
- Action tracking currently focuses on feedback; could be expanded to more user interactions

## Recent Improvements (2025-07-24)
- ✅ Added comprehensive user action tracking with undo functionality
- ✅ Added user session management for analytics
- ✅ Added `image_url` field to `user_garments` for product images
- ✅ Created `user_action_history` view for easy action querying
- ✅ Implemented complete audit trail for user feedback changes

## Future Improvements Needed
- Add more measurement types and garment attributes as needed
- Expand action tracking to cover more user interactions (app navigation, search, etc.)
- Automate ingestion and mapping workflows
- Add more analytics views and dashboards
- Continue to normalize and modularize as new use cases arise

---

*Schema based on: `supabase/tailor3_schema_2025-06-29_231849_clean.sql`*
*Updated: 2025-07-24 with action tracking tables and undo functionality*

*For detailed constraints, triggers, and sample inserts, see also: DATABASE_CONSTRAINTS.md, SCHEMA_EVOLUTION.md, and session_log_tailor3.md.* 