#!/usr/bin/env python3
"""
Add dual unit tracking to garment_guides table
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('src/ios_app/Backend/.env')

def get_db_connection():
    """Get database connection using environment variables or defaults"""
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "aws-0-us-east-2.pooler.supabase.com"),
        port=os.getenv("DB_PORT", "6543"),
        database=os.getenv("DB_NAME", "postgres"),
        user=os.getenv("DB_USER", "postgres.lbilxlkchzpducggkrxx"),
        password=os.getenv("DB_PASSWORD", "efvTower12"),
        cursor_factory=RealDictCursor
    )

def add_dual_unit_tracking():
    """Add dual unit tracking to garment_guides"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("📊 Adding dual unit tracking...")
        
        # Step 1: Add column to garment_guides
        print("1. Adding provides_dual_units column to garment_guides...")
        cursor.execute("""
            ALTER TABLE public.garment_guides 
            ADD COLUMN IF NOT EXISTS provides_dual_units boolean DEFAULT false;
        """)
        
        # Step 2: Check current brands table structure
        print("2. Current brands table structure:")
        cursor.execute("""
            SELECT column_name, data_type, column_default
            FROM information_schema.columns 
            WHERE table_name = 'brands' 
            AND column_name = 'default_unit'
        """)
        
        brand_unit_col = cursor.fetchone()
        if brand_unit_col:
            print(f"   {brand_unit_col['column_name']}: {brand_unit_col['data_type']} (default: {brand_unit_col['column_default']})")
        
        # Step 3: Show current brand data
        print("3. Current brand default units:")
        cursor.execute("""
            SELECT id, name, default_unit
            FROM brands
            ORDER BY name
        """)
        
        brands = cursor.fetchall()
        for brand in brands:
            print(f"   {brand['name']}: {brand['default_unit']}")
        
        # Step 4: Identify which garment guides have dual units
        print("4. Analyzing garment guides for dual units...")
        cursor.execute("""
            SELECT 
                gg.id,
                gg.guide_header,
                b.name as brand_name,
                COUNT(DISTINCT gge.unit) as unit_count,
                ARRAY_AGG(DISTINCT gge.unit) as units_provided
            FROM garment_guides gg
            LEFT JOIN brands b ON gg.brand_id = b.id
            LEFT JOIN garment_guide_entries gge ON gg.id = gge.garment_guide_id
            GROUP BY gg.id, gg.guide_header, b.name
            HAVING COUNT(DISTINCT gge.unit) > 0
            ORDER BY b.name, gg.id
        """)
        
        guides = cursor.fetchall()
        print("   Garment guides analysis:")
        for guide in guides:
            print(f"   Guide {guide['id']} ({guide['brand_name']}): {guide['units_provided']} units")
        
        # Step 5: Update garment guides that have dual units
        print("5. Updating garment guides with dual units...")
        cursor.execute("""
            UPDATE garment_guides gg
            SET provides_dual_units = true
            WHERE EXISTS (
                SELECT 1 
                FROM garment_guide_entries gge 
                WHERE gge.garment_guide_id = gg.id 
                AND gge.measurement_value_cm IS NOT NULL
                AND gge.measurement_value_in IS NOT NULL
            )
        """)
        
        updated_guides = cursor.rowcount
        print(f"   Updated {updated_guides} garment guides to provide dual units")
        
        # Step 6: Show final results
        print("6. Final garment guides with dual units:")
        cursor.execute("""
            SELECT 
                gg.id,
                gg.guide_header,
                b.name as brand_name,
                gg.provides_dual_units,
                COUNT(gge.id) as measurement_count
            FROM garment_guides gg
            LEFT JOIN brands b ON gg.brand_id = b.id
            LEFT JOIN garment_guide_entries gge ON gg.id = gge.garment_guide_id
            WHERE gg.provides_dual_units = true
            GROUP BY gg.id, gg.guide_header, b.name, gg.provides_dual_units
            ORDER BY b.name
        """)
        
        dual_unit_guides = cursor.fetchall()
        for guide in dual_unit_guides:
            print(f"   {guide['brand_name']} - {guide['guide_header']}: {guide['measurement_count']} measurements")
        
        # Step 7: Consider updating brands table
        print("7. Brands that provide dual units but have single unit default:")
        cursor.execute("""
            SELECT DISTINCT
                b.id,
                b.name,
                b.default_unit,
                'Should consider updating default_unit or adding dual_unit_support' as recommendation
            FROM brands b
            JOIN garment_guides gg ON b.id = gg.brand_id
            WHERE gg.provides_dual_units = true
            ORDER BY b.name
        """)
        
        brands_to_update = cursor.fetchall()
        for brand in brands_to_update:
            print(f"   {brand['name']}: default_unit = {brand['default_unit']} (but provides dual units)")
        
        conn.commit()
        print("✅ Dual unit tracking added successfully!")
        
        # Show recommendations
        print("\n🎯 Recommendations:")
        print("   • Consider adding 'dual_unit_support' column to brands table")
        print("   • Update brands.default_unit to reflect primary unit preference")
        print("   • Use provides_dual_units in UI to show both units when available")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    add_dual_unit_tracking()

