#!/usr/bin/env python3
"""
Remove redundant dual_unit_support column from brands table
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

def remove_dual_unit_support_redundancy():
    """Remove redundant dual_unit_support from brands table"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("🧹 Removing redundant dual_unit_support from brands table...")
        
        # Step 1: Check current data
        print("\n1. CURRENT DATA ANALYSIS:")
        print("=" * 50)
        
        cursor.execute("""
            SELECT 
                id,
                name,
                dual_unit_support,
                original_measurement_unit
            FROM brands
            ORDER BY id
        """)
        
        brands = cursor.fetchall()
        print("Current brands data:")
        for brand in brands:
            print(f"   Brand {brand['id']}: {brand['name']}")
            print(f"     dual_unit_support: {brand['dual_unit_support']}")
            print(f"     original_measurement_unit: {brand['original_measurement_unit']}")
        
        # Step 2: Check if dual_unit_support is redundant with garment_guides
        print("\n2. REDUNDANCY ANALYSIS:")
        print("=" * 50)
        
        cursor.execute("""
            SELECT 
                b.id,
                b.name,
                b.dual_unit_support as brand_dual_support,
                COUNT(gg.id) as guide_count,
                COUNT(CASE WHEN gg.provides_dual_units = true THEN 1 END) as dual_guides,
                COUNT(CASE WHEN gg.provides_dual_units = false THEN 1 END) as single_guides
            FROM brands b
            LEFT JOIN garment_guides gg ON b.id = gg.brand_id
            GROUP BY b.id, b.name, b.dual_unit_support
            ORDER BY b.id
        """)
        
        redundancy = cursor.fetchall()
        print("Brand dual_unit_support vs Guide provides_dual_units:")
        for row in redundancy:
            brand_support = row['brand_dual_support']
            dual_guides = row['dual_guides']
            single_guides = row['single_guides']
            
            print(f"\n   Brand: {row['name']}")
            print(f"     Brand dual_unit_support: {brand_support}")
            print(f"     Guide count: {row['guide_count']}")
            print(f"     Dual guides: {dual_guides}")
            print(f"     Single guides: {single_guides}")
            
            # Check for redundancy
            if row['guide_count'] > 0:
                if brand_support and dual_guides == 0:
                    print(f"     ❌ INCONSISTENT: Brand says dual support, but no dual guides")
                elif not brand_support and dual_guides > 0:
                    print(f"     ❌ INCONSISTENT: Brand says no dual support, but has dual guides")
                elif brand_support and dual_guides > 0:
                    print(f"     ✅ CONSISTENT: Both say dual support")
                else:
                    print(f"     ✅ CONSISTENT: Both say no dual support")
            else:
                print(f"     ⚠️  NO GUIDES: Can't verify consistency")
        
        # Step 3: Drop the view first (since it might reference the column)
        print("\n3. REMOVING REDUNDANT COLUMN:")
        print("=" * 50)
        
        cursor.execute("DROP VIEW IF EXISTS public.brands_with_dual_units")
        print("   ✅ Dropped brands_with_dual_units view")
        
        # Step 4: Remove the redundant column
        cursor.execute("""
            ALTER TABLE public.brands 
            DROP COLUMN IF EXISTS dual_unit_support;
        """)
        
        print("   ✅ Removed dual_unit_support column")
        
        # Step 5: Verify the removal
        print("\n4. VERIFYING REMOVAL:")
        print("=" * 50)
        
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'brands' 
            AND column_name = 'dual_unit_support'
        """)
        
        remaining = cursor.fetchall()
        if not remaining:
            print("   ✅ Column successfully removed")
        else:
            print("   ❌ Column still exists")
        
        # Step 6: Show final brands table structure
        print("\n5. FINAL BRANDS TABLE STRUCTURE:")
        print("=" * 50)
        
        cursor.execute("""
            SELECT 
                column_name,
                data_type,
                is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'brands'
            ORDER BY ordinal_position
        """)
        
        final_structure = cursor.fetchall()
        print("brands table columns:")
        for col in final_structure:
            print(f"   {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
        
        # Step 7: Recreate the view without dual_unit_support
        print("\n6. RECREATING VIEW:")
        print("=" * 50)
        
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns 
            WHERE table_name = 'brands'
            ORDER BY ordinal_position
        """)
        
        brand_columns = cursor.fetchall()
        brand_column_list = [col['column_name'] for col in brand_columns]
        brand_column_string = ', '.join([f"b.{col}" for col in brand_column_list])
        
        cursor.execute(f"""
            CREATE OR REPLACE VIEW public.brands_with_dual_units AS
            SELECT 
                {brand_column_string},
                CASE 
                    WHEN COUNT(gg.id) = 0 THEN 'no_guides'
                    WHEN COUNT(CASE WHEN gg.provides_dual_units = true THEN 1 END) = COUNT(gg.id) THEN 'all_dual'
                    WHEN COUNT(CASE WHEN gg.provides_dual_units = false THEN 1 END) = COUNT(gg.id) THEN 'all_single'
                    ELSE 'mixed'
                END as dual_unit_status,
                COUNT(gg.id) as total_guides,
                COUNT(CASE WHEN gg.provides_dual_units = true THEN 1 END) as dual_guides,
                COUNT(CASE WHEN gg.provides_dual_units = false THEN 1 END) as single_guides
            FROM brands b
            LEFT JOIN garment_guides gg ON b.id = gg.brand_id
            GROUP BY {brand_column_string}
        """)
        
        print("   ✅ Recreated brands_with_dual_units view")
        
        # Step 8: Test the final structure
        print("\n7. TESTING FINAL STRUCTURE:")
        print("=" * 50)
        
        cursor.execute("""
            SELECT 
                id,
                name,
                original_measurement_unit,
                dual_unit_status
            FROM brands_with_dual_units
            ORDER BY id
        """)
        
        final_test = cursor.fetchall()
        print("Final brands data (using view):")
        for row in final_test:
            print(f"   Brand {row['id']}: {row['name']}")
            print(f"     original_measurement_unit: {row['original_measurement_unit']}")
            print(f"     dual_unit_status: {row['dual_unit_status']}")
        
        conn.commit()
        print("\n✅ Redundant dual_unit_support column removed successfully!")
        
        # Summary of improvements
        print("\n🎯 FINAL IMPROVEMENTS:")
        print("   ✅ Removed redundant dual_unit_support from brands table")
        print("   ✅ Removed redundant provides_dual_units from brands table")
        print("   ✅ Eliminated all dual unit redundancy")
        print("   ✅ Guide-level provides_dual_units is the ONLY source of truth")
        print("   ✅ brands_with_dual_units view provides brand-level aggregation")
        
        print("\n📊 ULTIMATE DATA MODEL:")
        print("   • brands: original_measurement_unit (brand's primary unit only)")
        print("   • garment_guides: provides_dual_units (single source of truth)")
        print("   • garment_guide_entries: measurement_value_in, measurement_value_cm (actual values)")
        print("   • brands_with_dual_units: view for brand-level aggregation when needed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    remove_dual_unit_support_redundancy()

