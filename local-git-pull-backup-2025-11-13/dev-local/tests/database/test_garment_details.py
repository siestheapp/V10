#!/usr/bin/env python3
"""
Test script to debug garment 1 details
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

def test_garment_details():
    """Test garment 1 details"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Get garment 1 details
    cursor.execute("""
        SELECT ug.*, b.name as brand_name, c.name as category_name, 
               sc.name as subcategory_name, u.email as user_email
        FROM user_garments ug
        JOIN brands b ON ug.brand_id = b.id
        JOIN categories c ON ug.category_id = c.id
        LEFT JOIN subcategories sc ON ug.subcategory_id = sc.id
        JOIN users u ON ug.user_id = u.id
        WHERE ug.id = 1
    """)
    garment = cursor.fetchone()
    
    print("=== GARMENT 1 DETAILS ===")
    print(f"Brand: {garment['brand_name']} (ID: {garment['brand_id']})")
    print(f"Category: {garment['category_name']} (ID: {garment['category_id']})")
    print(f"Size: {garment['size_label']}")
    print(f"Gender: {garment['gender']}")
    print(f"Fit Type: {garment['fit_type']}")
    print(f"Size Guide ID: {garment['size_guide_id']}")
    print(f"Size Guide Entry ID: {garment['size_guide_entry_id']}")
    print()
    
    # Check what size guides exist for Banana Republic
    print("=== AVAILABLE SIZE GUIDES FOR BANANA REPUBLIC ===")
    cursor.execute("""
        SELECT sg.id, sg.brand_id, sg.category_id, sg.gender, sg.fit_type,
               b.name as brand_name, c.name as category_name
        FROM size_guides sg
        JOIN brands b ON sg.brand_id = b.id
        JOIN categories c ON sg.category_id = c.id
        WHERE sg.brand_id = %s
    """, (garment['brand_id'],))
    
    size_guides = cursor.fetchall()
    for sg in size_guides:
        print(f"  Size Guide {sg['id']}: {sg['brand_name']} {sg['category_name']} {sg['gender']} {sg['fit_type']}")
    print()
    
    if garment['size_guide_id']:
        print("=== TESTING DIMENSION QUERY ===")
        
        # Test the exact query from the web app
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
        """, (garment['size_guide_id'],))
        
        dimensions_result = cursor.fetchone()
        print(f"Query result: {dimensions_result}")
        
        available_dimensions = []
        if dimensions_result:
            # Add all dimensions that exist for this brand (only non-None values)
            for dim in dimensions_result.values():
                if dim is not None:
                    available_dimensions.append(dim)
        
        print(f"Available dimensions: {available_dimensions}")
        
        # Also check what entries exist for this size guide
        cursor.execute("""
            SELECT size_label, chest_min, chest_max, sleeve_min, sleeve_max, center_back_length
            FROM size_guide_entries 
            WHERE size_guide_id = %s
            ORDER BY size_label
        """, (garment['size_guide_id'],))
        
        entries = cursor.fetchall()
        print(f"\nAll entries for size guide {garment['size_guide_id']}:")
        for entry in entries:
            print(f"  {entry['size_label']}: chest={entry['chest_min']}-{entry['chest_max']}, sleeve={entry['sleeve_min']}-{entry['sleeve_max']}, length={entry['center_back_length']}")
    
    else:
        print("No size guide linked to this garment")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    test_garment_details() 