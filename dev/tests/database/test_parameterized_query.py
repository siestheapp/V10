#!/usr/bin/env python3
"""
Test parameterized query issue
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

def test_parameterized_query():
    """Test parameterized query"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Test values
    brand_id = 5
    category_id = 1
    gender = 'Male'
    fit_type = 'Regular'
    
    print(f"Testing with: brand_id={brand_id}, category_id={category_id}, gender={gender}, fit_type={fit_type}")
    
    # Test 1: Hardcoded
    cursor.execute("""
        SELECT id FROM size_guides 
        WHERE brand_id = 5 AND category_id = 1 AND gender = 'Male' 
        AND (fit_type = 'Regular' OR fit_type = 'Unspecified')
        AND subcategory_id IS NULL
        ORDER BY CASE WHEN fit_type = 'Regular' THEN 1 ELSE 2 END
        LIMIT 1
    """)
    result1 = cursor.fetchone()
    print(f"Hardcoded result: {result1}")
    
    # Test 2: Parameterized
    cursor.execute("""
        SELECT id FROM size_guides 
        WHERE brand_id = %s AND category_id = %s AND gender = %s 
        AND (fit_type = %s OR fit_type = 'Unspecified')
        AND subcategory_id IS NULL
        ORDER BY CASE WHEN fit_type = %s THEN 1 ELSE 2 END
        LIMIT 1
    """, (brand_id, category_id, gender, fit_type, fit_type))
    result2 = cursor.fetchone()
    print(f"Parameterized result: {result2}")
    
    # Test 3: Let's see what's actually in the table
    cursor.execute("""
        SELECT id, brand_id, category_id, gender, fit_type, subcategory_id 
        FROM size_guides 
        WHERE brand_id = %s AND category_id = %s
    """, (brand_id, category_id))
    all_results = cursor.fetchall()
    print(f"All matching brand/category records:")
    for row in all_results:
        print(f"  {row}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    test_parameterized_query() 