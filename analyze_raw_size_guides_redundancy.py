#!/usr/bin/env python3
"""
Analyze redundancy between raw_size_guides and size_guides tables
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

def analyze_raw_size_guides_redundancy():
    """Analyze redundancy between raw_size_guides and size_guides tables"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("🔍 Analyzing redundancy between raw_size_guides and size_guides...")
        
        # Step 1: Check table structures
        print("\n1. TABLE STRUCTURE ANALYSIS:")
        print("=" * 70)
        
        # Check raw_size_guides structure
        cursor.execute("""
            SELECT 
                column_name,
                data_type,
                is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'raw_size_guides'
            ORDER BY ordinal_position
        """)
        
        raw_columns = cursor.fetchall()
        print("raw_size_guides table columns:")
        for col in raw_columns:
            print(f"   {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
        
        # Check size_guides structure
        cursor.execute("""
            SELECT 
                column_name,
                data_type,
                is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'size_guides'
            ORDER BY ordinal_position
        """)
        
        size_columns = cursor.fetchall()
        print("\nsize_guides table columns:")
        for col in size_columns:
            print(f"   {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
        
        # Step 2: Identify overlapping columns
        print("\n2. OVERLAPPING COLUMNS ANALYSIS:")
        print("=" * 70)
        
        raw_column_names = {col['column_name'] for col in raw_columns}
        size_column_names = {col['column_name'] for col in size_columns}
        
        overlapping = raw_column_names & size_column_names
        raw_only = raw_column_names - size_column_names
        size_only = size_column_names - raw_column_names
        
        print("Overlapping columns (potential redundancy):")
        for col in sorted(overlapping):
            print(f"   ✅ {col}")
        
        print("\nraw_size_guides only columns:")
        for col in sorted(raw_only):
            print(f"   📁 {col}")
        
        print("\nsize_guides only columns:")
        for col in sorted(size_only):
            print(f"   📊 {col}")
        
        # Step 3: Analyze data relationships
        print("\n3. DATA RELATIONSHIP ANALYSIS:")
        print("=" * 70)
        
        # Check row counts
        cursor.execute("SELECT COUNT(*) as count FROM raw_size_guides")
        raw_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM size_guides")
        size_count = cursor.fetchone()['count']
        
        print(f"raw_size_guides row count: {raw_count}")
        print(f"size_guides row count: {size_count}")
        
        # Check for matching records
        cursor.execute("""
            SELECT 
                rsg.id as raw_id,
                rsg.brand_id,
                rsg.gender,
                rsg.category_id,
                rsg.subcategory_id,
                rsg.fit_type,
                rsg.source_url,
                sg.id as size_guide_id,
                sg.source_url as sg_source_url
            FROM raw_size_guides rsg
            LEFT JOIN size_guides sg ON (
                rsg.brand_id = sg.brand_id 
                AND rsg.gender = sg.gender 
                AND rsg.category_id = sg.category_id
                AND COALESCE(rsg.subcategory_id, 0) = COALESCE(sg.subcategory_id, 0)
                AND COALESCE(rsg.fit_type, 'Regular') = COALESCE(sg.fit_type, 'Regular')
            )
            ORDER BY rsg.id
        """)
        
        relationships = cursor.fetchall()
        matched = 0
        unmatched = 0
        
        print("\nRecord matching analysis:")
        for row in relationships:
            if row['size_guide_id']:
                matched += 1
                print(f"   ✅ Raw {row['raw_id']} → Size Guide {row['size_guide_id']}")
            else:
                unmatched += 1
                print(f"   ❌ Raw {row['raw_id']} → No matching size guide")
        
        print(f"\nMatched: {matched}, Unmatched: {unmatched}")
        
        # Step 4: Analyze unique value proposition
        print("\n4. UNIQUE VALUE ANALYSIS:")
        print("=" * 70)
        
        # Check what raw_size_guides provides that size_guides doesn't
        cursor.execute("""
            SELECT 
                COUNT(*) as total_records,
                COUNT(screenshot_path) as has_screenshot,
                COUNT(raw_text) as has_raw_text,
                COUNT(raw_table_json) as has_raw_json
            FROM raw_size_guides
        """)
        
        raw_value = cursor.fetchone()
        print("raw_size_guides unique value:")
        print(f"   Total records: {raw_value['total_records']}")
        print(f"   Has screenshot_path: {raw_value['has_screenshot']}")
        print(f"   Has raw_text: {raw_value['has_raw_text']}")
        print(f"   Has raw_table_json: {raw_value['has_raw_json']}")
        
        # Check what size_guides provides that raw_size_guides doesn't
        cursor.execute("""
            SELECT 
                COUNT(*) as total_records,
                COUNT(guide_level) as has_guide_level,
                COUNT(specificity) as has_specificity,
                COUNT(version) as has_version,
                COUNT(size_guide_header) as has_header,
                COUNT(measurements_available) as has_measurements
            FROM size_guides
        """)
        
        size_value = cursor.fetchone()
        print("\nsize_guides unique value:")
        print(f"   Total records: {size_value['total_records']}")
        print(f"   Has guide_level: {size_value['has_guide_level']}")
        print(f"   Has specificity: {size_value['has_specificity']}")
        print(f"   Has version: {size_value['has_version']}")
        print(f"   Has size_guide_header: {size_value['has_header']}")
        print(f"   Has measurements_available: {size_value['has_measurements']}")
        
        # Step 5: Usage analysis
        print("\n5. USAGE ANALYSIS:")
        print("=" * 70)
        
        # Check if raw_size_guides is referenced by other tables
        cursor.execute("""
            SELECT 
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY' 
            AND ccu.table_name = 'raw_size_guides'
        """)
        
        raw_references = cursor.fetchall()
        print("Tables that reference raw_size_guides:")
        if raw_references:
            for ref in raw_references:
                print(f"   {ref['table_name']}.{ref['column_name']} → raw_size_guides.{ref['foreign_column_name']}")
        else:
            print("   None found")
        
        # Check if size_guides is referenced by other tables
        cursor.execute("""
            SELECT 
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY' 
            AND ccu.table_name = 'size_guides'
        """)
        
        size_references = cursor.fetchall()
        print("\nTables that reference size_guides:")
        if size_references:
            for ref in size_references:
                print(f"   {ref['table_name']}.{ref['column_name']} → size_guides.{ref['foreign_column_name']}")
        else:
            print("   None found")
        
        # Step 6: Recommendations
        print("\n6. CONSOLIDATION ANALYSIS:")
        print("=" * 70)
        
        print("Current separation purpose:")
        print("   • raw_size_guides: Source documentation & provenance")
        print("   • size_guides: Processed metadata for application use")
        
        print("\nPros of keeping separate:")
        print("   ✅ Clear separation of concerns")
        print("   ✅ raw_size_guides = audit trail/documentation")
        print("   ✅ size_guides = clean application data")
        print("   ✅ Different update patterns")
        print("   ✅ Raw data preservation")
        
        print("\nPros of consolidating:")
        print("   ✅ Reduced redundancy in overlapping columns")
        print("   ✅ Simpler queries (no joins needed)")
        print("   ✅ Single source of truth")
        print("   ✅ Easier maintenance")
        
        print("\nCons of consolidating:")
        print("   ❌ Mixing raw documentation with processed data")
        print("   ❌ Potential data pollution")
        print("   ❌ Loss of clear separation between source and processed")
        print("   ❌ Harder to maintain data lineage")
        
        # Step 7: Final recommendation
        print("\n7. RECOMMENDATION:")
        print("=" * 70)
        
        if raw_value['has_screenshot'] > 0 or raw_value['has_raw_text'] > 0 or raw_value['has_raw_json'] > 0:
            print("   🎯 KEEP TABLES SEPARATE")
            print("   Reasons:")
            print("   1. raw_size_guides serves as important documentation/audit trail")
            print("   2. Contains unique data (screenshots, raw text, JSON)")
            print("   3. Different purposes: documentation vs application data")
            print("   4. Separation of concerns is valuable for data integrity")
            print("   5. Raw data preservation is important for debugging/updates")
            
            print("\n   Optimization suggestions:")
            print("   • Add foreign key from size_guides to raw_size_guides")
            print("   • Use raw_size_guides.id in size_guides for linkage")
            print("   • Keep overlapping columns but ensure consistency")
            print("   • Consider raw_size_guides as 'source of truth' for metadata")
        else:
            print("   🎯 CONSIDER CONSOLIDATION")
            print("   Reasons:")
            print("   1. No unique documentation data in raw_size_guides")
            print("   2. Significant redundancy in metadata columns")
            print("   3. Simpler data model")
            print("   4. Fewer tables to maintain")
        
        conn.commit()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    analyze_raw_size_guides_redundancy()

