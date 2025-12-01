# Tailor3 Database Summary

## Database Information
- **Database Name**: tailor3 (Supabase PostgreSQL)
- **Version**: PostgreSQL 15.8
- **Dump Size**: 515KB
- **Dump Date**: 2025-08-06 23:35:33 EDT

## Core Tables

### User Management
- `users` - User accounts and profiles
- `user_sessions` - User session tracking
- `user_actions` - User activity logging (scans, recommendations, etc.)

### Garment & Fit System
- `user_garments` - User's owned garments
- `user_garment_feedback` - Fit feedback for garments
- `user_fit_zones` - User's fit preferences by category/dimension
- `body_measurements` - User body measurements

### Brand & Size Guide System
- `brands` - Clothing brands (Banana Republic, J.Crew, etc.)
- `categories` - Clothing categories (Tops, Bottoms, etc.)
- `subcategories` - Subcategories (T-Shirts, Shirts, etc.)
- `size_guides` - Brand size guide definitions
- `size_guide_entries` - Individual size measurements
- `raw_size_guides` - Raw size guide data before processing

### Measurement System
- `measurement_instructions` - How to measure garments
- `measurement_methodology` - Measurement confidence and reliability
- `feedback_codes` - Standardized fit feedback options
- `fit_zones` - Fit zone definitions

### Product System
- `products` - Product catalog (currently Uniqlo products)

### Admin & Audit
- `admins` - Admin users
- `admin_activity_log` - Admin activity tracking
- `audit_log` - Database change auditing
- `standardization_log` - Size guide standardization tracking

## Key Features

### Multi-Dimensional Fit Analysis
- Stores user fit preferences by category and dimension
- Tracks measurement confidence and reliability scores
- Supports complex fit zone calculations

### Scan History System
- `user_actions` table stores scan history with metadata
- Includes product URLs, recommended sizes, confidence scores
- Supports duplicate detection and deduplication

### Brand-Specific Size Guides
- Comprehensive size guide system for multiple brands
- Supports different measurement methodologies per brand
- Includes measurement instructions and confidence scoring

### Real-time Features
- Supabase realtime subscriptions
- Row-level security policies
- Audit logging for all changes

## Recent Enhancements

### Product Name Extraction
- Backend extracts real product names from web pages
- Stores accurate product names in scan history
- Replaces hardcoded product names

### Image System (Infrastructure Ready)
- Product image extraction functions implemented
- Brand-specific placeholder images
- Ready for real product images when available

### Fast Development Workflow
- API testing tools for rapid backend development
- 60x faster iteration cycle (2-3 seconds vs 2-3 minutes)
- Comprehensive test scripts

## Database Schema Highlights

### User Actions Table (Scan History)
```sql
CREATE TABLE user_actions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action_type TEXT, -- 'scan_item', etc.
    target_table TEXT,
    metadata JSONB, -- Stores product_url, product_name, recommended_size, etc.
    created_at TIMESTAMP DEFAULT NOW(),
    undone_by_action_id INTEGER REFERENCES user_actions(id)
);
```

### User Garments Table
```sql
CREATE TABLE user_garments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    brand_id INTEGER REFERENCES brands(id),
    category_id INTEGER REFERENCES categories(id),
    subcategory_id INTEGER REFERENCES subcategories(id),
    size_label TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Size Guide System
```sql
CREATE TABLE size_guides (
    id SERIAL PRIMARY KEY,
    brand_id INTEGER REFERENCES brands(id),
    gender TEXT,
    category_id INTEGER REFERENCES categories(id),
    fit_type TEXT,
    version INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE size_guide_entries (
    id SERIAL PRIMARY KEY,
    size_guide_id INTEGER REFERENCES size_guides(id),
    size_label TEXT,
    chest_range TEXT,
    neck_range TEXT,
    sleeve_range TEXT,
    waist_range TEXT,
    measurements_available BOOLEAN DEFAULT FALSE
);
```

## Usage Examples

### Recent Scan History Query
```sql
SELECT 
    ua.id,
    ua.metadata->>'product_name' as name,
    ua.metadata->>'brand_name' as brand,
    ua.metadata->>'recommended_size' as size,
    ua.created_at
FROM user_actions ua
WHERE ua.action_type = 'scan_item'
ORDER BY ua.created_at DESC;
```

### User Fit Zones Query
```sql
SELECT 
    category,
    dimension,
    tight_min,
    perfect_min,
    perfect_max,
    relaxed_max
FROM user_fit_zones
WHERE user_id = 1;
```

## File Information
- **Full Dump**: `tailor3_database_dump.sql` (515KB)
- **Contains**: Complete schema, data, indexes, constraints, functions
- **Format**: PostgreSQL pg_dump format
- **Ready for**: Import into any PostgreSQL database

This database powers a sophisticated clothing fit recommendation system with multi-dimensional analysis, brand-specific size guides, and comprehensive user tracking.
