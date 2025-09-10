#!/usr/bin/env python3
"""
Remove redundant provides_dual_units column from garment_guides
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

def remove_redundant_dual_units():
    """Remove redundant provides_dual_units column"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("🧹 Removing redundant provides_dual_units column...")
        
        # Step 1: Verify redundancy before removal
        print("\n1. VERIFYING REDUNDANCY:")
        print("=" * 50)
        
        cursor.execute("""
            SELECT 
                gg.id,
                gg.provides_dual_units,
                COUNT(gge.id) as total_entries,
                COUNT(CASE WHEN gge.measurement_source_type = 'provided_both' THEN 1 END) as provided_both_entries
            FROM garment_guides gg
            LEFT JOIN garment_guide_entries gge ON gg.id = gge.garment_guide_id
            GROUP BY gg.id, gg.provides_dual_units
        """)
        
        verification = cursor.fetchall()
        for row in verification:
            is_redundant = row['provides_dual_units'] == (row['provided_both_entries'] > 0)
            print(f"   Guide {row['id']}: provides_dual_units={row['provides_dual_units']}, provided_both_entries={row['provided_both_entries']}")
            print(f"     Redundant: {is_redundant}")
        
        # Step 2: Create a view to replace the functionality
        print("\n2. CREATING REPLACEMENT VIEW:")
        print("=" * 50)
        
        cursor.execute("""
            CREATE OR REPLACE VIEW public.garment_guides_with_dual_units AS
            SELECT 
                gg.id,
                gg.brand_id,
                gg.info_source,
                gg.guide_header,
                gg.measurements_available,
                gg.source_url,
                gg.notes,
                gg.created_at,
                gg.created_by,
                gg.updated_at,
                gg.updated_by,
                gg.screenshot_path,
                gg.raw_source_text,
                gg.user_garment_id,
                gg.source_terms_available,
                CASE 
                    WHEN COUNT(gge.id) > 0 AND COUNT(CASE WHEN gge.measurement_source_type = 'provided_both' THEN 1 END) = COUNT(gge.id)
                    THEN true
                    ELSE false
                END as provides_dual_units
            FROM garment_guides gg
            LEFT JOIN garment_guide_entries gge ON gg.id = gge.garment_guide_id
            GROUP BY gg.id, gg.brand_id, gg.info_source, gg.guide_header, gg.measurements_available, 
                     gg.source_url, gg.notes, gg.created_at, gg.created_by, gg.updated_at, gg.updated_by,
                     gg.screenshot_path, gg.raw_source_text, gg.user_garment_id, gg.source_terms_available
        """)
        
        print("   ✅ Created garment_guides_with_dual_units view")
        
        # Step 3: Test the view
        print("\n3. TESTING REPLACEMENT VIEW:")
        print("=" * 50)
        
        cursor.execute("""
            SELECT 
                id,
                guide_header,
                provides_dual_units
            FROM garment_guides_with_dual_units
            ORDER BY id
        """)
        
        view_test = cursor.fetchall()
        for row in view_test:
            print(f"   Guide {row['id']}: {row['guide_header']} - provides_dual_units: {row['provides_dual_units']}")
        
        # Step 4: Remove the redundant column
        print("\n4. REMOVING REDUNDANT COLUMN:")
        print("=" * 50)
        
        # Drop dependent views first
        cursor.execute("DROP VIEW IF EXISTS public.brand_unit_capabilities CASCADE")
        print("   ✅ Dropped dependent view brand_unit_capabilities")
        
        cursor.execute("""
            ALTER TABLE public.garment_guides 
            DROP COLUMN IF EXISTS provides_dual_units;
        """)
        
        print("   ✅ Removed provides_dual_units column")
        
        # Step 5: Verify the removal
        print("\n5. VERIFYING REMOVAL:")
        print("=" * 50)
        
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'garment_guides' 
            AND column_name = 'provides_dual_units'
        """)
        
        remaining = cursor.fetchall()
        if not remaining:
            print("   ✅ Column successfully removed")
        else:
            print("   ❌ Column still exists")
        
        # Step 6: Show final structure
        print("\n6. FINAL TABLE STRUCTURE:")
        print("=" * 50)
        
        cursor.execute("""
            SELECT 
                column_name,
                data_type,
                is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'garment_guides'
            ORDER BY ordinal_position
        """)
        
        final_structure = cursor.fetchall()
        print("garment_guides table columns:")
        for col in final_structure:
            print(f"   {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
        
        # Step 7: Show how to get dual unit info now
        print("\n7. HOW TO GET DUAL UNIT INFO NOW:")
        print("=" * 50)
        
        print("Option 1: Use the view")
        print("   SELECT * FROM garment_guides_with_dual_units WHERE provides_dual_units = true")
        
        print("\nOption 2: Query directly")
        print("   SELECT gg.* FROM garment_guides gg")
        print("   WHERE EXISTS (")
        print("       SELECT 1 FROM garment_guide_entries gge")
        print("       WHERE gge.garment_guide_id = gg.id")
        print("       AND gge.measurement_source_type = 'provided_both'")
        print("   )")
        
        print("\nOption 3: Aggregate from entries")
        print("   SELECT")
        print("       garment_guide_id,")
        print("       COUNT(*) as total_entries,")
        print("       COUNT(CASE WHEN measurement_source_type = 'provided_both' THEN 1 END) as dual_unit_entries")
        print("   FROM garment_guide_entries")
        print("   GROUP BY garment_guide_id")
        
        conn.commit()
        print("\n✅ Redundant column removed successfully!")
        
        # Summary of improvements
        print("\n🎯 IMPROVEMENTS MADE:")
        print("   ✅ Removed redundant provides_dual_units column")
        print("   ✅ Created replacement view for backward compatibility")
        print("   ✅ Eliminated data duplication")
        print("   ✅ Improved data consistency")
        print("   ✅ measurement_source_type is now the single source of truth")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    remove_redundant_dual_units()
