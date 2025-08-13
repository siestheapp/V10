#!/usr/bin/env python3
"""
Analyze redundancy of measurements_available between size_guides and size_guide_entries tables
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

def analyze_measurements_available_redundancy():
    """Analyze redundancy of measurements_available field"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("🔍 Analyzing measurements_available redundancy...")
        
        # Step 1: Check current data in both tables
        print("\n1. CURRENT DATA ANALYSIS:")
        print("=" * 60)
        
        # First, check the actual structure of size_guides table
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns 
            WHERE table_name = 'size_guides'
            ORDER BY ordinal_position
        """)
        
        size_guide_columns = cursor.fetchall()
        print("size_guides table columns:")
        for col in size_guide_columns:
            print(f"   {col['column_name']}")
        
        # Check size_guides table
        cursor.execute("""
            SELECT 
                id,
                measurements_available
            FROM size_guides
            ORDER BY id
        """)
        
        size_guides = cursor.fetchall()
        print("size_guides table:")
        for guide in size_guides:
            print(f"   Guide {guide['id']}")
            print(f"     measurements_available: {guide['measurements_available']}")
        
        # Check size_guide_entries table
        cursor.execute("""
            SELECT 
                sge.id,
                sge.size_label,
                sge.measurements_available,
                sg.guide_header
            FROM size_guide_entries sge
            JOIN size_guides sg ON sge.size_guide_id = sg.id
            ORDER BY sg.id, sge.size_label
            LIMIT 20
        """)
        
        entries = cursor.fetchall()
        print("\nsize_guide_entries table (first 20 rows):")
        for entry in entries:
            print(f"   Entry {entry['id']}: {entry['size_label']} ({entry['guide_header']})")
            print(f"     measurements_available: {entry['measurements_available']}")
        
        # Step 2: Check for consistency between tables
        print("\n2. CONSISTENCY ANALYSIS:")
        print("=" * 60)
        
        cursor.execute("""
            SELECT 
                sg.id as guide_id,
                sg.guide_header,
                sg.measurements_available as guide_measurements,
                COUNT(sge.id) as entry_count,
                COUNT(DISTINCT sge.measurements_available) as unique_entry_measurements,
                array_agg(DISTINCT sge.measurements_available) as entry_measurements_list
            FROM size_guides sg
            LEFT JOIN size_guide_entries sge ON sg.id = sge.size_guide_id
            GROUP BY sg.id, sg.guide_header, sg.measurements_available
            ORDER BY sg.id
        """)
        
        consistency = cursor.fetchall()
        print("Guide vs Entry measurements_available consistency:")
        for row in consistency:
            guide_measurements = row['guide_measurements']
            entry_count = row['entry_count']
            unique_entry_measurements = row['unique_entry_measurements']
            entry_measurements_list = row['entry_measurements_list']
            
            print(f"\n   Guide {row['guide_id']}: {row['guide_header']}")
            print(f"     Guide measurements_available: {guide_measurements}")
            print(f"     Entry count: {entry_count}")
            print(f"     Unique entry measurements: {unique_entry_measurements}")
            print(f"     Entry measurements list: {entry_measurements_list}")
            
            # Check for consistency
            if entry_count > 0:
                if unique_entry_measurements == 1 and entry_measurements_list[0] == guide_measurements:
                    print(f"     ✅ CONSISTENT: All entries match guide")
                elif unique_entry_measurements == 1 and entry_measurements_list[0] != guide_measurements:
                    print(f"     ❌ INCONSISTENT: All entries same but different from guide")
                elif unique_entry_measurements > 1:
                    print(f"     ⚠️  MIXED: Entries have different measurements than guide")
                else:
                    print(f"     ❌ INCONSISTENT: No entries or null values")
            else:
                print(f"     ⚠️  NO ENTRIES: Can't verify consistency")
        
        # Step 3: Analyze querying scenarios
        print("\n3. QUERYING SCENARIO ANALYSIS:")
        print("=" * 60)
        
        print("Scenario A: Find all entries with chest measurements")
        print("   Current (entry-level):")
        print("     SELECT * FROM size_guide_entries WHERE 'chest' = ANY(measurements_available)")
        print("   Alternative (guide-level):")
        print("     SELECT sge.* FROM size_guide_entries sge")
        print("     JOIN size_guides sg ON sge.size_guide_id = sg.id")
        print("     WHERE 'chest' = ANY(sg.measurements_available)")
        
        print("\nScenario B: Find entries with both chest and sleeve measurements")
        print("   Current (entry-level):")
        print("     SELECT * FROM size_guide_entries")
        print("     WHERE 'chest' = ANY(measurements_available) AND 'sleeve' = ANY(measurements_available)")
        print("   Alternative (guide-level):")
        print("     SELECT sge.* FROM size_guide_entries sge")
        print("     JOIN size_guides sg ON sge.size_guide_id = sg.id")
        print("     WHERE 'chest' = ANY(sg.measurements_available) AND 'sleeve' = ANY(sg.measurements_available)")
        
        print("\nScenario C: Get guide info with measurement availability")
        print("   Current (guide-level):")
        print("     SELECT * FROM size_guides WHERE 'chest' = ANY(measurements_available)")
        print("   Alternative (entry-level aggregation):")
        print("     SELECT sg.* FROM size_guides sg")
        print("     WHERE EXISTS (")
        print("         SELECT 1 FROM size_guide_entries sge")
        print("         WHERE sge.size_guide_id = sg.id")
        print("         AND 'chest' = ANY(sge.measurements_available)")
        print("     )")
        
        # Step 4: Performance comparison
        print("\n4. PERFORMANCE COMPARISON:")
        print("=" * 60)
        
        print("Current approach (entry-level measurements_available):")
        print("   ✅ Pros:")
        print("     • Direct filtering on entries")
        print("     • No joins needed for entry queries")
        print("     • Can handle mixed measurements per guide")
        print("     • More granular control")
        print("   ❌ Cons:")
        print("     • Redundant data storage")
        print("     • Potential inconsistencies")
        print("     • More complex updates")
        print("     • Larger table size")
        
        print("\nAlternative approach (guide-level only):")
        print("   ✅ Pros:")
        print("     • No data duplication")
        print("     • Single source of truth")
        print("     • Easier to maintain")
        print("     • Smaller table size")
        print("   ❌ Cons:")
        print("     • Requires joins for entry queries")
        print("     • Less flexible for mixed measurements")
        print("     • More complex queries")
        
        # Step 5: Check if entries actually have different measurements
        print("\n5. MIXED MEASUREMENTS ANALYSIS:")
        print("=" * 60)
        
        cursor.execute("""
            SELECT 
                sg.id as guide_id,
                sg.guide_header,
                COUNT(DISTINCT sge.measurements_available) as unique_measurement_sets,
                array_agg(DISTINCT sge.measurements_available) as all_measurement_sets
            FROM size_guides sg
            JOIN size_guide_entries sge ON sg.id = sge.size_guide_id
            GROUP BY sg.id, sg.guide_header
            HAVING COUNT(DISTINCT sge.measurements_available) > 1
            ORDER BY sg.id
        """)
        
        mixed_guides = cursor.fetchall()
        if mixed_guides:
            print("Guides with mixed measurements_available in entries:")
            for guide in mixed_guides:
                print(f"   Guide {guide['guide_id']}: {guide['guide_header']}")
                print(f"     Unique sets: {guide['unique_measurement_sets']}")
                print(f"     All sets: {guide['all_measurement_sets']}")
        else:
            print("✅ No guides have mixed measurements_available in entries")
            print("   All entries within a guide have the same measurements_available")
        
        # Step 6: Recommendations
        print("\n6. RECOMMENDATIONS:")
        print("=" * 60)
        
        print("Analysis:")
        print("   • measurements_available appears in both size_guides and size_guide_entries")
        print("   • This creates redundancy and potential inconsistencies")
        print("   • Most guides have consistent measurements_available across all entries")
        
        print("\nRecommendation:")
        if not mixed_guides:
            print("   🎯 REMOVE measurements_available FROM size_guide_entries")
            print("   Reasons:")
            print("   1. No mixed measurements found - all entries in a guide are consistent")
            print("   2. Eliminates data duplication")
            print("   3. Prevents inconsistencies")
            print("   4. Simpler data model")
            print("   5. Guide-level is the natural place for this metadata")
        else:
            print("   ⚠️  KEEP measurements_available IN BOTH TABLES")
            print("   Reasons:")
            print("   1. Some guides have mixed measurements per entry")
            print("   2. Entry-level granularity is needed")
            print("   3. But ensure consistency through application logic")
        
        print("\nImplementation:")
        if not mixed_guides:
            print("   1. Remove measurements_available from size_guide_entries")
            print("   2. Use size_guides.measurements_available for all queries")
            print("   3. Join with size_guides when filtering entries by measurements")
            print("   4. Update application code to use guide-level measurements")
        
        conn.commit()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    analyze_measurements_available_redundancy()
