#!/usr/bin/env python3
"""
Analyze garment tables for redundancies and inefficiencies
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

def analyze_garment_tables():
    """Analyze garment tables for redundancies and inefficiencies"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("🔍 Analyzing garment tables for redundancies and inefficiencies...")
        
        # Step 1: Analyze table structures
        print("\n1. TABLE STRUCTURE ANALYSIS:")
        print("=" * 50)
        
        # garment_guides table
        cursor.execute("""
            SELECT 
                column_name,
                data_type,
                is_nullable,
                column_default,
                character_maximum_length
            FROM information_schema.columns 
            WHERE table_name = 'garment_guides'
            ORDER BY ordinal_position
        """)
        
        garment_guides_cols = cursor.fetchall()
        print("garment_guides table:")
        for col in garment_guides_cols:
            print(f"   {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
        
        # garment_guide_entries table
        cursor.execute("""
            SELECT 
                column_name,
                data_type,
                is_nullable,
                column_default,
                character_maximum_length
            FROM information_schema.columns 
            WHERE table_name = 'garment_guide_entries'
            ORDER BY ordinal_position
        """)
        
        garment_entries_cols = cursor.fetchall()
        print("\ngarment_guide_entries table:")
        for col in garment_entries_cols:
            print(f"   {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
        
        # Step 2: Check for redundant columns
        print("\n2. REDUNDANCY ANALYSIS:")
        print("=" * 50)
        
        # Check if unit column is redundant with measurement_value_in/cm
        cursor.execute("""
            SELECT 
                COUNT(*) as total_rows,
                COUNT(CASE WHEN unit = 'in' THEN 1 END) as inch_rows,
                COUNT(CASE WHEN unit = 'cm' THEN 1 END) as cm_rows,
                COUNT(CASE WHEN unit IS NULL THEN 1 END) as null_unit_rows
            FROM garment_guide_entries
        """)
        
        unit_analysis = cursor.fetchone()
        print(f"Unit column analysis:")
        print(f"   Total rows: {unit_analysis['total_rows']}")
        print(f"   Inch rows: {unit_analysis['inch_rows']}")
        print(f"   CM rows: {unit_analysis['cm_rows']}")
        print(f"   Null unit rows: {unit_analysis['null_unit_rows']}")
        
        # Check for redundant data between unit and measurement columns
        cursor.execute("""
            SELECT 
                COUNT(*) as redundant_unit_rows
            FROM garment_guide_entries
            WHERE unit = 'in' AND measurement_value_in IS NOT NULL
        """)
        
        redundant_units = cursor.fetchone()
        print(f"   Rows where unit='in' AND measurement_value_in exists: {redundant_units['redundant_unit_rows']}")
        
        # Step 3: Check for normalization issues
        print("\n3. NORMALIZATION ANALYSIS:")
        print("=" * 50)
        
        # Check for repeated data in garment_guides
        cursor.execute("""
            SELECT 
                brand_id,
                info_source,
                COUNT(*) as duplicate_count
            FROM garment_guides
            GROUP BY brand_id, info_source
            HAVING COUNT(*) > 1
        """)
        
        duplicate_guides = cursor.fetchall()
        if duplicate_guides:
            print("⚠️  Potential duplicate garment guides:")
            for guide in duplicate_guides:
                print(f"   Brand {guide['brand_id']}, source {guide['info_source']}: {guide['duplicate_count']} entries")
        else:
            print("✅ No duplicate garment guides found")
        
        # Check for measurement_type consistency
        cursor.execute("""
            SELECT 
                measurement_type,
                COUNT(*) as count,
                COUNT(DISTINCT garment_guide_id) as guide_count
            FROM garment_guide_entries
            GROUP BY measurement_type
            ORDER BY count DESC
        """)
        
        measurement_types = cursor.fetchall()
        print("\nMeasurement type distribution:")
        for mt in measurement_types:
            print(f"   {mt['measurement_type']}: {mt['count']} entries across {mt['guide_count']} guides")
        
        # Step 4: Check for inefficiencies
        print("\n4. INEFFICIENCY ANALYSIS:")
        print("=" * 50)
        
        # Check for missing indexes
        cursor.execute("""
            SELECT 
                indexname,
                indexdef
            FROM pg_indexes
            WHERE tablename IN ('garment_guides', 'garment_guide_entries')
            ORDER BY tablename, indexname
        """)
        
        indexes = cursor.fetchall()
        print("Current indexes:")
        for idx in indexes:
            print(f"   {idx['indexname']}: {idx['indexdef']}")
        
        # Check for unused columns
        cursor.execute("""
            SELECT 
                column_name,
                COUNT(*) as null_count,
                COUNT(*) FILTER (WHERE column_value IS NOT NULL) as non_null_count
            FROM (
                SELECT 
                    'measurement_source' as column_name,
                    measurement_source as column_value
                FROM garment_guide_entries
                UNION ALL
                SELECT 
                    'source_term' as column_name,
                    source_term as column_value
                FROM garment_guide_entries
                UNION ALL
                SELECT 
                    'notes' as column_name,
                    notes as column_value
                FROM garment_guide_entries
            ) subq
            GROUP BY column_name
        """)
        
        column_usage = cursor.fetchall()
        print("\nColumn usage analysis:")
        for col in column_usage:
            print(f"   {col['column_name']}: {col['non_null_count']} non-null, {col['null_count']} null")
        
        # Step 5: Check for data consistency issues
        print("\n5. DATA CONSISTENCY ANALYSIS:")
        print("=" * 50)
        
        # Check for orphaned entries
        cursor.execute("""
            SELECT COUNT(*) as orphaned_entries
            FROM garment_guide_entries gge
            LEFT JOIN garment_guides gg ON gge.garment_guide_id = gg.id
            WHERE gg.id IS NULL
        """)
        
        orphaned = cursor.fetchone()
        print(f"Orphaned garment guide entries: {orphaned['orphaned_entries']}")
        
        # Check for measurement value consistency
        cursor.execute("""
            SELECT 
                COUNT(*) as inconsistent_measurements
            FROM garment_guide_entries
            WHERE measurement_value_in IS NOT NULL 
            AND measurement_value_cm IS NOT NULL
            AND ABS(measurement_value_in * 2.54 - measurement_value_cm) > 0.1
        """)
        
        inconsistent = cursor.fetchone()
        print(f"Inconsistent inch/cm conversions: {inconsistent['inconsistent_measurements']}")
        
        # Step 6: Recommendations
        print("\n6. RECOMMENDATIONS:")
        print("=" * 50)
        
        recommendations = []
        
        # Check if unit column is redundant
        if unit_analysis['cm_rows'] == 0:
            recommendations.append("❌ 'unit' column may be redundant since all rows are 'in'")
        
        # Check for missing indexes
        if len(indexes) < 3:
            recommendations.append("⚠️  Consider adding indexes on frequently queried columns")
        
        # Check for unused columns
        for col in column_usage:
            if col['non_null_count'] == 0:
                recommendations.append(f"❌ Column '{col['column_name']}' appears unused (all null)")
        
        if not recommendations:
            print("✅ No major issues found! Your tables are well-structured.")
        else:
            for rec in recommendations:
                print(rec)
        
        # Step 7: Performance analysis
        print("\n7. PERFORMANCE ANALYSIS:")
        print("=" * 50)
        
        cursor.execute("""
            SELECT 
                schemaname,
                tablename,
                attname,
                n_distinct,
                correlation
            FROM pg_stats
            WHERE tablename IN ('garment_guides', 'garment_guide_entries')
            ORDER BY tablename, attname
        """)
        
        stats = cursor.fetchall()
        print("Table statistics:")
        for stat in stats:
            print(f"   {stat['tablename']}.{stat['attname']}: {stat['n_distinct']} distinct values")
        
        conn.commit()
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    analyze_garment_tables()

