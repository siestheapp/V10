#!/usr/bin/env python3
"""
Debug size guides table
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

def debug_size_guides():
    """Debug size guides table"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Check size guide 8 specifically
    cursor.execute("""
        SELECT * FROM size_guides WHERE id = 8
    """)
    
    sg = cursor.fetchone()
    print("=== SIZE GUIDE 8 ===")
    for key, value in sg.items():
        print(f"{key}: {value}")
    print()
    
    # Test the exact query from fix script
    print("=== TESTING EXACT QUERY ===")
    cursor.execute("""
        SELECT id FROM size_guides 
        WHERE brand_id = 5 AND category_id = 1 AND gender = 'Male' 
        AND (fit_type = 'Regular' OR fit_type = 'Unspecified')
        AND subcategory_id IS NULL
        ORDER BY CASE WHEN fit_type = 'Regular' THEN 1 ELSE 2 END
        LIMIT 1
    """)
    
    result = cursor.fetchone()
    print(f"Query result: {result}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    debug_size_guides() 