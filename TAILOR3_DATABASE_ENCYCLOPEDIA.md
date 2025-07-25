# Tailor3 Database Encyclopedia
*Complete Reference Guide for the Sies App Database*

## 📋 Table of Contents
- [Overview](#overview)
- [Core User System](#core-user-system)
- [Garment Management](#garment-management)
- [Brand & Catalog System](#brand--catalog-system)
- [Size Guide System](#size-guide-system)
- [Feedback & Fit System](#feedback--fit-system)
- [Admin & Audit System](#admin--audit-system)
- [Views & Computed Data](#views--computed-data)
- [Triggers & Automation](#triggers--automation)
- [Relationships Map](#relationships-map)

---

## Overview

**Database:** `tailor3` (Supabase PostgreSQL)  
**Purpose:** Complete garment fitting and recommendation system for the Sies app  
**Tables:** 19 core tables + 10 views  
**Key Features:** Comprehensive audit trails, undo functionality, measurement analysis, brand-specific size guides

### Complete Table List (19 Tables)
1. `admin_activity_log` - Admin action audit trail
2. `admins` - Administrative user accounts  
3. `audit_log` - General system audit log
4. `body_measurements` - User body measurements
5. `brands` - Clothing brand registry
6. `categories` - Garment type classification
7. `feedback_codes` - Standardized feedback options
8. `fit_zones` - Calculated fit recommendations
9. `measurement_instructions` - How-to-measure guides
10. `raw_size_guides` - Unprocessed size guide data
11. `size_guide_entries` - Individual size measurements
12. `size_guides` - Brand-specific size charts
13. `standardization_log` - Data processing history
14. `subcategories` - Specific garment styles
15. `user_actions` - User activity audit trail
16. `user_garment_feedback` - Fit feedback collection
17. `user_garments` - User's clothing inventory
18. `user_sessions` - Login session tracking
19. `users` - User accounts and profiles

### Complete View List (10 Views)
1. `audit_activity_summary` - Audit log summary by table/operation
2. `brand_measurement_coverage_summary` - Brand measurement statistics
3. `brand_user_measurement_comparison` - User vs brand measurement analysis
4. `size_guide_entries_with_brand` - Size entries with brand context
5. `user_action_history` - User action history with descriptions
6. `user_feedback_by_dimension` - Feedback organized by body dimension
7. `user_garments_actual_feedback` - Garments with actual feedback data
8. `user_garments_feedback_summary` - Feedback count summaries
9. `user_garments_simple` - Simplified garment view
10. `user_latest_feedback_by_dimension` - Most recent feedback per dimension

---

## Core User System

### `users` - User Accounts & Profiles
**Created:** Core table (schema foundation)  
**Purpose:** Central user registry with basic profile information and measurement preferences.

**Key Columns:**
- `id` - Primary key, referenced throughout system
- `email` - Unique identifier, login credential
- `gender` - Male/Female/Unisex, affects size guide matching
- `height_in` - User height in inches for fit calculations
- `preferred_units` - in/cm, determines measurement display
- `created_at` - Account creation timestamp
- `notes` - Admin notes about user

**Usage Patterns:**
- Referenced by `user_garments`, `body_measurements`, `user_actions`
- Gender field critical for size guide matching
- Height used in fit zone calculations
- Soft deletes preferred (no CASCADE deletes)

**Related Tables:** All user-specific tables reference this via `user_id`

---

### `body_measurements` - Individual Body Measurements
**Created:** Core table (schema foundation)  
**Purpose:** Stores actual body measurements for each user to enable fit predictions and size recommendations.

**Key Columns:**
- `user_id` - Links to users table (CASCADE DELETE)
- `chest`, `waist`, `neck`, `sleeve`, `hip`, `inseam`, `length` - Body dimensions
- `unit` - in/cm for measurement values
- `confidence_score` - Reliability rating (0.0-1.0)
- `source` - How measurement was obtained (manual, estimated, scanned)
- `created_at`, `updated_at` - Tracking measurement history

**Usage Patterns:**
- Multiple measurement sets per user allowed (historical tracking)
- Confidence scoring helps weight measurements in algorithms
- Backend uses for size recommendations and fit zone calculations
- Source tracking enables measurement quality assessment

**Key Relationships:**
- `users(id)` → `body_measurements(user_id)` (1:many, CASCADE)

---

### `user_sessions` - Login Session Tracking
**Created:** Core table (schema foundation)  
**Purpose:** Tracks user login sessions for security and analytics.

**Key Columns:**
- `user_id` - Links to users table
- `session_token` - Unique session identifier
- `created_at` - Login timestamp
- `expires_at` - Session expiration
- `last_activity` - Most recent activity timestamp
- `ip_address` - Client IP for security
- `user_agent` - Browser/app information

**Usage Patterns:**
- Created on user login
- Updated on each API request
- Expired sessions cleaned up periodically
- Used for concurrent session management

---

## Garment Management

### `user_garments` - User's Clothing Items
**Created:** Core table (schema foundation)  
**Purpose:** Central inventory of clothing items owned by users, with brand, size, and image information.

**Key Columns:**
- `user_id` - Owner of the garment
- `brand_id` - Links to brands table
- `product_name` - User-provided or scanned name
- `size_label` - Size as labeled on garment (S, M, L, 32x34, etc.)
- `image_url` - Product image URL for display
- `category_id`, `subcategory_id` - Classification
- `purchase_date` - When item was acquired
- `created_at` - When added to app
- `owns_garment` - Boolean flag for ownership status
- `fit_feedback` - Quick fit summary
- `feedback_timestamp` - When feedback was last updated

**Usage Patterns:**
- Core entity for fit feedback collection
- Images displayed in closet view
- Size labels matched against size guides for recommendations
- Categories used for filtering and organization

**Key Relationships:**
- `users(id)` → `user_garments(user_id)` (1:many)
- `brands(id)` → `user_garments(brand_id)` (1:many)
- `categories(id)` → `user_garments(category_id)` (1:many)

---

## Brand & Catalog System

### `brands` - Clothing Brand Registry
**Created:** Core table (schema foundation)  
**Purpose:** Master list of clothing brands with metadata for size guide organization and regional preferences.

**Key Columns:**
- `name` - Brand name (unique)
- `region` - Geographic region (affects sizing standards)
- `default_unit` - Preferred measurement unit (in/cm)
- `created_by`, `updated_by` - Admin tracking
- `notes` - Admin notes about brand characteristics

**Usage Patterns:**
- Referenced by user_garments and size_guides
- Region affects size guide interpretation
- Default unit used when creating size guides
- Name must be unique across system

**Key Relationships:**
- `brands(id)` → `user_garments(brand_id)` (1:many)
- `brands(id)` → `size_guides(brand_id)` (1:many)

---

### `categories` - Garment Type Classification
**Created:** Core table (schema foundation)  
**Purpose:** High-level garment classification (Shirts, Pants, Jackets, etc.).

**Key Columns:**
- `name` - Category name (unique)
- `description` - Detailed explanation
- `created_by`, `updated_by` - Admin tracking

**Usage Patterns:**
- Used for organizing size guides
- Filters garment displays
- Affects measurement requirements (shirts need chest, pants need waist)

**Key Relationships:**
- `categories(id)` → `subcategories(category_id)` (1:many)
- `categories(id)` → `size_guides(category_id)` (1:many)

---

### `subcategories` - Specific Garment Styles
**Created:** Core table (schema foundation)  
**Purpose:** Detailed garment classification within categories (Dress Shirts, T-Shirts, Jeans, Chinos).

**Key Columns:**
- `category_id` - Parent category
- `name` - Subcategory name (unique within category)
- `description` - Style-specific details

**Usage Patterns:**
- Provides granular classification
- Enables style-specific size guides
- Used in product matching algorithms

**Key Relationships:**
- `categories(id)` → `subcategories(category_id)` (1:many, CASCADE)

---

## Size Guide System

### `size_guides` - Brand Size Charts
**Created:** Core table (schema foundation)  
**Purpose:** Brand-specific size charts that define measurement ranges for each size label.

**Key Columns:**
- `brand_id` - Which brand this guide belongs to
- `gender` - Male/Female/Unisex sizing
- `category_id` - Garment type (Shirts, Pants, etc.)
- `fit_type` - Regular/Slim/Tall variations
- `guide_level` - brand_level/category_level/product_level specificity
- `version` - Version number for guide updates
- `source_url` - Original source of size data
- `unit` - Measurement unit for this guide

**Usage Patterns:**
- One guide per brand/gender/category/fit_type combination
- Versioning allows guide updates without losing history
- Source URLs enable verification and updates
- Unit consistency critical for calculations

**Key Relationships:**
- `brands(id)` → `size_guides(brand_id)` (1:many, CASCADE)
- `categories(id)` → `size_guides(category_id)` (1:many)
- `size_guides(id)` → `size_guide_entries(size_guide_id)` (1:many, CASCADE)

---

### `size_guide_entries` - Individual Size Measurements
**Created:** Core table (schema foundation)  
**Purpose:** Specific measurement ranges for each size label within a size guide.

**Key Columns:**
- `size_guide_id` - Parent size guide
- `size_label` - Size name (S, M, L, 32, 34, etc.)
- `chest_min`, `chest_max`, `chest_range` - Chest measurement range
- `waist_min`, `waist_max`, `waist_range` - Waist measurement range
- `sleeve_min`, `sleeve_max`, `sleeve_range` - Sleeve length range
- `neck_min`, `neck_max`, `neck_range` - Neck measurement range
- `hip_min`, `hip_max`, `hip_range` - Hip measurement range
- `center_back_length` - Garment length measurement
- `measurements_available` - Array of available measurement types

**Usage Patterns:**
- Ranges accommodate manufacturing tolerances
- Not all measurements required for all garment types
- Used in size recommendation algorithms
- Enables fit zone calculations

**Key Relationships:**
- `size_guides(id)` → `size_guide_entries(size_guide_id)` (1:many, CASCADE)

---

### `raw_size_guides` - Unprocessed Size Data
**Created:** Data ingestion enhancement  
**Purpose:** Stores original size guide data before standardization and processing.

**Key Columns:**
- `brand_id` - Source brand
- `gender` - Target gender
- `category_id` - Garment category
- `raw_data` - Original size guide content (JSONB)
- `source_url` - Where data was obtained
- `processed` - Whether data has been standardized
- `notes` - Processing notes

**Usage Patterns:**
- Preserves original data for reference
- Enables reprocessing with improved algorithms
- Tracks data source for updates
- JSONB format accommodates various input formats

---

## Feedback & Fit System

### `user_garment_feedback` - Fit Feedback Collection
**Created:** Core table (schema foundation)  
**Purpose:** Records how garments actually fit users, enabling fit prediction improvements.

**Key Columns:**
- `user_id` - User providing feedback
- `user_garment_id` - Garment being evaluated (renamed from garment_id)
- `dimension` - Body part (chest, waist, sleeve, length, overall)
- `feedback_code_id` - Standardized feedback (links to feedback_codes)
- `feedback_text` - User's descriptive feedback
- `confidence` - User's confidence in their assessment
- `created_at` - When feedback was given

**Usage Patterns:**
- Multiple feedback entries per garment (different dimensions)
- Feedback codes ensure consistent data collection
- Text feedback provides qualitative insights
- Confidence weighting improves algorithm accuracy

**Key Relationships:**
- `users(id)` → `user_garment_feedback(user_id)` (1:many)
- `user_garments(id)` → `user_garment_feedback(user_garment_id)` (1:many)
- `feedback_codes(id)` → `user_garment_feedback(feedback_code_id)` (1:many)

---

### `feedback_codes` - Standardized Feedback Options
**Created:** Core table (schema foundation)  
**Purpose:** Provides consistent feedback categories for data analysis and machine learning.

**Key Columns:**
- `code` - Short identifier (TT, TL, PF, etc.)
- `feedback_text` - Human-readable description
- `feedback_type` - Category classification
- `is_positive` - Boolean for sentiment analysis
- `display_order` - UI ordering

**Usage Patterns:**
- Referenced by user_garment_feedback
- Boolean values enable statistical analysis
- Categories group related feedback types
- Display order controls UI presentation

---

### `fit_zones` - Calculated Fit Recommendations
**Created:** Algorithm enhancement  
**Purpose:** Stores calculated fit predictions based on user measurements and size guides.

**Key Columns:**
- `user_id` - Target user
- `brand_id` - Brand being evaluated
- `category_id` - Garment category
- `recommended_size` - Calculated best size
- `fit_score` - Confidence in recommendation (0.0-1.0)
- `calculation_method` - Algorithm used
- `created_at` - When calculation was performed

**Usage Patterns:**
- Pre-calculated recommendations for performance
- Recalculated when user measurements change
- Multiple calculation methods for comparison
- Fit scores enable ranking of recommendations

---

## Admin & Audit System

### `admins` - Administrative Users
**Created:** Core table (schema foundation)  
**Purpose:** Manages admin user accounts for web interface access and audit tracking.

**Key Columns:**
- `email` - Admin login credential (unique)
- `name` - Display name
- `role` - admin/moderator/contributor permissions
- `created_at` - Account creation
- `notes` - Admin notes about user

**Usage Patterns:**
- Referenced by created_by/updated_by fields throughout system
- Role-based access control in web interfaces
- Audit trail attribution

**Key Relationships:**
- `admins(id)` → `brands(created_by)` (1:many)
- `admins(id)` → `admin_activity_log(admin_id)` (1:many)

---

### `admin_activity_log` - Comprehensive Audit Trail
**Created:** Core table (schema foundation)  
**Purpose:** Records all administrative actions and database changes for security and debugging.

**Key Columns:**
- `admin_id` - Admin who performed action
- `action_type` - INSERT/UPDATE/DELETE/etc.
- `table_name` - Affected table
- `record_id` - Affected record
- `description` - Human-readable action description
- `details` - Full change details (JSONB)
- `created_at` - When action occurred

**Usage Patterns:**
- Populated by database triggers on all major tables
- Manual entries for admin interface actions
- JSONB details enable full change reconstruction
- Critical for debugging and security auditing

**Key Relationships:**
- `admins(id)` → `admin_activity_log(admin_id)` (1:many)

---

### `audit_log` - General System Audit Log
**Created:** System audit enhancement  
**Purpose:** General purpose audit logging for system-wide changes and events.

**Key Columns:**
- `table_name` - Affected table
- `operation` - Type of operation (INSERT/UPDATE/DELETE)
- `changed_at` - When change occurred
- `old_values` - Previous state (JSONB)
- `new_values` - New state (JSONB)

**Usage Patterns:**
- System-wide change tracking
- Broader scope than admin_activity_log
- Used for general audit queries
- Enables change rollback analysis

---

### `user_actions` - User Activity Audit Trail
**Created:** Core table (schema foundation)  
**Purpose:** Tracks user-initiated actions with undo capability for user experience and debugging.

**Key Columns:**
- `user_id` - User who performed action
- `session_id` - Session identifier
- `action_type` - Type of action performed
- `target_table` - Database table affected
- `target_id` - Specific record affected
- `previous_values` - Before state (JSONB)
- `new_values` - After state (JSONB)
- `metadata` - Additional context (JSONB)
- `is_undone` - Whether action has been reversed
- `undone_at` - When action was undone
- `created_at` - Action timestamp

**Usage Patterns:**
- Enables undo functionality in user interfaces
- Debugging user-reported issues
- Analytics on user behavior patterns
- State tracking for complex operations

**Key Relationships:**
- `users(id)` → `user_actions(user_id)` (1:many)

---

### `measurement_instructions` - How-to-Measure Guide
**Created:** User experience enhancement  
**Purpose:** Provides standardized instructions for taking body measurements.

**Key Columns:**
- `measurement_type` - chest/waist/neck/sleeve/etc.
- `instruction_text` - Step-by-step measuring guide
- `image_url` - Illustration of measurement technique
- `video_url` - Video demonstration
- `tips` - Additional measuring tips
- `common_mistakes` - What to avoid

**Usage Patterns:**
- Referenced in measurement collection interfaces
- Ensures consistent measurement techniques
- Reduces measurement errors
- Supports multiple media types for clarity

---

### `standardization_log` - Data Processing History
**Created:** Data quality enhancement  
**Purpose:** Tracks data cleaning, unit conversions, and standardization operations.

**Key Columns:**
- `operation_type` - Type of standardization performed
- `table_name` - Table that was processed
- `record_count` - Number of records affected
- `details` - Processing details (JSONB)
- `performed_by` - Admin who initiated operation
- `created_at` - When operation occurred

**Usage Patterns:**
- Tracks bulk data operations
- Enables rollback of standardization errors
- Documents data quality improvements
- Performance monitoring for batch operations

---

## Views & Computed Data

### `audit_activity_summary` - Audit Log Summary
**Purpose:** Aggregates audit log entries by table and operation type with latest activity timestamps.

**Provides:**
- Table-wise operation counts
- Latest change timestamps
- Operation type breakdown
- Activity monitoring overview

---

### `brand_measurement_coverage_summary` - Brand Measurement Statistics
**Purpose:** Analyzes measurement coverage across brands to identify data gaps.

**Provides:**
- Total garments per brand
- Average coverage percentage
- Fully covered vs no coverage garments
- Most missing dimension by brand

---

### `brand_user_measurement_comparison` - User vs Brand Measurement Analysis
**Purpose:** Compares user feedback dimensions with available brand measurements.

**Provides:**
- Available brand measurements per garment
- User feedback dimensions entered
- Missing feedback dimensions
- Coverage percentage calculations
- Overlap analysis between brand data and user feedback

---

### `size_guide_entries_with_brand` - Size Entries with Brand Context
**Purpose:** Enriches size guide entries with brand and category information for easier querying.

**Combines:**
- size_guide_entries (measurement data)
- size_guides (guide metadata)
- brands (brand information)

---

### `user_action_history` - User Action History with Descriptions
**Purpose:** Provides human-readable descriptions of user actions for interface display.

**Features:**
- Descriptive action summaries
- User email context
- Undo status tracking
- Chronological ordering

---

### `user_feedback_by_dimension` - Feedback Organized by Body Dimension
**Purpose:** Organizes all user feedback by body dimension for analysis and display.

**Combines:**
- users (user context)
- user_garments (garment details)
- user_garment_feedback (feedback data)
- feedback_codes (standardized feedback)
- brands, categories, subcategories (classification)

---

### `user_garments_actual_feedback` - Garments with Actual Feedback Data
**Purpose:** Pivots feedback data to show all dimensions for each garment in a single row.

**Features:**
- Separate columns for each dimension (overall, chest, sleeve, length)
- Feedback text and type for each dimension
- Sentiment analysis (positive/negative)
- Timestamp tracking per dimension

---

### `user_garments_feedback_summary` - Feedback Count Summaries
**Purpose:** Provides statistical summaries of feedback counts by user and garment.

**Metrics:**
- Total feedback count per garment
- Dimension-specific feedback counts
- Positive vs negative feedback counts
- User and brand breakdowns

---

### `user_garments_simple` - Simplified Garment View
**Purpose:** Streamlined view of user garments for basic display needs.

**Features:**
- Essential garment information only
- User and brand context
- Category classification
- Simplified feedback summary

---

### `user_latest_feedback_by_dimension` - Most Recent Feedback Per Dimension
**Purpose:** Shows only the most recent feedback for each garment/dimension combination to avoid duplicates.

**Features:**
- DISTINCT ON clause for latest feedback only
- Complete feedback context
- User and garment information
- Chronological ordering

---

## Triggers & Automation

### Audit Triggers (61+ total)
**Pattern:** `audit_trigger_[table_name]`  
**Purpose:** Automatically log all changes to major tables  
**Target:** `admin_activity_log` table  
**Coverage:** All 19 core tables with INSERT/UPDATE/DELETE events

### Custom Logging Triggers
**Pattern:** `trigger_log_[table_name]`  
**Purpose:** Enhanced logging with custom business logic  
**Target:** `admin_activity_log` with richer JSONB details  
**Current Coverage:** size_guides, size_guide_entries

### Validation Triggers
- `tr_check_filters` - Validates subscription filter rules
- `update_objects_updated_at` - Maintains timestamp consistency

---

## Relationships Map

### Core Entity Relationships
```
users (1) → (many) user_garments
users (1) → (many) body_measurements  
users (1) → (many) user_garment_feedback
users (1) → (many) user_actions
users (1) → (many) user_sessions

brands (1) → (many) user_garments
brands (1) → (many) size_guides

categories (1) → (many) subcategories
categories (1) → (many) size_guides
categories (1) → (many) user_garments

size_guides (1) → (many) size_guide_entries

user_garments (1) → (many) user_garment_feedback

admins (1) → (many) admin_activity_log
admins (1) → (many) brands (created_by)

feedback_codes (1) → (many) user_garment_feedback
```

### Critical Foreign Keys
- **CASCADE DELETE:** body_measurements, subcategories, size_guide_entries
- **RESTRICT DELETE:** Most other relationships to prevent data loss
- **NULL ON DELETE:** Admin references when admin accounts are removed

---

## Data Integrity Rules

### Unique Constraints
- `users.email` - One account per email
- `brands.name` - Unique brand names
- `categories.name` - Unique category names
- `(subcategories.category_id, subcategories.name)` - Unique within category
- `(size_guides.brand_id, gender, category_id, fit_type, version)` - Unique size guides

### Check Constraints
- Gender values: 'Male', 'Female', 'Unisex'
- Units: 'in', 'cm'
- Admin roles: 'admin', 'moderator', 'contributor'
- Fit types: 'Regular', 'Slim', 'Tall'

### Business Rules
- Size guide entries must have at least one measurement range
- Feedback requires either feedback_code_id or feedback_text
- User actions with is_undone=false can be reversed
- Body measurements require confidence_score between 0.0 and 1.0

---

*Last Updated: July 2025*  
*Database Version: tailor3*  
*Total Tables: 19 + 10 Views*  
*Total Triggers: 61+ audit triggers + custom triggers* 