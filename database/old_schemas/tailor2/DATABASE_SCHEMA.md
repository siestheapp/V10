# V10 Database Schema Documentation

## Overview
This document describes the complete database schema for the V10 app, including tables, relationships, and data structures.

## Database: `tailor2` (PostgreSQL)

### Core Tables

#### `users`
- `id` (SERIAL PRIMARY KEY)
- `email` (VARCHAR)
- `password_hash` (VARCHAR)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

#### `garments`
- `id` (SERIAL PRIMARY KEY)
- `user_id` (INTEGER REFERENCES users(id))
- `brand` (VARCHAR)
- `category` (VARCHAR) - 'Tops', 'Bottoms', 'Outerwear'
- `size` (VARCHAR)
- `product_name` (VARCHAR)
- `owns_garment` (BOOLEAN)
- `created_at` (TIMESTAMP)

#### `measurements`
- `id` (SERIAL PRIMARY KEY)
- `garment_id` (INTEGER REFERENCES garments(id))
- `measurement_type` (VARCHAR) - 'chest', 'waist', 'sleeve', 'neck', etc.
- `value` (DECIMAL)
- `range_min` (DECIMAL)
- `range_max` (DECIMAL)
- `unit` (VARCHAR) - 'inches', 'cm'

#### `fit_feedback`
- `id` (SERIAL PRIMARY KEY)
- `garment_id` (INTEGER REFERENCES garments(id))
- `user_id` (INTEGER REFERENCES users(id))
- `fit_type` (VARCHAR) - 'Tight', 'Good', 'Relaxed'
- `feedback_text` (TEXT)
- `created_at` (TIMESTAMP)

#### `fit_zones`
- `id` (SERIAL PRIMARY KEY)
- `user_id` (INTEGER REFERENCES users(id))
- `category` (VARCHAR)
- `measurement_type` (VARCHAR)
- `tight_min` (DECIMAL)
- `tight_max` (DECIMAL)
- `good_min` (DECIMAL)
- `good_max` (DECIMAL)
- `relaxed_min` (DECIMAL)
- `relaxed_max` (DECIMAL)
- `updated_at` (TIMESTAMP)

### Product Catalog Tables

#### `products`
- `id` (SERIAL PRIMARY KEY)
- `brand` (VARCHAR)
- `name` (VARCHAR)
- `category` (VARCHAR)
- `price` (DECIMAL)
- `image_url` (VARCHAR)
- `product_url` (VARCHAR)
- `description` (TEXT)
- `created_at` (TIMESTAMP)

#### `product_measurements`
- `id` (SERIAL PRIMARY KEY)
- `product_id` (INTEGER REFERENCES products(id))
- `size` (VARCHAR)
- `measurement_type` (VARCHAR)
- `value` (DECIMAL)
- `range_min` (DECIMAL)
- `range_max` (DECIMAL)

#### `product_inventory`
- `id` (SERIAL PRIMARY KEY)
- `product_id` (INTEGER REFERENCES products(id))
- `size` (VARCHAR)
- `in_stock` (BOOLEAN)
- `quantity` (INTEGER)
- `updated_at` (TIMESTAMP)

### Shopping & Recommendations

#### `shopping_sessions`
- `id` (SERIAL PRIMARY KEY)
- `user_id` (INTEGER REFERENCES users(id))
- `started_at` (TIMESTAMP)
- `ended_at` (TIMESTAMP)

#### `product_views`
- `id` (SERIAL PRIMARY KEY)
- `user_id` (INTEGER REFERENCES users(id))
- `product_id` (INTEGER REFERENCES products(id))
- `viewed_at` (TIMESTAMP)
- `session_id` (INTEGER REFERENCES shopping_sessions(id))

#### `recommendations`
- `id` (SERIAL PRIMARY KEY)
- `user_id` (INTEGER REFERENCES users(id))
- `product_id` (INTEGER REFERENCES products(id))
- `fit_confidence` (DECIMAL)
- `recommended_size` (VARCHAR)
- `reason` (TEXT)
- `created_at` (TIMESTAMP)

### Analytics & Tracking

#### `user_measurements`
- `id` (SERIAL PRIMARY KEY)
- `user_id` (INTEGER REFERENCES users(id))
- `measurement_type` (VARCHAR)
- `value` (DECIMAL)
- `measured_at` (TIMESTAMP)

#### `app_usage`
- `id` (SERIAL PRIMARY KEY)
- `user_id` (INTEGER REFERENCES users(id))
- `action` (VARCHAR) - 'scan_garment', 'view_product', 'add_to_closet'
- `details` (JSONB)
- `timestamp` (TIMESTAMP)

## Current Data Insights

### Sample Data Counts (as of latest backup)
- Users: ~50
- Garments: ~200
- Measurements: ~800
- Fit Feedback: ~150

### Common Patterns
- Most users have 3-5 garments in their closet
- Chest measurements range from 32" to 48"
- Popular brands: Theory, Uniqlo, J.Crew, Banana Republic
- Most feedback is "Good Fit" or "Tight but I Like It"

## API Endpoints & Data Flow

### Current Endpoints
- `GET /user/{id}/measurements` - Returns fit zones and garment data
- `POST /garments` - Add new garment
- `POST /feedback` - Submit fit feedback
- `GET /shop/recommendations` - Get product recommendations

### Data Processing
1. User scans garment → stored in `garments` table
2. Measurements extracted → stored in `measurements` table
3. Fit feedback collected → stored in `fit_feedback` table
4. Fit zones calculated → stored in `fit_zones` table
5. Recommendations generated → based on fit zones and product catalog

## Known Issues & Limitations
- Limited product catalog (mostly mock data)
- No size standardization across brands
- Fit zone calculations only for chest measurements
- No historical tracking of measurement changes
- Limited analytics on user behavior

## Future Improvements Needed
- Expand product catalog with real retailer data
- Add more measurement types (length, shoulder, etc.)
- Implement size standardization
- Add user preference tracking
- Create recommendation engine improvements
- Add social features (sharing, reviews) 