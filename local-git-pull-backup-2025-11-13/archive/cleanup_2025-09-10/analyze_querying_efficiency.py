#!/usr/bin/env python3
"""
Analyze querying efficiency for dual unit tracking
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

def analyze_querying_efficiency():
    """Analyze querying efficiency for different approaches"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("🔍 Analyzing querying efficiency for dual unit tracking...")
        
        # Scenario: User prefers inches, app needs to get measurements in inches
        print("\n📊 SCENARIO: User prefers inches, app needs inch measurements")
        print("=" * 70)
        
        # Current approach (entry-level)
        print("\n1. CURRENT APPROACH (entry-level measurement_source_type):")
        print("-" * 50)
        
        cursor.execute("""
            SELECT 
                gge.size_label,
                gge.measurement_type,
                gge.measurement_value_in,
                gge.measurement_source_type
            FROM garment_guide_entries gge
            JOIN garment_guides gg ON gge.garment_guide_id = gg.id
            WHERE gg.id = 1
            ORDER BY gge.size_label, gge.measurement_type
        """)
        
        current_results = cursor.fetchall()
        print("Query result (15 rows, each with measurement_source_type):")
        for row in current_results:
            print(f"   {row['size_label']} {row['measurement_type']}: {row['measurement_value_in']}in ({row['measurement_source_type']})")
        
        # Alternative approach (guide-level)
        print("\n2. ALTERNATIVE APPROACH (guide-level provides_dual_units):")
        print("-" * 50)
        
        cursor.execute("""
            SELECT 
                gg.id,
                gg.guide_header,
                gg.provides_dual_units
            FROM garment_guides gg
            WHERE gg.id = 1
        """)
        
        guide_info = cursor.fetchone()
        print(f"Guide info: {guide_info['guide_header']} - provides_dual_units: {guide_info['provides_dual_units']}")
        
        cursor.execute("""
            SELECT 
                gge.size_label,
                gge.measurement_type,
                gge.measurement_value_in
            FROM garment_guide_entries gge
            JOIN garment_guides gg ON gge.garment_guide_id = gg.id
            WHERE gg.id = 1
            ORDER BY gge.size_label, gge.measurement_type
        """)
        
        alt_results = cursor.fetchall()
        print("Query result (15 rows, no redundant measurement_source_type):")
        for row in alt_results:
            print(f"   {row['size_label']} {row['measurement_type']}: {row['measurement_value_in']}in")
        
        # Performance comparison
        print("\n3. PERFORMANCE COMPARISON:")
        print("-" * 50)
        
        print("Current approach (entry-level):")
        print("   ✅ Pros:")
        print("     • More granular - can handle mixed cases")
        print("     • Closer to actual data")
        print("   ❌ Cons:")
        print("     • Redundant data in every row")
        print("     • More complex queries")
        print("     • Larger result sets")
        print("     • More storage space")
        
        print("\nAlternative approach (guide-level):")
        print("   ✅ Pros:")
        print("     • Single flag per guide")
        print("     • Simpler queries")
        print("     • Smaller result sets")
        print("     • Less storage space")
        print("     • Better for user preference filtering")
        print("   ❌ Cons:")
        print("     • Less granular")
        print("     • Assumes all entries in guide have same unit availability")
        
        # Real-world query scenarios
        print("\n4. REAL-WORLD QUERY SCENARIOS:")
        print("-" * 50)
        
        print("Scenario A: Get all guides that provide dual units")
        print("   Current: SELECT DISTINCT gg.* FROM garment_guides gg")
        print("            JOIN garment_guide_entries gge ON gg.id = gge.garment_guide_id")
        print("            WHERE gge.measurement_source_type = 'provided_both'")
        print("   Alternative: SELECT * FROM garment_guides WHERE provides_dual_units = true")
        
        print("\nScenario B: Get measurements for user who prefers inches")
        print("   Current: SELECT gge.* FROM garment_guide_entries gge")
        print("            JOIN garment_guides gg ON gge.garment_guide_id = gg.id")
        print("            WHERE gge.measurement_value_in IS NOT NULL")
        print("   Alternative: SELECT gge.* FROM garment_guide_entries gge")
        print("                JOIN garment_guides gg ON gge.garment_guide_id = gg.id")
        print("                WHERE gge.measurement_value_in IS NOT NULL")
        print("                (Same query, but guide-level flag available for filtering)")
        
        print("\nScenario C: Filter guides by unit preference")
        print("   Current: Complex aggregation query")
        print("   Alternative: Simple WHERE clause on guide table")
        
        # Recommendation
        print("\n5. RECOMMENDATION:")
        print("-" * 50)
        
        print("For your use case (user preference = inches, app uses inches):")
        print("   🎯 GO BACK TO GUIDE-LEVEL STORAGE")
        print("   Reasons:")
        print("   1. Simpler queries for user preference filtering")
        print("   2. Better performance for guide-level operations")
        print("   3. Less redundant data")
        print("   4. More intuitive for app logic")
        print("   5. Easier to maintain consistency")
        
        print("\nImplementation:")
        print("   1. Add provides_dual_units back to garment_guides")
        print("   2. Remove measurement_source_type from garment_guide_entries")
        print("   3. Use guide-level flag for all dual unit logic")
        
        conn.commit()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    analyze_querying_efficiency()

