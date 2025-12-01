#!/usr/bin/env python3
"""
Fix existing garments that don't have size guide links
"""
import psycopg2
from psycopg2.extras import RealDictCursor

# Database configuration - Supabase tailor3
DB_CONFIG = {
    "database": "postgres",
    "user": "fs_core_rw",
    "password": "CHANGE_ME",
    "host": "aws-1-us-east-1.pooler.supabase.com",
    "port": "5432"
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def fix_garment_links():
    """Fix garments that don't have size guide links"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Find garments without size guide links
    cursor.execute("""
        SELECT ug.id, ug.brand_id, ug.category_id, ug.subcategory_id, 
               ug.gender, ug.fit_type, ug.size_label,
               b.name as brand_name, c.name as category_name
        FROM user_garments ug
        JOIN brands b ON ug.brand_id = b.id
        JOIN categories c ON ug.category_id = c.id
        WHERE ug.size_guide_id IS NULL
    """)
    
    garments = cursor.fetchall()
    print(f"Found {len(garments)} garments without size guide links")
    
    for garment in garments:
        print(f"\nFixing garment {garment['id']}: {garment['brand_name']} {garment['category_name']} {garment['size_label']}")
        
        # Use a fresh cursor for the size guide lookup
        size_guide_cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Look up size guide - simplified approach
        if garment['subcategory_id']:
            size_guide_cursor.execute("""
                SELECT id FROM size_guides 
                WHERE brand_id = %s AND category_id = %s AND gender = %s 
                AND (fit_type = %s OR fit_type = 'Unspecified')
                AND subcategory_id = %s
                ORDER BY CASE WHEN fit_type = %s THEN 1 ELSE 2 END
                LIMIT 1
            """, (garment['brand_id'], garment['category_id'], garment['gender'], 
                  garment['fit_type'], garment['subcategory_id'], garment['fit_type']))
        else:
            size_guide_cursor.execute("""
                SELECT id FROM size_guides 
                WHERE brand_id = %s AND category_id = %s AND gender = %s 
                AND (fit_type = %s OR fit_type = 'Unspecified')
                AND subcategory_id IS NULL
                ORDER BY CASE WHEN fit_type = %s THEN 1 ELSE 2 END
                LIMIT 1
            """, (garment['brand_id'], garment['category_id'], garment['gender'], 
                  garment['fit_type'], garment['fit_type']))
        
        size_guide_result = size_guide_cursor.fetchone()
        
        if size_guide_result:
            size_guide_id = size_guide_result['id']
            print(f"  Found size guide: {size_guide_id}")
            
            # Look up specific size entry
            size_guide_cursor.execute("""
                SELECT id FROM size_guide_entries 
                WHERE size_guide_id = %s AND size_label = %s
                LIMIT 1
            """, (size_guide_id, garment['size_label']))
            
            entry_result = size_guide_cursor.fetchone()
            size_guide_entry_id = entry_result['id'] if entry_result else None
            
            if size_guide_entry_id:
                print(f"  Found size entry: {size_guide_entry_id}")
            else:
                print(f"  Size guide found but no entry for size {garment['size_label']}")
            
            # Update the garment using the main cursor
            cursor.execute("""
                UPDATE user_garments 
                SET size_guide_id = %s, size_guide_entry_id = %s
                WHERE id = %s
            """, (size_guide_id, size_guide_entry_id, garment['id']))
            
            print(f"  ✅ Updated garment {garment['id']} (rows affected: {cursor.rowcount})")
        else:
            print(f"  ❌ No size guide found for this combination")
        
        size_guide_cursor.close()
    
    conn.commit()
    cursor.close()
    conn.close()
    print(f"\nFixed {len(garments)} garments")

if __name__ == "__main__":
    fix_garment_links() 