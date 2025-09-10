#!/usr/bin/env python3
"""
Remove redundant provides_dual_units column from brands table
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

def remove_brand_dual_units_redundancy():
    """Remove redundant provides_dual_units from brands table"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("🧹 Removing redundant provides_dual_units from brands table...")
        
        # Step 1: Create a view to replace brand-level dual unit functionality
        print("\n1. CREATING BRAND DUAL UNIT VIEW:")
        print("=" * 50)
        
        # First, get the actual brands table structure
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
        
        print("   ✅ Created brands_with_dual_units view")
        
        # Step 2: Test the view
        print("\n2. TESTING REPLACEMENT VIEW:")
        print("=" * 50)
        
        cursor.execute("""
            SELECT 
                id,
                name,
                original_measurement_unit,
                dual_unit_status,
                total_guides,
                dual_guides,
                single_guides
            FROM brands_with_dual_units
            ORDER BY id
        """)
        
        view_test = cursor.fetchall()
        for row in view_test:
            print(f"   Brand {row['id']}: {row['name']}")
            print(f"     original_measurement_unit: {row['original_measurement_unit']}")
            print(f"     dual_unit_status: {row['dual_unit_status']}")
            print(f"     Guides: {row['total_guides']} total, {row['dual_guides']} dual, {row['single_guides']} single")
        
        # Step 3: Drop the view, remove column, then recreate view
        print("\n3. REMOVING REDUNDANT COLUMN:")
        print("=" * 50)
        
        # Drop the view first
        cursor.execute("DROP VIEW IF EXISTS public.brands_with_dual_units")
        print("   ✅ Dropped temporary view")
        
        # Remove the column
        cursor.execute("""
            ALTER TABLE public.brands 
            DROP COLUMN IF EXISTS provides_dual_units;
        """)
        
        print("   ✅ Removed provides_dual_units column")
        
        # Recreate the view without the provides_dual_units column
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
        
        # Step 4: Verify the removal
        print("\n4. VERIFYING REMOVAL:")
        print("=" * 50)
        
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'brands' 
            AND column_name = 'provides_dual_units'
        """)
        
        remaining = cursor.fetchall()
        if not remaining:
            print("   ✅ Column successfully removed")
        else:
            print("   ❌ Column still exists")
        
        # Step 5: Show final brands table structure
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
        
        # Step 6: Show how to get dual unit info now
        print("\n6. HOW TO GET DUAL UNIT INFO NOW:")
        print("=" * 50)
        
        print("Option 1: Use the view for brand-level info")
        print("   SELECT * FROM brands_with_dual_units WHERE dual_unit_status = 'all_dual'")
        
        print("\nOption 2: Query guides directly")
        print("   SELECT DISTINCT b.* FROM brands b")
        print("   JOIN garment_guides gg ON b.id = gg.brand_id")
        print("   WHERE gg.provides_dual_units = true")
        
        print("\nOption 3: Aggregate from guides")
        print("   SELECT")
        print("       b.id, b.name,")
        print("       COUNT(gg.id) as total_guides,")
        print("       COUNT(CASE WHEN gg.provides_dual_units = true THEN 1 END) as dual_guides")
        print("   FROM brands b")
        print("   LEFT JOIN garment_guides gg ON b.id = gg.brand_id")
        print("   GROUP BY b.id, b.name")
        
        # Step 7: Test the new approach
        print("\n7. TESTING NEW APPROACH:")
        print("=" * 50)
        
        # Test getting brands with dual units
        cursor.execute("""
            SELECT 
                id,
                name,
                dual_unit_status
            FROM brands_with_dual_units
            WHERE dual_unit_status IN ('all_dual', 'mixed')
        """)
        
        dual_brands = cursor.fetchall()
        print("Brands with dual unit guides (using view):")
        for brand in dual_brands:
            print(f"   {brand['name']}: {brand['dual_unit_status']}")
        
        # Test getting guides for a specific brand
        cursor.execute("""
            SELECT 
                gg.guide_header,
                gg.provides_dual_units
            FROM garment_guides gg
            JOIN brands b ON gg.brand_id = b.id
            WHERE b.name = 'NN.07'
        """)
        
        nn07_guides = cursor.fetchall()
        print("\nNN.07 guides (guide-level data):")
        for guide in nn07_guides:
            print(f"   {guide['guide_header']}: provides_dual_units = {guide['provides_dual_units']}")
        
        conn.commit()
        print("\n✅ Redundant column removed successfully!")
        
        # Summary of improvements
        print("\n🎯 IMPROVEMENTS MADE:")
        print("   ✅ Removed redundant provides_dual_units from brands table")
        print("   ✅ Created replacement view for brand-level aggregation")
        print("   ✅ Eliminated data duplication")
        print("   ✅ Improved data consistency")
        print("   ✅ Guide-level provides_dual_units is now the single source of truth")
        print("   ✅ Can handle mixed cases (brands with both dual and single guides)")
        
        print("\n📊 FINAL DATA MODEL:")
        print("   • brands: original_measurement_unit (brand's primary unit)")
        print("   • garment_guides: provides_dual_units (guide-level dual unit availability)")
        print("   • garment_guide_entries: measurement_value_in, measurement_value_cm (actual values)")
        print("   • brands_with_dual_units: view for brand-level aggregation")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    remove_brand_dual_units_redundancy()
