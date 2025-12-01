#!/usr/bin/env python3
"""
Remove length feedback entries from the database
"""

import psycopg2
from psycopg2.extras import RealDictCursor

# Database configuration
DB_CONFIG = {
    "database": "postgres",
    "user": "fs_core_rw",
    "password": "CHANGE_ME",
    "host": "aws-1-us-east-1.pooler.supabase.com",
    "port": "5432"
}

def get_connection():
    """Get database connection"""
    return psycopg2.connect(**DB_CONFIG)

def remove_length_feedback():
    """Remove all length feedback entries"""
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # First, let's see what we're about to delete
        cursor.execute("""
            SELECT ugf.id, ugf.user_garment_id, ug.product_name, fc.feedback_text, ugf.created_at
            FROM user_garment_feedback ugf
            JOIN user_garments ug ON ugf.user_garment_id = ug.id
            JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
            WHERE ugf.dimension = 'length'
            ORDER BY ugf.created_at
        """)
        
        entries_to_delete = cursor.fetchall()
        
        if not entries_to_delete:
            print("✅ No length feedback entries found to delete.")
            return
        
        print(f"🗑️  Found {len(entries_to_delete)} length feedback entries to delete:")
        print("-" * 80)
        for entry in entries_to_delete:
            print(f"ID: {entry[0]} | Garment: {entry[2]} | Feedback: {entry[3]} | Date: {entry[4]}")
        
        # Confirm deletion
        confirm = input("\n❓ Are you sure you want to delete these entries? (yes/no): ")
        if confirm.lower() != 'yes':
            print("❌ Deletion cancelled.")
            return
        
        # Delete length feedback entries
        cursor.execute("""
            DELETE FROM user_garment_feedback 
            WHERE dimension = 'length'
        """)
        
        deleted_count = cursor.rowcount
        conn.commit()
        
        print(f"✅ Successfully deleted {deleted_count} length feedback entries!")
        
        # Verify deletion
        cursor.execute("""
            SELECT COUNT(*) FROM user_garment_feedback WHERE dimension = 'length'
        """)
        remaining = cursor.fetchone()[0]
        print(f"📊 Remaining length feedback entries: {remaining}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error removing length feedback: {e}")

if __name__ == "__main__":
    remove_length_feedback() 