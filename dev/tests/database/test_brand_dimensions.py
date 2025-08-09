#!/usr/bin/env python3
"""
Test script to check what dimensions exist for each brand
"""
import psycopg2
from psycopg2.extras import RealDictCursor

# Database configuration - Supabase tailor3
DB_CONFIG = {
    "database": "postgres",
    "user": "postgres.lbilxlkchzpducggkrxx",
    "password": "efvTower12",
    "host": "aws-0-us-east-2.pooler.supabase.com",
    "port": "6543"
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def test_brand_dimensions():
    """Test what dimensions exist for each brand"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Get all brands with size guides
    cursor.execute("""
        SELECT DISTINCT b.id, b.name, sg.id as size_guide_id
        FROM brands b
        JOIN size_guides sg ON b.id = sg.brand_id
        ORDER BY b.name
    """)
    brands = cursor.fetchall()
    
    print("=== BRAND DIMENSION ANALYSIS ===\n")
    
    for brand in brands:
        print(f"Brand: {brand['name']} (ID: {brand['id']}, Size Guide ID: {brand['size_guide_id']})")
        
        # Check what dimensions exist for this brand
        cursor.execute("""
            SELECT 
                COUNT(*) as total_entries,
                COUNT(CASE WHEN chest_min IS NOT NULL OR chest_max IS NOT NULL OR chest_range IS NOT NULL THEN 1 END) as chest_count,
                COUNT(CASE WHEN waist_min IS NOT NULL OR waist_max IS NOT NULL OR waist_range IS NOT NULL THEN 1 END) as waist_count,
                COUNT(CASE WHEN sleeve_min IS NOT NULL OR sleeve_max IS NOT NULL OR sleeve_range IS NOT NULL THEN 1 END) as sleeve_count,
                COUNT(CASE WHEN neck_min IS NOT NULL OR neck_max IS NOT NULL OR neck_range IS NOT NULL THEN 1 END) as neck_count,
                COUNT(CASE WHEN hip_min IS NOT NULL OR hip_max IS NOT NULL OR hip_range IS NOT NULL THEN 1 END) as hip_count,
                COUNT(CASE WHEN center_back_length IS NOT NULL THEN 1 END) as length_count
            FROM size_guide_entries 
            WHERE size_guide_id = %s
        """, (brand['size_guide_id'],))
        
        result = cursor.fetchone()
        
        print(f"  Total entries: {result['total_entries']}")
        print(f"  Chest: {result['chest_count']}/{result['total_entries']}")
        print(f"  Waist: {result['waist_count']}/{result['total_entries']}")
        print(f"  Sleeve: {result['sleeve_count']}/{result['total_entries']}")
        print(f"  Neck: {result['neck_count']}/{result['total_entries']}")
        print(f"  Hip: {result['hip_count']}/{result['total_entries']}")
        print(f"  Length: {result['length_count']}/{result['total_entries']}")
        
        # Show sample entries
        cursor.execute("""
            SELECT size_label, chest_min, chest_max, sleeve_min, sleeve_max, center_back_length
            FROM size_guide_entries 
            WHERE size_guide_id = %s
            ORDER BY size_label
            LIMIT 3
        """, (brand['size_guide_id'],))
        
        samples = cursor.fetchall()
        print("  Sample entries:")
        for sample in samples:
            print(f"    {sample['size_label']}: chest={sample['chest_min']}-{sample['chest_max']}, sleeve={sample['sleeve_min']}-{sample['sleeve_max']}, length={sample['center_back_length']}")
        
        print()
    
    # TEST THE EXACT WEB APP QUERY FOR BANANA REPUBLIC
    print("=== TESTING WEB APP QUERY FOR BANANA REPUBLIC ===")
    size_guide_id = 8  # Banana Republic
    
    cursor.execute("""
        SELECT 
            CASE WHEN COUNT(CASE WHEN chest_min IS NOT NULL OR chest_max IS NOT NULL OR chest_range IS NOT NULL THEN 1 END) > 0 THEN 'chest' END as chest,
            CASE WHEN COUNT(CASE WHEN waist_min IS NOT NULL OR waist_max IS NOT NULL OR waist_range IS NOT NULL THEN 1 END) > 0 THEN 'waist' END as waist,
            CASE WHEN COUNT(CASE WHEN sleeve_min IS NOT NULL OR sleeve_max IS NOT NULL OR sleeve_range IS NOT NULL THEN 1 END) > 0 THEN 'sleeve' END as sleeve,
            CASE WHEN COUNT(CASE WHEN neck_min IS NOT NULL OR neck_max IS NOT NULL OR neck_range IS NOT NULL THEN 1 END) > 0 THEN 'neck' END as neck,
            CASE WHEN COUNT(CASE WHEN hip_min IS NOT NULL OR hip_max IS NOT NULL OR hip_range IS NOT NULL THEN 1 END) > 0 THEN 'hip' END as hip,
            CASE WHEN COUNT(CASE WHEN center_back_length IS NOT NULL THEN 1 END) > 0 THEN 'length' END as length
        FROM size_guide_entries 
        WHERE size_guide_id = %s
    """, (size_guide_id,))
    
    dimensions_result = cursor.fetchone()
    print(f"Query result: {dimensions_result}")
    
    available_dimensions = []
    if dimensions_result:
        # Add all dimensions that exist for this brand
        for dim in dimensions_result:
            if dim is not None:
                available_dimensions.append(dim)
    
    print(f"Available dimensions: {available_dimensions}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    test_brand_dimensions() 