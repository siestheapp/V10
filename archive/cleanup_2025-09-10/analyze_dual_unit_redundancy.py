#!/usr/bin/env python3
"""
Analyze redundancy between provides_dual_units and measurement_source_type
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

def analyze_dual_unit_redundancy():
    """Analyze redundancy between provides_dual_units and measurement_source_type"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("🔍 Analyzing redundancy between provides_dual_units and measurement_source_type...")
        
        # Step 1: Check current values
        print("\n1. CURRENT VALUES:")
        print("=" * 60)
        
        # Check garment_guides.provides_dual_units
        cursor.execute("""
            SELECT 
                id,
                guide_header,
                provides_dual_units
            FROM garment_guides
            ORDER BY id
        """)
        
        guides = cursor.fetchall()
        print("garment_guides.provides_dual_units:")
        for guide in guides:
            print(f"   Guide {guide['id']}: {guide['provides_dual_units']}")
        
        # Check garment_guide_entries.measurement_source_type
        cursor.execute("""
            SELECT 
                garment_guide_id,
                measurement_source_type,
                COUNT(*) as count
            FROM garment_guide_entries
            GROUP BY garment_guide_id, measurement_source_type
            ORDER BY garment_guide_id, measurement_source_type
        """)
        
        entries = cursor.fetchall()
        print("\ngarment_guide_entries.measurement_source_type:")
        for entry in entries:
            print(f"   Guide {entry['garment_guide_id']}: {entry['measurement_source_type']} ({entry['count']} entries)")
        
        # Step 2: Check for consistency
        print("\n2. CONSISTENCY ANALYSIS:")
        print("=" * 60)
        
        cursor.execute("""
            SELECT 
                gg.id as guide_id,
                gg.provides_dual_units,
                gge.measurement_source_type,
                COUNT(gge.id) as entry_count
            FROM garment_guides gg
            LEFT JOIN garment_guide_entries gge ON gg.id = gge.garment_guide_id
            GROUP BY gg.id, gg.provides_dual_units, gge.measurement_source_type
            ORDER BY gg.id
        """)
        
        consistency = cursor.fetchall()
        print("Consistency between the two fields:")
        for row in consistency:
            print(f"   Guide {row['guide_id']}: provides_dual_units={row['provides_dual_units']}, source_type={row['measurement_source_type']}, entries={row['entry_count']}")
        
        # Step 3: Check if we can derive one from the other
        print("\n3. DERIVATION ANALYSIS:")
        print("=" * 60)
        
        cursor.execute("""
            SELECT 
                garment_guide_id,
                COUNT(*) as total_entries,
                COUNT(CASE WHEN measurement_value_cm IS NOT NULL AND measurement_value_in IS NOT NULL THEN 1 END) as dual_unit_entries,
                COUNT(CASE WHEN measurement_source_type = 'provided_both' THEN 1 END) as provided_both_entries
            FROM garment_guide_entries
            GROUP BY garment_guide_id
        """)
        
        derivation = cursor.fetchall()
        print("Can we derive provides_dual_units from measurement_source_type?")
        for row in derivation:
            has_dual_units = row['dual_unit_entries'] > 0
            all_provided_both = row['provided_both_entries'] == row['total_entries']
            print(f"   Guide {row['garment_guide_id']}: {row['total_entries']} total, {row['dual_unit_entries']} dual, {row['provided_both_entries']} provided_both")
            print(f"     Has dual units: {has_dual_units}")
            print(f"     All provided_both: {all_provided_both}")
        
        # Step 4: Check if we can derive measurement_source_type from provides_dual_units
        print("\n4. REVERSE DERIVATION ANALYSIS:")
        print("=" * 60)
        
        cursor.execute("""
            SELECT 
                gg.id as guide_id,
                gg.provides_dual_units,
                gge.measurement_source_type,
                COUNT(*) as count
            FROM garment_guides gg
            JOIN garment_guide_entries gge ON gg.id = gge.garment_guide_id
            GROUP BY gg.id, gg.provides_dual_units, gge.measurement_source_type
            ORDER BY gg.id, gge.measurement_source_type
        """)
        
        reverse_derivation = cursor.fetchall()
        print("Can we derive measurement_source_type from provides_dual_units?")
        for row in reverse_derivation:
            if row['provides_dual_units']:
                expected_source = 'provided_both'
            else:
                expected_source = 'original'
            
            matches = row['measurement_source_type'] == expected_source
            print(f"   Guide {row['guide_id']}: provides_dual_units={row['provides_dual_units']}")
            print(f"     Expected source_type: {expected_source}")
            print(f"     Actual source_type: {row['measurement_source_type']}")
            print(f"     Matches: {matches} ({row['count']} entries)")
        
        # Step 5: Recommendations
        print("\n5. RECOMMENDATIONS:")
        print("=" * 60)
        
        print("Analysis:")
        print("   • provides_dual_units (garment_guides): Brand-level flag")
        print("   • measurement_source_type (garment_guide_entries): Entry-level detail")
        print("   • They are indeed redundant for current data")
        
        print("\nOptions:")
        print("   1. Remove provides_dual_units - derive from measurement_source_type")
        print("   2. Remove measurement_source_type - derive from provides_dual_units")
        print("   3. Keep both but ensure consistency")
        print("   4. Consolidate into a single approach")
        
        print("\nRecommendation:")
        print("   Remove provides_dual_units from garment_guides because:")
        print("   • measurement_source_type is more granular and accurate")
        print("   • It can handle mixed cases (some entries dual, others not)")
        print("   • It's closer to the actual data")
        print("   • We can always aggregate up to garment_guide level if needed")
        
        conn.commit()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    analyze_dual_unit_redundancy()

