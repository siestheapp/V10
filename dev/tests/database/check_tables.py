#!/usr/bin/env python3
"""
Check table structure to understand the user_garments issue
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
    """Get database connection"""
    return psycopg2.connect(**DB_CONFIG)

def check_tables():
    """Check table structure"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    print("🔍 Checking table structure...")
    
    # Check if user_garments table exists and has user_id column
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'user_garments' 
        ORDER BY ordinal_position
    """)
    
    columns = cursor.fetchall()
    print(f"\nuser_garments table columns:")
    for col in columns:
        print(f"  {col['column_name']}: {col['data_type']}")
    
    # Check current users
    cursor.execute("SELECT * FROM users ORDER BY id")
    users = cursor.fetchall()
    
    print(f"\nCurrent users:")
    for user in users:
        print(f"  User {user['id']}: {user['email']}")
    
    # Check user_garments data
    cursor.execute("SELECT user_id, COUNT(*) as count FROM user_garments GROUP BY user_id")
    garment_counts = cursor.fetchall()
    
    print(f"\nUser garments:")
    for gc in garment_counts:
        print(f"  User {gc['user_id']}: {gc['count']} garments")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_tables() 