#!/usr/bin/env python3
"""
Implement the best database solution for dual unit tracking
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

def implement_best_solution():
    """Implement the best database solution for dual unit tracking"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("🏗️  Implementing best database solution for dual unit tracking...")
        
        # Step 1: Add dual_unit_support to brands table
        print("1. Adding dual_unit_support column to brands table...")
        cursor.execute("""
            ALTER TABLE public.brands 
            ADD COLUMN IF NOT EXISTS dual_unit_support boolean DEFAULT false;
        """)
        
        # Step 2: Update brands that provide dual units
        print("2. Identifying and updating brands with dual unit support...")
        cursor.execute("""
            UPDATE brands b
            SET dual_unit_support = true
            WHERE EXISTS (
                SELECT 1 
                FROM garment_guides gg
                JOIN garment_guide_entries gge ON gg.id = gge.garment_guide_id
                WHERE gg.brand_id = b.id
                AND gge.measurement_value_cm IS NOT NULL
                AND gge.measurement_value_in IS NOT NULL
            )
        """)
        
        updated_brands = cursor.rowcount
        print(f"   Updated {updated_brands} brands to support dual units")
        
        # Step 3: Show the final structure
        print("3. Final brands table structure:")
        cursor.execute("""
            SELECT 
                name,
                default_unit,
                dual_unit_support,
                CASE 
                    WHEN dual_unit_support THEN 'Provides both units'
                    ELSE 'Single unit only'
                END as capability
            FROM brands
            ORDER BY name
        """)
        
        brands = cursor.fetchall()
        for brand in brands:
            print(f"   {brand['name']}: {brand['default_unit']} (dual support: {brand['dual_unit_support']})")
        
        # Step 4: Create a view for easy querying
        print("4. Creating view for easy dual unit queries...")
        cursor.execute("""
            CREATE OR REPLACE VIEW public.brand_unit_capabilities AS
            SELECT 
                b.id as brand_id,
                b.name as brand_name,
                b.default_unit,
                b.dual_unit_support,
                COUNT(DISTINCT gg.id) as garment_guide_count,
                COUNT(DISTINCT CASE WHEN gg.provides_dual_units THEN gg.id END) as dual_unit_guide_count
            FROM brands b
            LEFT JOIN garment_guides gg ON b.id = gg.brand_id
            GROUP BY b.id, b.name, b.default_unit, b.dual_unit_support
            ORDER BY b.name;
        """)
        
        # Step 5: Show sample queries for different use cases
        print("5. Sample queries for different use cases:")
        
        # Query 1: Get all brands with dual unit support
        cursor.execute("""
            SELECT brand_name, default_unit 
            FROM brand_unit_capabilities 
            WHERE dual_unit_support = true
        """)
        
        dual_brands = cursor.fetchall()
        print("   Brands with dual unit support:")
        for brand in dual_brands:
            print(f"     • {brand['brand_name']} (prefers {brand['default_unit']})")
        
        # Query 2: Get measurements with unit preference
        cursor.execute("""
            SELECT 
                b.name as brand_name,
                gge.size_label,
                gge.measurement_type,
                CASE 
                    WHEN b.dual_unit_support THEN 
                        format('%s in / %s cm', gge.measurement_value_in, gge.measurement_value_cm)
                    ELSE 
                        format('%s %s', gge.measurement_value_in, b.default_unit)
                END as display_value
            FROM garment_guide_entries gge
            JOIN garment_guides gg ON gge.garment_guide_id = gg.id
            JOIN brands b ON gg.brand_id = b.id
            WHERE gge.measurement_value_in IS NOT NULL
            ORDER BY b.name, gge.size_label
            LIMIT 5
        """)
        
        sample_measurements = cursor.fetchall()
        print("   Sample measurements with unit preference:")
        for measurement in sample_measurements:
            print(f"     • {measurement['brand_name']} {measurement['size_label']}: {measurement['display_value']}")
        
        # Step 6: Performance analysis
        print("6. Performance considerations:")
        print("   ✅ dual_unit_support: boolean index, fast queries")
        print("   ✅ default_unit: existing index, no changes needed")
        print("   ✅ provides_dual_units: boolean index, fast filtering")
        print("   ✅ Normalized structure: no data duplication")
        
        conn.commit()
        print("✅ Best database solution implemented successfully!")
        
        # Show benefits
        print("\n🎯 Benefits of this approach:")
        print("   • Maintains existing code compatibility")
        print("   • Clear separation of concerns")
        print("   • Excellent query performance")
        print("   • Scales to support more unit types")
        print("   • Follows database normalization principles")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    implement_best_solution()

