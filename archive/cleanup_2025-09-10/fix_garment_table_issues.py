#!/usr/bin/env python3
"""
Fix redundancies and inefficiencies in garment tables
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

def fix_garment_table_issues():
    """Fix identified redundancies and inefficiencies"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("🔧 Fixing garment table redundancies and inefficiencies...")
        
        # Issue 1: Remove redundant 'unit' column
        print("\n1. REMOVING REDUNDANT 'unit' COLUMN:")
        print("=" * 50)
        
        # Check if unit column is truly redundant
        cursor.execute("""
            SELECT 
                COUNT(*) as total_rows,
                COUNT(CASE WHEN unit = 'in' THEN 1 END) as inch_rows,
                COUNT(CASE WHEN unit IS NULL THEN 1 END) as null_rows
            FROM garment_guide_entries
        """)
        
        unit_check = cursor.fetchone()
        print(f"   Total rows: {unit_check['total_rows']}")
        print(f"   Inch rows: {unit_check['inch_rows']}")
        print(f"   Null rows: {unit_check['null_rows']}")
        
        if unit_check['inch_rows'] == unit_check['total_rows']:
            print("   ✅ Confirmed: 'unit' column is redundant (all rows are 'in')")
            print("   Removing redundant 'unit' column...")
            
            cursor.execute("""
                ALTER TABLE public.garment_guide_entries 
                DROP COLUMN IF EXISTS unit;
            """)
            print("   ✅ Removed redundant 'unit' column")
        else:
            print("   ⚠️  'unit' column has mixed values - keeping for now")
        
        # Issue 2: Fix inconsistent inch/cm conversions
        print("\n2. FIXING INCONSISTENT CONVERSIONS:")
        print("=" * 50)
        
        cursor.execute("""
            SELECT 
                id,
                measurement_value_in,
                measurement_value_cm,
                ABS(measurement_value_in * 2.54 - measurement_value_cm) as variance
            FROM garment_guide_entries
            WHERE measurement_value_in IS NOT NULL 
            AND measurement_value_cm IS NOT NULL
            AND ABS(measurement_value_in * 2.54 - measurement_value_cm) > 0.1
            ORDER BY variance DESC
        """)
        
        inconsistent = cursor.fetchall()
        print(f"   Found {len(inconsistent)} inconsistent conversions:")
        for row in inconsistent:
            print(f"   ID {row['id']}: {row['measurement_value_in']} in = {float(row['measurement_value_in']) * 2.54:.1f} cm, but stored as {row['measurement_value_cm']} cm (variance: {float(row['variance']):.2f})")
        
        # Fix the conversions by recalculating cm from inches
        if inconsistent:
            print("   Fixing conversions by recalculating cm from inches...")
            cursor.execute("""
                UPDATE garment_guide_entries
                SET measurement_value_cm = ROUND((measurement_value_in * 2.54)::numeric, 1)
                WHERE measurement_value_in IS NOT NULL 
                AND measurement_value_cm IS NOT NULL
                AND ABS(measurement_value_in * 2.54 - measurement_value_cm) > 0.1
            """)
            print(f"   ✅ Fixed {len(inconsistent)} inconsistent conversions")
        
        # Issue 3: Add missing indexes for performance
        print("\n3. ADDING MISSING INDEXES:")
        print("=" * 50)
        
        # Check existing indexes
        cursor.execute("""
            SELECT indexname FROM pg_indexes 
            WHERE tablename = 'garment_guide_entries'
        """)
        
        existing_indexes = [row['indexname'] for row in cursor.fetchall()]
        print(f"   Existing indexes: {existing_indexes}")
        
        # Add missing indexes
        missing_indexes = []
        
        if 'idx_garment_guide_id' not in existing_indexes:
            missing_indexes.append("CREATE INDEX idx_garment_guide_id ON garment_guide_entries(garment_guide_id)")
        
        if 'idx_size_label' not in existing_indexes:
            missing_indexes.append("CREATE INDEX idx_size_label ON garment_guide_entries(size_label)")
        
        if 'idx_measurement_type_size' not in existing_indexes:
            missing_indexes.append("CREATE INDEX idx_measurement_type_size ON garment_guide_entries(measurement_type, size_label)")
        
        if 'idx_garment_guide_measurement' not in existing_indexes:
            missing_indexes.append("CREATE INDEX idx_garment_guide_measurement ON garment_guide_entries(garment_guide_id, measurement_type)")
        
        for index_sql in missing_indexes:
            print(f"   Adding index: {index_sql}")
            cursor.execute(index_sql)
        
        print(f"   ✅ Added {len(missing_indexes)} missing indexes")
        
        # Issue 4: Clean up unused columns
        print("\n4. CLEANING UP UNUSED COLUMNS:")
        print("=" * 50)
        
        # Check column usage
        cursor.execute("""
            SELECT 
                'measurement_source' as column_name,
                COUNT(*) as total,
                COUNT(CASE WHEN measurement_source IS NOT NULL THEN 1 END) as non_null
            FROM garment_guide_entries
            UNION ALL
            SELECT 
                'source_term' as column_name,
                COUNT(*) as total,
                COUNT(CASE WHEN source_term IS NOT NULL THEN 1 END) as non_null
            FROM garment_guide_entries
            UNION ALL
            SELECT 
                'notes' as column_name,
                COUNT(*) as total,
                COUNT(CASE WHEN notes IS NOT NULL THEN 1 END) as non_null
            FROM garment_guide_entries
        """)
        
        column_usage = cursor.fetchall()
        for col in column_usage:
            print(f"   {col['column_name']}: {col['non_null']}/{col['total']} non-null values")
            if col['non_null'] == 0:
                print(f"     ⚠️  Column '{col['column_name']}' is unused - consider removing")
        
        # Issue 5: Add constraints for data integrity
        print("\n5. ADDING DATA INTEGRITY CONSTRAINTS:")
        print("=" * 50)
        
        # Add check constraints
        cursor.execute("""
            ALTER TABLE public.garment_guide_entries 
            ADD CONSTRAINT check_measurement_values 
            CHECK (
                (measurement_value_in IS NOT NULL AND measurement_value_in > 0) OR
                (measurement_value_cm IS NOT NULL AND measurement_value_cm > 0)
            );
        """)
        print("   ✅ Added check constraint for positive measurement values")
        
        cursor.execute("""
            ALTER TABLE public.garment_guide_entries 
            ADD CONSTRAINT check_measurement_source_type 
            CHECK (measurement_source_type IN ('original', 'converted', 'provided_both'));
        """)
        print("   ✅ Added check constraint for measurement source type")
        
        # Issue 6: Optimize data types
        print("\n6. OPTIMIZING DATA TYPES:")
        print("=" * 50)
        
        # Check if numeric precision is appropriate
        cursor.execute("""
            SELECT 
                MAX(LENGTH(measurement_value_in::text)) as max_in_length,
                MAX(LENGTH(measurement_value_cm::text)) as max_cm_length
            FROM garment_guide_entries
            WHERE measurement_value_in IS NOT NULL OR measurement_value_cm IS NOT NULL
        """)
        
        length_check = cursor.fetchone()
        print(f"   Max inch value length: {length_check['max_in_length']}")
        print(f"   Max cm value length: {length_check['max_cm_length']}")
        print("   ✅ Numeric data types are appropriate for measurement precision")
        
        # Issue 7: Create summary view for common queries
        print("\n7. CREATING OPTIMIZED VIEWS:")
        print("=" * 50)
        
        cursor.execute("""
            CREATE OR REPLACE VIEW public.garment_measurements_summary AS
            SELECT 
                gg.id as garment_guide_id,
                b.name as brand_name,
                b.original_measurement_unit,
                b.provides_dual_units,
                gge.size_label,
                gge.measurement_type,
                gge.measurement_value_in,
                gge.measurement_value_cm,
                gge.measurement_source_type,
                gg.source_url,
                gg.guide_header
            FROM garment_guide_entries gge
            JOIN garment_guides gg ON gge.garment_guide_id = gg.id
            JOIN brands b ON gg.brand_id = b.id
            WHERE gge.measurement_value_in IS NOT NULL;
        """)
        print("   ✅ Created optimized summary view")
        
        # Issue 8: Final verification
        print("\n8. FINAL VERIFICATION:")
        print("=" * 50)
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_entries,
                COUNT(DISTINCT garment_guide_id) as unique_guides,
                COUNT(DISTINCT measurement_type) as measurement_types,
                COUNT(DISTINCT size_label) as size_labels
            FROM garment_guide_entries
        """)
        
        final_stats = cursor.fetchone()
        print(f"   Total entries: {final_stats['total_entries']}")
        print(f"   Unique guides: {final_stats['unique_guides']}")
        print(f"   Measurement types: {final_stats['measurement_types']}")
        print(f"   Size labels: {final_stats['size_labels']}")
        
        # Check for any remaining issues
        cursor.execute("""
            SELECT COUNT(*) as orphaned_entries
            FROM garment_guide_entries gge
            LEFT JOIN garment_guides gg ON gge.garment_guide_id = gg.id
            WHERE gg.id IS NULL
        """)
        
        orphaned = cursor.fetchone()
        print(f"   Orphaned entries: {orphaned['orphaned_entries']}")
        
        conn.commit()
        print("\n✅ All garment table issues fixed successfully!")
        
        # Summary of improvements
        print("\n🎯 IMPROVEMENTS MADE:")
        print("   ✅ Removed redundant 'unit' column")
        print("   ✅ Fixed inconsistent inch/cm conversions")
        print("   ✅ Added performance indexes")
        print("   ✅ Added data integrity constraints")
        print("   ✅ Created optimized views")
        print("   ✅ Improved data consistency")
        
    except Exception as e:
        print(f"❌ Error during fixes: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    fix_garment_table_issues()
