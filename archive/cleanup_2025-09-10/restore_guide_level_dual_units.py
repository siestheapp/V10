#!/usr/bin/env python3
"""
Restore guide-level provides_dual_units approach and remove redundant measurement_source_type
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

def restore_guide_level_dual_units():
    """Restore guide-level provides_dual_units and remove measurement_source_type"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("🔄 Restoring guide-level provides_dual_units approach...")
        
        # Step 1: Add provides_dual_units back to garment_guides
        print("\n1. ADDING provides_dual_units TO garment_guides:")
        print("=" * 50)
        
        cursor.execute("""
            ALTER TABLE public.garment_guides 
            ADD COLUMN IF NOT EXISTS provides_dual_units boolean DEFAULT false;
        """)
        
        print("   ✅ Added provides_dual_units column")
        
        # Step 2: Set provides_dual_units based on current data
        print("\n2. SETTING provides_dual_units VALUES:")
        print("=" * 50)
        
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
        
        print("   ✅ Updated provides_dual_units based on dual unit availability")
        
        # Step 3: Verify the update
        print("\n3. VERIFYING provides_dual_units:")
        print("=" * 50)
        
        cursor.execute("""
            SELECT 
                id,
                guide_header,
                provides_dual_units
            FROM garment_guides
            ORDER BY id
        """)
        
        guides = cursor.fetchall()
        for guide in guides:
            print(f"   Guide {guide['id']}: {guide['guide_header']} - provides_dual_units: {guide['provides_dual_units']}")
        
        # Step 4: Remove measurement_source_type from garment_guide_entries
        print("\n4. REMOVING measurement_source_type FROM garment_guide_entries:")
        print("=" * 50)
        
        # Drop dependent views first
        cursor.execute("DROP VIEW IF EXISTS public.smart_measurements CASCADE")
        cursor.execute("DROP VIEW IF EXISTS public.garment_measurements_summary CASCADE")
        cursor.execute("DROP VIEW IF EXISTS public.garment_guides_with_dual_units CASCADE")
        print("   ✅ Dropped dependent views")
        
        cursor.execute("""
            ALTER TABLE public.garment_guide_entries 
            DROP COLUMN IF EXISTS measurement_source_type;
        """)
        
        print("   ✅ Removed measurement_source_type column")
        
        # Step 5: Verify the removal
        print("\n5. VERIFYING measurement_source_type REMOVAL:")
        print("=" * 50)
        
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'garment_guide_entries' 
            AND column_name = 'measurement_source_type'
        """)
        
        remaining = cursor.fetchall()
        if not remaining:
            print("   ✅ Column successfully removed")
        else:
            print("   ❌ Column still exists")
        
        # Step 6: Show final structure
        print("\n6. FINAL TABLE STRUCTURES:")
        print("=" * 50)
        
        # garment_guides structure
        cursor.execute("""
            SELECT 
                column_name,
                data_type,
                is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'garment_guides'
            ORDER BY ordinal_position
        """)
        
        guides_structure = cursor.fetchall()
        print("garment_guides table columns:")
        for col in guides_structure:
            print(f"   {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
        
        # garment_guide_entries structure
        cursor.execute("""
            SELECT 
                column_name,
                data_type,
                is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'garment_guide_entries'
            ORDER BY ordinal_position
        """)
        
        entries_structure = cursor.fetchall()
        print("\ngarment_guide_entries table columns:")
        for col in entries_structure:
            print(f"   {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
        
        # Step 7: Test querying efficiency
        print("\n7. TESTING QUERYING EFFICIENCY:")
        print("=" * 50)
        
        # Test guide-level query
        cursor.execute("""
            SELECT 
                gg.id,
                gg.guide_header,
                gg.provides_dual_units
            FROM garment_guides gg
            WHERE gg.provides_dual_units = true
        """)
        
        dual_unit_guides = cursor.fetchall()
        print("Guides with dual units (simple query):")
        for guide in dual_unit_guides:
            print(f"   Guide {guide['id']}: {guide['guide_header']}")
        
        # Test measurement query for inch-preferring user
        cursor.execute("""
            SELECT 
                gge.size_label,
                gge.measurement_type,
                gge.measurement_value_in,
                gge.measurement_value_cm
            FROM garment_guide_entries gge
            JOIN garment_guides gg ON gge.garment_guide_id = gg.id
            WHERE gg.id = 1
            ORDER BY gge.size_label, gge.measurement_type
        """)
        
        measurements = cursor.fetchall()
        print("\nMeasurements for guide 1 (clean query, no redundant data):")
        for row in measurements:
            print(f"   {row['size_label']} {row['measurement_type']}: {row['measurement_value_in']}in / {row['measurement_value_cm']}cm")
        
        # Step 8: Show benefits
        print("\n8. BENEFITS OF GUIDE-LEVEL APPROACH:")
        print("=" * 50)
        
        print("✅ For user preference = inches:")
        print("   • Simple: SELECT * FROM garment_guides WHERE provides_dual_units = true")
        print("   • Efficient: No redundant data in every measurement row")
        print("   • Clean: measurement_value_in always available when needed")
        print("   • Fast: Single boolean flag per guide")
        
        print("\n✅ For app queries:")
        print("   • Guide filtering: WHERE provides_dual_units = true")
        print("   • Measurement retrieval: SELECT measurement_value_in")
        print("   • No complex aggregations needed")
        print("   • Smaller result sets")
        
        print("\n✅ For data consistency:")
        print("   • Single source of truth at guide level")
        print("   • Easier to maintain")
        print("   • Less storage space")
        print("   • Better performance")
        
        conn.commit()
        print("\n✅ Guide-level approach restored successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    restore_guide_level_dual_units()
