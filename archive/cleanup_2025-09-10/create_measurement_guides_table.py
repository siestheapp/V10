#!/usr/bin/env python3
"""
Create the unified measurement_guides table and populate it from existing data
WITHOUT altering any existing tables.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

# Database connection
conn = psycopg2.connect(
    dbname='postgres',
    user='postgres.lbilxlkchzpducggkrxx',
    password='efvTower12',
    host='aws-0-us-east-2.pooler.supabase.com',
    port='6543'
)
cur = conn.cursor(cursor_factory=RealDictCursor)

try:
    # Start transaction
    conn.autocommit = False
    
    print("Creating measurement_guides table...")
    
    # Create the new unified table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS measurement_guides (
            id SERIAL PRIMARY KEY,
            
            -- Core identification
            guide_type TEXT NOT NULL CHECK (guide_type IN ('body', 'garment')),
            brand_id INTEGER REFERENCES brands(id),
            
            -- What this guide applies to
            garment_id INTEGER REFERENCES garments(id),  -- NULL for body guides
            category_id INTEGER REFERENCES categories(id),  -- NULL for garment-specific guides
            subcategory_id INTEGER REFERENCES subcategories(id),
            
            -- Guide metadata
            name TEXT NOT NULL,  -- e.g., "Banana Republic Men's Tops Size Guide" or "NN07 Clive Tee Measurements"
            gender TEXT,
            fit_type TEXT,
            version INTEGER DEFAULT 1,
            
            -- Source information
            source_url TEXT,
            source_type TEXT,  -- 'official_chart', 'product_page', 'customer_service', etc.
            screenshot_path TEXT,
            raw_source_text TEXT,
            
            -- What measurements this guide provides
            measurements_available TEXT[],  -- ['chest', 'waist'] or ['g_chest_width', 'g_sleeve_length']
            unit TEXT DEFAULT 'inches',
            provides_dual_units BOOLEAN DEFAULT false,
            
            -- Tracking fields from original tables
            original_table TEXT,  -- 'size_guides' or 'garment_guides'
            original_id INTEGER,  -- ID from the original table for reference
            
            -- Metadata
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by INTEGER,
            updated_at TIMESTAMP,
            updated_by INTEGER,
            
            -- Constraints
            CHECK (
                (guide_type = 'body' AND category_id IS NOT NULL) OR
                (guide_type = 'garment' AND garment_id IS NOT NULL) OR
                (guide_type = 'garment' AND garment_id IS NULL)  -- Allow for garment guides not yet linked
            )
        );
    """)
    
    # Create indexes for performance
    cur.execute("CREATE INDEX IF NOT EXISTS idx_mg_brand_category ON measurement_guides(brand_id, category_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_mg_garment ON measurement_guides(garment_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_mg_type ON measurement_guides(guide_type);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_mg_original ON measurement_guides(original_table, original_id);")
    
    print("Table created successfully!")
    
    # Migrate data from size_guides
    print("\nMigrating size_guides...")
    cur.execute("""
        INSERT INTO measurement_guides (
            guide_type, brand_id, category_id, subcategory_id,
            name, gender, fit_type, version,
            source_url, source_type, screenshot_path, raw_source_text,
            measurements_available, unit, provides_dual_units,
            notes, created_at, created_by, updated_at, updated_by,
            original_table, original_id
        )
        SELECT 
            'body' as guide_type,
            brand_id, 
            category_id, 
            subcategory_id,
            COALESCE(size_guide_header, 
                     'Size Guide #' || id) as name,
            gender, 
            fit_type, 
            version,
            source_url, 
            CASE 
                WHEN guide_level = 'category_level' THEN 'official_chart'
                WHEN source_url LIKE '%product%' THEN 'product_page'
                ELSE 'official_chart'
            END as source_type,
            screenshot_path, 
            raw_text as raw_source_text,
            measurements_available, 
            unit,
            false as provides_dual_units,  -- size guides don't have this field
            notes, 
            created_at, 
            created_by,
            updated_at,
            updated_by,
            'size_guides' as original_table,
            id as original_id
        FROM size_guides
        WHERE NOT EXISTS (
            SELECT 1 FROM measurement_guides mg 
            WHERE mg.original_table = 'size_guides' 
            AND mg.original_id = size_guides.id
        );
    """)
    
    size_guide_count = cur.rowcount
    print(f"Migrated {size_guide_count} size guides")
    
    # Migrate data from garment_guides
    print("\nMigrating garment_guides...")
    
    # First, find which garments reference each garment_guide
    cur.execute("""
        WITH garment_guide_mapping AS (
            SELECT 
                gg.id as guide_id,
                g.id as garment_id
            FROM garment_guides gg
            LEFT JOIN garments g ON g.garment_guide_id = gg.id
        )
        INSERT INTO measurement_guides (
            guide_type, brand_id, garment_id,
            name, source_url, source_type,
            screenshot_path, raw_source_text,
            measurements_available, unit, provides_dual_units,
            notes, created_at, created_by, updated_at, updated_by,
            original_table, original_id
        )
        SELECT 
            'garment' as guide_type,
            gg.brand_id,
            ggm.garment_id,
            COALESCE(gg.guide_header, 
                     'Garment Guide #' || gg.id) as name,
            gg.source_url,
            COALESCE(gg.info_source, 'product_measurement_table') as source_type,
            gg.screenshot_path,
            gg.raw_source_text,
            gg.measurements_available,
            'inches' as unit,  -- garment guides don't have unit field, default to inches
            COALESCE(gg.provides_dual_units, false),
            gg.notes,
            gg.created_at,
            gg.created_by,
            gg.updated_at,
            gg.updated_by,
            'garment_guides' as original_table,
            gg.id as original_id
        FROM garment_guides gg
        LEFT JOIN garment_guide_mapping ggm ON ggm.guide_id = gg.id
        WHERE NOT EXISTS (
            SELECT 1 FROM measurement_guides mg 
            WHERE mg.original_table = 'garment_guides' 
            AND mg.original_id = gg.id
        );
    """)
    
    garment_guide_count = cur.rowcount
    print(f"Migrated {garment_guide_count} garment guides")
    
    # Show summary
    print("\n=== Migration Summary ===")
    cur.execute("""
        SELECT 
            guide_type,
            COUNT(*) as count,
            COUNT(DISTINCT brand_id) as brands,
            COUNT(DISTINCT category_id) as categories,
            COUNT(DISTINCT garment_id) as garments
        FROM measurement_guides
        GROUP BY guide_type
        ORDER BY guide_type;
    """)
    
    for row in cur.fetchall():
        print(f"{row['guide_type'].capitalize()} guides: {row['count']} total")
        print(f"  - {row['brands']} brands")
        if row['guide_type'] == 'body':
            print(f"  - {row['categories']} categories")
        else:
            print(f"  - {row['garments']} garments")
    
    # Show sample entries
    print("\n=== Sample Entries ===")
    print("\nBody Guide Example:")
    cur.execute("""
        SELECT mg.*, b.name as brand_name, c.name as category_name
        FROM measurement_guides mg
        LEFT JOIN brands b ON mg.brand_id = b.id
        LEFT JOIN categories c ON mg.category_id = c.id
        WHERE guide_type = 'body'
        LIMIT 1;
    """)
    sample = cur.fetchone()
    if sample:
        print(f"  Name: {sample['name']}")
        print(f"  Brand: {sample['brand_name']}")
        print(f"  Category: {sample['category_name']}")
        print(f"  Measurements: {sample['measurements_available']}")
        print(f"  Original: {sample['original_table']} (ID: {sample['original_id']})")
    
    print("\nGarment Guide Example:")
    cur.execute("""
        SELECT mg.*, b.name as brand_name, g.product_name
        FROM measurement_guides mg
        LEFT JOIN brands b ON mg.brand_id = b.id
        LEFT JOIN garments g ON mg.garment_id = g.id
        WHERE guide_type = 'garment'
        LIMIT 1;
    """)
    sample = cur.fetchone()
    if sample:
        print(f"  Name: {sample['name']}")
        print(f"  Brand: {sample['brand_name']}")
        print(f"  Product: {sample['product_name']}")
        print(f"  Measurements: {sample['measurements_available']}")
        print(f"  Original: {sample['original_table']} (ID: {sample['original_id']})")
    
    # Commit the transaction
    conn.commit()
    print("\n✅ Successfully created and populated measurement_guides table!")
    print("✅ Original tables remain unchanged")
    print("\nNext steps:")
    print("1. Verify the data looks correct")
    print("2. Update the measurements table to reference measurement_guides")
    print("3. Update application code to use the new table")
    print("4. Once confirmed working, the original tables can be deprecated")
    
except Exception as e:
    conn.rollback()
    print(f"❌ Error: {e}")
    raise
finally:
    cur.close()
    conn.close()
