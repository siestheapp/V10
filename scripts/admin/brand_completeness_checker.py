#!/usr/bin/env python3
"""
Brand Completeness Checker
Helps track which brands are missing data in size guide related tables
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import sys
import os

# Database connection parameters
DB_CONFIG = {
    'host': 'aws-0-us-east-2.pooler.supabase.com',
    'port': 6543,
    'user': 'postgres.lbilxlkchzpducggkrxx',
    'password': 'efvTower12',
    'database': 'postgres'
}

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(**DB_CONFIG)

def check_brand_completeness():
    """Check completeness of all brands"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    print("🔍 BRAND DATA COMPLETENESS REPORT")
    print("=" * 60)
    
    # Get overall summary
    cursor.execute("""
        SELECT 
            COUNT(*) as total_brands,
            COUNT(*) FILTER (WHERE completeness_percentage = 100) as complete_brands,
            COUNT(*) FILTER (WHERE completeness_percentage < 100) as incomplete_brands,
            ROUND(AVG(completeness_percentage), 1) as avg_completeness
        FROM brand_data_completeness
    """)
    summary = cursor.fetchone()
    
    print(f"📊 SUMMARY:")
    print(f"   Total Brands: {summary['total_brands']}")
    print(f"   Complete: {summary['complete_brands']} ✅")
    print(f"   Incomplete: {summary['incomplete_brands']} ⚠️")
    print(f"   Average Completeness: {summary['avg_completeness']}%")
    print()
    
    # Get complete brands
    cursor.execute("""
        SELECT brand_name, completeness_percentage 
        FROM brand_data_completeness 
        WHERE completeness_percentage = 100
        ORDER BY brand_name
    """)
    complete_brands = cursor.fetchall()
    
    if complete_brands:
        print("✅ COMPLETE BRANDS:")
        for brand in complete_brands:
            print(f"   • {brand['brand_name']} (100%)")
        print()
    
    # Get incomplete brands with details
    cursor.execute("SELECT * FROM brand_missing_data ORDER BY completeness_percentage ASC")
    incomplete_brands = cursor.fetchall()
    
    if incomplete_brands:
        print("⚠️  INCOMPLETE BRANDS:")
        for brand in incomplete_brands:
            print(f"   • {brand['brand_name']} ({brand['completeness_percentage']}%)")
            print(f"     Missing: {brand['all_missing_tables']}")
            print(f"     Counts: SG={brand['size_guides_count']}, SGE={brand['size_entries_count']}, "
                  f"RSG={brand['raw_guides_count']}, SL={brand['standardization_entries']}, "
                  f"MI={brand['instruction_count']}, MM={brand['methodology_count']}")
            print()
    
    cursor.close()
    conn.close()

def check_specific_brand(brand_name):
    """Check completeness of a specific brand"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("""
        SELECT * FROM brand_data_completeness 
        WHERE LOWER(brand_name) = LOWER(%s)
    """, (brand_name,))
    
    brand = cursor.fetchone()
    if not brand:
        print(f"❌ Brand '{brand_name}' not found!")
        return
    
    print(f"🔍 DETAILED REPORT: {brand['brand_name']}")
    print("=" * 50)
    print(f"Completeness: {brand['completeness_percentage']}% ({brand['completeness_score']}/7)")
    print()
    
    # Show status for each table
    tables = [
        ('Size Guides', brand['has_size_guides'], brand['size_guides_count']),
        ('Size Guide Entries', brand['has_size_entries'], brand['size_entries_count']),
        ('Raw Size Guides', brand['has_raw_data'], brand['raw_guides_count']),
        ('Screenshots', brand['has_screenshots'], 'Yes' if brand['has_screenshots'] == '✅' else 'No'),
        ('Standardization Log', brand['has_standardization'], brand['standardization_entries']),
        ('Measurement Instructions', brand['has_instructions'], brand['instruction_count']),
        ('Measurement Methodology', brand['has_methodology'], brand['methodology_count'])
    ]
    
    for table_name, status, count in tables:
        print(f"{status} {table_name}: {count}")
    
    print()
    
    # Show details if available
    if brand['size_guide_categories']:
        print(f"📋 Categories: {', '.join(brand['size_guide_categories'])}")
    
    if brand['term_mappings']:
        print(f"🔄 Term Mappings: {', '.join(brand['term_mappings'])}")
    
    if brand['instruction_dimensions']:
        print(f"📏 Instructions for: {', '.join(brand['instruction_dimensions'])}")
    
    if brand['methodology_dimensions']:
        print(f"🔬 Methodology for: {', '.join(brand['methodology_dimensions'])}")
    
    if brand['avg_confidence']:
        print(f"📊 Quality: Confidence={brand['avg_confidence']}, Reliability={brand['avg_reliability']}")
    
    cursor.close()
    conn.close()

def generate_fix_commands(brand_name):
    """Generate SQL commands to fix missing data for a brand"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Get brand details
    cursor.execute("SELECT * FROM brand_missing_data WHERE LOWER(brand_name) = LOWER(%s)", (brand_name,))
    brand = cursor.fetchone()
    
    if not brand:
        print(f"❌ Brand '{brand_name}' not found or is already complete!")
        return
    
    print(f"🔧 FIX COMMANDS FOR: {brand['brand_name']}")
    print("=" * 50)
    
    missing_tables = brand['all_missing_tables'].split(', ')
    
    # Get brand ID
    cursor.execute("SELECT id FROM brands WHERE LOWER(name) = LOWER(%s)", (brand_name,))
    brand_id = cursor.fetchone()['id']
    
    for table in missing_tables:
        print(f"\n📝 Missing: {table}")
        
        if table == 'standardization_log':
            print("   # Add term mappings (example):")
            print(f"   INSERT INTO standardization_log (brand_id, original_term, standardized_term, source_table, notes, created_by)")
            print(f"   VALUES ({brand_id}, 'original_term', 'standardized_term', 'size_guide_entries', 'Notes about mapping', 1);")
        
        elif table == 'measurement_instructions':
            print("   # Add measurement instructions:")
            print(f"   INSERT INTO measurement_instructions (brand_id, original_term, standardized_term, instruction, source_url, created_by)")
            print(f"   VALUES ({brand_id}, 'Chest', 'chest', 'How to measure chest...', 'source_url', 1);")
        
        elif table == 'screenshots':
            print("   # Update size_guides with screenshot path:")
            print(f"   UPDATE size_guides SET screenshot_path = 'screenshot_url' WHERE brand_id = {brand_id};")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments - show all brands
        check_brand_completeness()
    elif len(sys.argv) == 2:
        # One argument - show specific brand
        check_specific_brand(sys.argv[1])
    elif len(sys.argv) == 3 and sys.argv[1] == "fix":
        # Two arguments with "fix" - generate fix commands
        generate_fix_commands(sys.argv[2])
    else:
        print("Usage:")
        print("  python brand_completeness_checker.py                    # Check all brands")
        print("  python brand_completeness_checker.py <brand_name>       # Check specific brand")
        print("  python brand_completeness_checker.py fix <brand_name>   # Generate fix commands") 