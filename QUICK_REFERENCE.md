# Sies Project Quick Reference

## 📝 About the App
Sies is a comprehensive garment fitting and recommendation system composed of:
* **iOS App (SwiftUI)** – lets users scan garments, view size guides, and give fit feedback.
* **Backend API (Flask)** – core business logic & ML estimation, served from `ios_app/Backend/app.py` on **port 8006**.
* **Web Garment Manager** – user-facing closet interface at **http://localhost:5001** (`scripts/web_garment_manager.py`).
* **Admin Interface** – brand/category management at **http://localhost:5002** (`scripts/admin_garment_manager.py`).

All services share a single Supabase **PostgreSQL** database (`tailor3`) with automatic change logging via the `user_actions` audit table.

## 🗄️ Database Table Purposes (tailor3)

### Core User Tables
- **`users`** - User accounts and profiles (email, gender, height, preferred units)
- **`body_measurements`** - Individual body measurements per user (chest, waist, neck, sleeve, etc.)
- **`user_sessions`** - User login sessions and activity tracking

### Garment & Feedback Tables  
- **`user_garments`** - User's owned clothing items with brand, size, image_url
- **`user_garment_feedback`** - How garments fit users (too tight, too loose, etc.)
- **`user_actions`** - Audit trail of user-initiated actions with undo capability

### Catalog & Brand Tables
- **`brands`** - Clothing brands (J.Crew, NN.07, etc.) with region and default units
- **`categories`** - Garment types (Shirts, Pants, etc.)
- **`subcategories`** - Specific garment styles (Dress Shirts, Jeans, etc.)
- **`size_guides`** - Brand-specific size charts (J.Crew Men's Shirts)
- **`size_guide_entries`** - Individual size measurements within guides (S, M, L with chest/waist/sleeve)
- **`raw_size_guides`** - Unprocessed size guide data before standardization

### System & Admin Tables
- **`admins`** - Admin user accounts for web interface
- **`admin_activity_log`** - Audit trail for admin actions and database changes
- **`feedback_codes`** - Standardized feedback options (Too Tight, Too Loose, etc.)
- **`fit_zones`** - Calculated fit recommendations based on measurements
- **`measurement_instructions`** - How to measure different body parts
- **`standardization_log`** - Data cleaning and unit conversion tracking

### Views (Computed Tables)
- **`user_garment_feedback_view`** - Combined garment + feedback data
- **`brand_dimensions_view`** - Brand measurement statistics
- **`latest_feedback_view`** - Most recent feedback per garment
- **`custom_column_order_view`** - Flexible garment display columns

## 📁 Key Documentation Files
- **Database Schema**: `TAILOR3_COMPLETE_SCHEMA.md` - Complete database structure and relationships
- **Project Context**: `contextjuly23.md` - Current project state and recent accomplishments
- **Database Config**: `DATABASE_CONFIG.md` - Connection details and setup
- **Project Structure**: `ios_app/Docs/PROJECT_STRUCTURE.md` - Codebase organization
- **Views Documentation**: `VIEWS_CREATED.md` - Database views and their purposes

## 🗄️ Database Quick Facts
- **Database**: Supabase PostgreSQL (tailor3)
- **Connection**: `aws-0-us-east-2.pooler.supabase.com:6543`
- **Key Tables**: 
  - `user_garments` - Stores user clothing with `image_url` field
  - `user_actions` - Full audit history tracking:
    - Every database change (DDL/DML operations) with `sql_command`
    - Stores before and after states in `previous_state` / `new_state` JSONB columns
    - Links to the user (`user_id`) who made the change
    - `is_undone` flag supports undo functionality
- **Brands**: J.Crew, NN.07, Banana Republic, Lululemon, Patagonia, Faherty

## 🔧 Common Operations

### Add Image to Existing Garment
```sql
UPDATE user_garments 
SET image_url = 'https://example.com/image.jpg' 
WHERE id = [garment_id];
```

### Find Garments by Brand
```sql
SELECT ug.*, b.name as brand_name 
FROM user_garments ug 
JOIN brands b ON ug.brand_id = b.id 
WHERE b.name = 'Brand Name';
```

### Check Current Users
```sql
SELECT id, email FROM users ORDER BY id;
```

### View User Actions (Audit Trail)
```sql
-- Recent actions
SELECT action_type, target_table, created_at 
FROM user_actions 
ORDER BY created_at DESC 
LIMIT 10;

-- Actions by type
SELECT action_type, COUNT(*) 
FROM user_actions 
GROUP BY action_type;

-- Undo functionality
SELECT * FROM user_actions WHERE is_undone = false;
```

### Database Change Tracking
```sql
-- View full change history
SELECT action_type, target_table, sql_command, created_at 
FROM user_actions 
ORDER BY created_at DESC 
LIMIT 10;

-- Audit specific table changes
SELECT created_at, user_id, action_type, 
       previous_state->>'image_url' AS old_image,
       new_state->>'image_url' AS new_image
FROM user_actions
WHERE target_table = 'user_garments';

-- Find reversible actions
SELECT * FROM user_actions 
WHERE is_undone = false
  AND action_type NOT IN ('create table', 'alter table');
```

## 🚀 Development Setup
- **Backend API**: `ios_app/Backend/app.py` (port 8006)
- **Web Garment Manager**: `scripts/web_garment_manager.py` (port 5001)
- **Admin Interface**: `scripts/admin_garment_manager.py` (port 5002)
- **iOS App**: `ios_app/V10/` - SwiftUI app
- **Virtual Environment**: `source venv/bin/activate`
- **Database Access**: Use scripts in `scripts/` folder

## 📱 App Features
- **Closet View**: Shows user's garments with images
- **Image Display**: Uses `AsyncImage` for garment photos
- **Fit Feedback**: Tracks how garments fit users
- **Size Guides**: Brand-specific measurement data

## 🔄 Recent Changes
- Added image URLs to J.Crew and NN.07 shirts
- Backend API includes `imageUrl` field in responses
- Frontend displays actual product images with placeholders for missing images

## 📊 Current State
- **Users**: 1 (user1@example.com)
- **Garments**: Multiple brands with image support
- **Brands**: 6 brands in system
- **Image Integration**: Working with direct product image URLs
- **Action Tracking**: 24 user actions logged (18 feedback updates, 6 undo actions)

## 🛠️ Useful Scripts
- `scripts/web_garment_manager.py` - Web UI for garment management
- `scripts/admin_garment_manager.py` - Admin interface
- `scripts/db_snapshot.py` - Database state tracking

## 📞 Quick Commands
```bash
# Start backend
source venv/bin/activate && cd ios_app/Backend && python app.py

# Database access
PGPASSWORD='efvTower12' psql -h aws-0-us-east-2.pooler.supabase.com -p 6543 -U postgres.lbilxlkchzpducggkrxx -d postgres

# Test API
curl -X GET "http://localhost:8006/user/1/closet"

# Start web interfaces (User & Admin)
source venv/bin/activate && ./start_server.sh

# Open interfaces in browser
open http://localhost:5001  # User Interface
open http://localhost:5002/admin/login  # Admin Interface
```

---
*Last updated: July 2025* 