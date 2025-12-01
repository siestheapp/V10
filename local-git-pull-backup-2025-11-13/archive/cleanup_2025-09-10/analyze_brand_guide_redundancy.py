#!/usr/bin/env python3
"""
Analyze redundancy between brands and garment_guides tables for dual unit tracking
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

def analyze_brand_guide_redundancy():
    """Analyze redundancy between brands and garment_guides tables"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("🔍 Analyzing redundancy between brands and garment_guides tables...")
        
        # Check current data
        print("\n1. CURRENT DATA ANALYSIS:")
        print("=" * 60)
        
        # Check brands table
        cursor.execute("""
            SELECT 
                id,
                name,
                original_measurement_unit,
                provides_dual_units
            FROM brands
            ORDER BY id
        """)
        
        brands = cursor.fetchall()
        print("brands table:")
        for brand in brands:
            print(f"   Brand {brand['id']}: {brand['name']}")
            print(f"     original_measurement_unit: {brand['original_measurement_unit']}")
            print(f"     provides_dual_units: {brand['provides_dual_units']}")
        
        # Check garment_guides table
        cursor.execute("""
            SELECT 
                gg.id,
                gg.guide_header,
                gg.provides_dual_units,
                b.name as brand_name
            FROM garment_guides gg
            LEFT JOIN brands b ON gg.brand_id = b.id
            ORDER BY gg.id
        """)
        
        guides = cursor.fetchall()
        print("\ngarment_guides table:")
        for guide in guides:
            print(f"   Guide {guide['id']}: {guide['guide_header']} (Brand: {guide['brand_name']})")
            print(f"     provides_dual_units: {guide['provides_dual_units']}")
        
        # Check for inconsistencies
        print("\n2. CONSISTENCY ANALYSIS:")
        print("=" * 60)
        
        cursor.execute("""
            SELECT 
                b.id as brand_id,
                b.name as brand_name,
                b.original_measurement_unit as brand_original_unit,
                b.provides_dual_units as brand_dual_units,
                COUNT(gg.id) as guide_count,
                COUNT(CASE WHEN gg.provides_dual_units = true THEN 1 END) as dual_unit_guides,
                COUNT(CASE WHEN gg.provides_dual_units = false THEN 1 END) as single_unit_guides
            FROM brands b
            LEFT JOIN garment_guides gg ON b.id = gg.brand_id
            GROUP BY b.id, b.name, b.original_measurement_unit, b.provides_dual_units
            ORDER BY b.id
        """)
        
        consistency = cursor.fetchall()
        print("Brand vs Guide consistency:")
        for row in consistency:
            brand_dual = row['brand_dual_units']
            guide_dual_count = row['dual_unit_guides']
            guide_single_count = row['single_unit_guides']
            
            print(f"\n   Brand: {row['brand_name']}")
            print(f"     Brand provides_dual_units: {brand_dual}")
            print(f"     Guide count: {row['guide_count']}")
            print(f"     Dual unit guides: {guide_dual_count}")
            print(f"     Single unit guides: {guide_single_count}")
            
            # Check for inconsistencies
            if row['guide_count'] > 0:
                if brand_dual and guide_dual_count == 0:
                    print(f"     ❌ INCONSISTENT: Brand says dual, but no dual guides")
                elif not brand_dual and guide_dual_count > 0:
                    print(f"     ❌ INCONSISTENT: Brand says single, but has dual guides")
                elif brand_dual and guide_single_count > 0:
                    print(f"     ⚠️  MIXED: Brand says dual, but has both dual and single guides")
                else:
                    print(f"     ✅ CONSISTENT")
        
        # Check if we can derive brand-level info from guides
        print("\n3. DERIVATION ANALYSIS:")
        print("=" * 60)
        
        cursor.execute("""
            SELECT 
                b.id as brand_id,
                b.name as brand_name,
                COUNT(gg.id) as total_guides,
                COUNT(CASE WHEN gg.provides_dual_units = true THEN 1 END) as dual_guides,
                COUNT(CASE WHEN gg.provides_dual_units = false THEN 1 END) as single_guides,
                CASE 
                    WHEN COUNT(gg.id) = 0 THEN 'no_guides'
                    WHEN COUNT(CASE WHEN gg.provides_dual_units = true THEN 1 END) = COUNT(gg.id) THEN 'all_dual'
                    WHEN COUNT(CASE WHEN gg.provides_dual_units = false THEN 1 END) = COUNT(gg.id) THEN 'all_single'
                    ELSE 'mixed'
                END as derived_dual_unit_status
            FROM brands b
            LEFT JOIN garment_guides gg ON b.id = gg.brand_id
            GROUP BY b.id, b.name
            ORDER BY b.id
        """)
        
        derivation = cursor.fetchall()
        print("Can we derive brand dual unit status from guides?")
        for row in derivation:
            print(f"\n   Brand: {row['brand_name']}")
            print(f"     Total guides: {row['total_guides']}")
            print(f"     Dual guides: {row['dual_guides']}")
            print(f"     Single guides: {row['single_guides']}")
            print(f"     Derived status: {row['derived_dual_unit_status']}")
        
        # Check original_measurement_unit logic
        print("\n4. ORIGINAL_MEASUREMENT_UNIT ANALYSIS:")
        print("=" * 60)
        
        cursor.execute("""
            SELECT 
                b.id as brand_id,
                b.name as brand_name,
                b.original_measurement_unit,
                COUNT(gg.id) as guide_count,
                COUNT(CASE WHEN gg.provides_dual_units = true THEN 1 END) as dual_guides
            FROM brands b
            LEFT JOIN garment_guides gg ON b.id = gg.brand_id
            GROUP BY b.id, b.name, b.original_measurement_unit
            ORDER BY b.id
        """)
        
        original_units = cursor.fetchall()
        print("Original measurement unit analysis:")
        for row in original_units:
            print(f"\n   Brand: {row['brand_name']}")
            print(f"     original_measurement_unit: {row['original_measurement_unit']}")
            print(f"     Guide count: {row['guide_count']}")
            print(f"     Dual guides: {row['dual_guides']}")
            
            # Check if original_measurement_unit makes sense
            if row['original_measurement_unit'] == 'cm' and row['dual_guides'] == 0:
                print(f"     ⚠️  European brand (cm) but no dual unit guides")
            elif row['original_measurement_unit'] == 'in' and row['dual_guides'] > 0:
                print(f"     ⚠️  US brand (in) but has dual unit guides")
        
        # Recommendations
        print("\n5. RECOMMENDATIONS:")
        print("=" * 60)
        
        print("Analysis:")
        print("   • Brands table has original_measurement_unit and provides_dual_units")
        print("   • Garment_guides table has provides_dual_units")
        print("   • This creates redundancy and potential inconsistencies")
        
        print("\nProblems:")
        print("   ❌ Redundant data storage")
        print("   ❌ Potential inconsistencies between brand and guide level")
        print("   ❌ Brand might not provide dual units in all guides")
        print("   ❌ Harder to maintain data consistency")
        
        print("\nSolutions:")
        print("   1. Remove dual unit tracking from brands table")
        print("   2. Keep only guide-level provides_dual_units")
        print("   3. Derive brand-level info from guides when needed")
        print("   4. Keep original_measurement_unit only if truly needed")
        
        print("\nRecommendation:")
        print("   🎯 REMOVE provides_dual_units FROM brands TABLE")
        print("   Reasons:")
        print("   1. Guide-level is more accurate (brands can have mixed guides)")
        print("   2. Eliminates redundancy")
        print("   3. Prevents inconsistencies")
        print("   4. Simpler data model")
        print("   5. Can always aggregate up to brand level if needed")
        
        conn.commit()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    analyze_brand_guide_redundancy()

