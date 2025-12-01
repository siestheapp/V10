#!/usr/bin/env python3
"""
Manually fix garment 1
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

def manual_fix():
    """Manually fix garment 1"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Update garment 1 with size guide 8
    cursor.execute("""
        UPDATE user_garments 
        SET size_guide_id = 8
        WHERE id = 1
    """)
    
    print(f"Updated garment 1 with size guide 8 (rows affected: {cursor.rowcount})")
    
    # Now look up the size entry for L
    cursor.execute("""
        SELECT id FROM size_guide_entries 
        WHERE size_guide_id = 8 AND size_label = 'L'
        LIMIT 1
    """)
    
    entry_result = cursor.fetchone()
    if entry_result:
        size_guide_entry_id = entry_result['id']
        print(f"Found size entry for L: {size_guide_entry_id}")
        
        # Update with size entry
        cursor.execute("""
            UPDATE user_garments 
            SET size_guide_entry_id = %s
            WHERE id = 1
        """, (size_guide_entry_id,))
        
        print(f"Updated garment 1 with size entry {size_guide_entry_id} (rows affected: {cursor.rowcount})")
    else:
        print("No size entry found for L")
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Manual fix completed")

if __name__ == "__main__":
    manual_fix() 