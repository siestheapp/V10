#!/usr/bin/env python3
"""
Simple user cleanup - remove inactive user and renumber active user
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

def simple_cleanup():
    """Simple cleanup approach"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    print("🧹 Simple User Cleanup")
    print("=" * 30)
    
    # Check current state
    cursor.execute("SELECT * FROM users ORDER BY id")
    users = cursor.fetchall()
    
    print(f"Current users:")
    for user in users:
        print(f"  User {user['id']}: {user['email']}")
    
    # Check which user has garments
    cursor.execute("SELECT user_id, COUNT(*) as count FROM user_garments GROUP BY user_id")
    garment_counts = cursor.fetchall()
    
    print(f"\nUser garments:")
    for gc in garment_counts:
        print(f"  User {gc['user_id']}: {gc['count']} garments")
    
    # Find active user (user with garments)
    active_user_id = None
    if garment_counts:
        active_user_id = garment_counts[0]['user_id']
        print(f"\n✅ Active user: User {active_user_id}")
    
    if not active_user_id:
        print("❌ No active user found!")
        return
    
    # Simple approach: Delete inactive user first, then update active user
    cursor.execute("SELECT email FROM users WHERE id = %s", (active_user_id,))
    active_user_email = cursor.fetchone()['email']
    
    print(f"\n🔄 Deleting inactive user 1 first...")
    cursor.execute("DELETE FROM users WHERE id = 1")
    
    print(f"🔄 Updating garments to reference user 1...")
    cursor.execute("UPDATE user_garments SET user_id = 1 WHERE user_id = %s", (active_user_id,))
    
    print(f"🔄 Updating user {active_user_id} to become user_id=1...")
    cursor.execute("UPDATE users SET id = 1 WHERE id = %s", (active_user_id,))
    
    # Update feedback to reference user 1's garments
    cursor.execute("""
        UPDATE user_garment_feedback 
        SET user_garment_id = ug_new.id
        FROM user_garments ug_new, user_garments ug_old
        WHERE ug_new.user_id = 1 
        AND ug_old.user_id = %s
        AND ug_new.brand_id = ug_old.brand_id
        AND ug_new.product_name = ug_old.product_name
        AND ug_new.size_label = ug_old.size_label
        AND user_garment_feedback.user_garment_id = ug_old.id
    """, (active_user_id,))
    
    conn.commit()
    
    print("✅ Cleanup completed!")
    
    # Verify results
    cursor.execute("SELECT * FROM users ORDER BY id")
    final_users = cursor.fetchall()
    
    print(f"\n📊 Final users:")
    for user in final_users:
        print(f"  User {user['id']}: {user['email']}")
    
    cursor.execute("SELECT user_id, COUNT(*) as count FROM user_garments GROUP BY user_id")
    final_garments = cursor.fetchall()
    
    print(f"\n👕 Final garments:")
    for gc in final_garments:
        print(f"  User {gc['user_id']}: {gc['count']} garments")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    simple_cleanup() 