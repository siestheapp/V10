#!/usr/bin/env python3
"""
Create enhanced product data tables for scalable garment storage
This adds new tables without breaking existing functionality
"""

import psycopg2
from datetime import datetime
import sys

# Database configuration - Supabase tailor3
DB_CONFIG = {
    "database": "postgres",
    "user": "postgres.lbilxlkchzpducggkrxx",
    "password": "efvTower12",
    "host": "aws-0-us-east-2.pooler.supabase.com",
    "port": "6543"
}

def create_product_master_tables():
    """Create the new product_master and product_variants tables"""
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        print("🚀 Creating Enhanced Product Data Tables")
        print("=" * 60)
        
        # 1. Create product_master table (shared data across all variants)
        print("\n📦 Creating product_master table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS product_master (
                id SERIAL PRIMARY KEY,
                brand_id INTEGER REFERENCES brands(id),
                product_code VARCHAR(50) NOT NULL,
                base_name TEXT NOT NULL,
                
                -- Shared material and construction data
                materials JSONB,              -- {"primary": "cotton", "composition": {"cotton": 100}}
                care_instructions TEXT[],     -- ['Machine wash cold', 'Tumble dry low']
                construction_details JSONB,   -- {"stitching": "double-needle", "buttons": "pearl"}
                technical_features TEXT[],    -- ['Moisture-wicking', 'Four-way stretch']
                sustainability JSONB,         -- {"certifications": ["BCI"], "recycled": 30}
                
                -- Full descriptions for AI analysis
                description_texts TEXT[],      -- All marketing copy
                styling_notes TEXT[],         -- How to wear it
                
                -- Product details
                product_details TEXT[],       -- Bullet points from product page
                fit_information JSONB,        -- Detailed fit descriptions
                
                -- Measurements guide (if product has specific measurements)
                measurements_guide JSONB,     -- Size charts specific to this product
                
                -- Metadata
                category_id INTEGER REFERENCES categories(id),
                subcategory_id INTEGER REFERENCES subcategories(id),
                
                -- Timestamps
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                last_scraped TIMESTAMP,
                
                -- Unique constraint - one master record per brand/product code
                UNIQUE(brand_id, product_code)
            );
        """)
        print("✅ product_master table created")
        
        # 2. Create product_variants table (color/fit specific)
        print("\n🎨 Creating product_variants table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS product_variants (
                id SERIAL PRIMARY KEY,
                product_master_id INTEGER REFERENCES product_master(id) ON DELETE CASCADE,
                brand_id INTEGER REFERENCES brands(id),
                
                -- Variant identifiers
                sku VARCHAR(100),
                variant_code VARCHAR(50),  -- Unique code for this variant
                
                -- Color information
                color_name VARCHAR(100),
                color_code VARCHAR(50),
                color_hex VARCHAR(7),
                color_swatch_url TEXT,
                color_family VARCHAR(50),  -- 'blue', 'red', 'neutral', etc.
                
                -- Fit information
                fit_option VARCHAR(50),    -- 'Classic', 'Slim', 'Tall', etc.
                
                -- Availability & Pricing
                current_price DECIMAL(10,2),
                original_price DECIMAL(10,2),
                sale_percentage INTEGER,
                currency VARCHAR(3) DEFAULT 'USD',
                in_stock BOOLEAN DEFAULT true,
                sizes_available TEXT[],     -- ['S', 'M', 'L', 'XL']
                sizes_in_stock TEXT[],      -- Currently in stock sizes
                
                -- Images for this specific variant
                images JSONB,               -- [{"url": "...", "type": "main"}, ...]
                
                -- Metadata
                variant_url TEXT,           -- Direct URL to this color/fit combo
                last_checked TIMESTAMP,
                availability_status VARCHAR(50), -- 'in_stock', 'low_stock', 'out_of_stock'
                
                -- Timestamps
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                
                -- Unique constraint - one variant per master/color/fit combination
                UNIQUE(product_master_id, color_name, fit_option)
            );
        """)
        print("✅ product_variants table created")
        
        # 3. Create brand_product_cache table (raw scraped data)
        print("\n💾 Creating brand_product_cache table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS brand_product_cache (
                id SERIAL PRIMARY KEY,
                brand_id INTEGER REFERENCES brands(id),
                cache_key VARCHAR(255) UNIQUE,
                product_url TEXT,
                raw_data JSONB,              -- Complete scraped data
                processed BOOLEAN DEFAULT false,
                error_message TEXT,          -- If scraping failed
                retry_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT NOW(),
                processed_at TIMESTAMP
            );
        """)
        print("✅ brand_product_cache table created")
        
        # 4. Create indexes for performance
        print("\n🔍 Creating indexes for fast lookups...")
        
        # Product master indexes
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_product_master_brand_code 
            ON product_master(brand_id, product_code);
        """)
        
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_product_master_category 
            ON product_master(category_id, subcategory_id);
        """)
        
        # Product variants indexes
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_product_variants_master 
            ON product_variants(product_master_id);
        """)
        
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_product_variants_sku 
            ON product_variants(sku);
        """)
        
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_product_variants_color 
            ON product_variants(product_master_id, color_name);
        """)
        
        # Cache table indexes
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_brand_cache_key 
            ON brand_product_cache(cache_key);
        """)
        
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_brand_cache_processed 
            ON brand_product_cache(processed, brand_id);
        """)
        
        print("✅ All indexes created")
        
        # 5. Add link from user_garments to product_master
        print("\n🔗 Adding product_master link to user_garments...")
        cur.execute("""
            ALTER TABLE user_garments 
            ADD COLUMN IF NOT EXISTS product_master_id INTEGER 
            REFERENCES product_master(id);
        """)
        
        cur.execute("""
            ALTER TABLE user_garments 
            ADD COLUMN IF NOT EXISTS product_variant_id INTEGER 
            REFERENCES product_variants(id);
        """)
        
        print("✅ Links added to user_garments")
        
        # 6. Create a view for easy product querying
        print("\n👁️ Creating product_catalog view...")
        cur.execute("""
            CREATE OR REPLACE VIEW product_catalog AS
            SELECT 
                pm.id as master_id,
                pm.brand_id,
                b.name as brand_name,
                pm.product_code,
                pm.base_name,
                pm.materials,
                pm.care_instructions,
                c.name as category,
                sc.name as subcategory,
                pv.id as variant_id,
                pv.color_name,
                pv.color_hex,
                pv.fit_option,
                pv.current_price,
                pv.sizes_available,
                pv.in_stock,
                pv.images
            FROM product_master pm
            JOIN brands b ON pm.brand_id = b.id
            LEFT JOIN categories c ON pm.category_id = c.id
            LEFT JOIN subcategories sc ON pm.subcategory_id = sc.id
            LEFT JOIN product_variants pv ON pm.id = pv.product_master_id;
        """)
        print("✅ product_catalog view created")
        
        # Commit all changes
        conn.commit()
        
        print("\n" + "=" * 60)
        print("✅ SUCCESS! All tables created successfully")
        print("=" * 60)
        print("\n📊 What was created:")
        print("   • product_master table - Shared product data")
        print("   • product_variants table - Color/fit specific data")
        print("   • brand_product_cache table - Raw scraped data")
        print("   • 7 performance indexes")
        print("   • product_catalog view for easy querying")
        print("   • Links from user_garments to new tables")
        
        print("\n🎯 Next steps:")
        print("   1. Migrate existing J.Crew data to new structure")
        print("   2. Update scrapers to populate these tables")
        print("   3. Link user feedback to product_master")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error creating tables: {str(e)}")
        return False

def check_existing_tables():
    """Check which tables already exist"""
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        print("\n🔍 Checking existing tables...")
        
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('product_master', 'product_variants', 'brand_product_cache')
        """)
        
        existing = [row[0] for row in cur.fetchall()]
        
        if existing:
            print(f"⚠️  These tables already exist: {', '.join(existing)}")
            return existing
        else:
            print("✅ No conflicting tables found")
            return []
            
    except Exception as e:
        print(f"❌ Error checking tables: {str(e)}")
        return []

if __name__ == "__main__":
    print("🚀 Enhanced Product Data Tables Migration")
    print("=" * 60)
    print("Database: tailor3")
    print("Host: aws-0-us-east-2.pooler.supabase.com")
    print("=" * 60)
    
    # Check for existing tables
    existing = check_existing_tables()
    
    if existing:
        response = input("\n⚠️  Some tables exist. Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("❌ Migration cancelled")
            sys.exit(1)
    
    # Create the tables
    success = create_product_master_tables()
    
    if success:
        print("\n✨ Migration completed successfully!")
        print("📝 Note: Existing data and functionality remain unchanged")
    else:
        print("\n❌ Migration failed. Please check the error above")
        print("💡 Your backup is at: database_dumps/tailor3_dump_2025-09-14_01-59-30.sql")
