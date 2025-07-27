#!/usr/bin/env python3
"""
Clean up users table - remove inactive user and renumber active user to user_id=1
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
    """Get database connection"""
    return psycopg2.connect(**DB_CONFIG)

def cleanup_users():
    """Clean up users table - remove inactive user and renumber active user"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    print("🔍 Analyzing current users...")
    
    # Check current users
    cursor.execute("SELECT * FROM users ORDER BY id")
    users = cursor.fetchall()
    
    print(f"Current users:")
    for user in users:
        print(f"  User {user['id']}: {user['email']} (created: {user['created_at']})")
    
    # Check which user has activity
    cursor.execute("""
        SELECT u.id, u.email, 
               COUNT(ug.id) as garment_count,
               COUNT(ugf.id) as feedback_count
        FROM users u
        LEFT JOIN user_garments ug ON u.id = ug.user_id
        LEFT JOIN user_garment_feedback ugf ON ug.id = ugf.user_garment_id
        GROUP BY u.id, u.email
        ORDER BY u.id
    """)
    
    user_activity = cursor.fetchall()
    
    print(f"\nUser activity:")
    for user in user_activity:
        print(f"  User {user['id']}: {user['email']} - {user['garment_count']} garments, {user['feedback_count']} feedback entries")
    
    # Find the active user (user with garments/feedback)
    active_user = None
    inactive_user = None
    
    for user in user_activity:
        if user['garment_count'] > 0 or user['feedback_count'] > 0:
            active_user = user
        else:
            inactive_user = user
    
    if not active_user:
        print("❌ No active user found!")
        return
    
    print(f"\n✅ Active user: User {active_user['id']} ({active_user['email']})")
    print(f"❌ Inactive user: User {inactive_user['id']} ({inactive_user['email']})")
    
    # Confirm the cleanup
    print(f"\n🔄 Will perform the following changes:")
    print(f"  1. Delete user {inactive_user['id']} ({inactive_user['email']})")
    print(f"  2. Update user {active_user['id']} to become user_id=1")
    print(f"  3. Update all related records to reference the new user_id")
    
    # Perform the cleanup
    try:
        # Start transaction
        cursor.execute("BEGIN")
        
        # Step 1: Delete the inactive user
        print(f"\n🗑️  Deleting user {inactive_user['id']}...")
        cursor.execute("DELETE FROM users WHERE id = %s", (inactive_user['id'],))
        print(f"✅ Deleted user {inactive_user['id']}")
        
        # Step 2: Update the active user to have id=1
        print(f"🔄 Updating user {active_user['id']} to become user_id=1...")
        
        # First, update all related records to use a temporary user_id
        temp_id = 999999
        tables_to_update = [
            'user_garments',
            'user_garment_feedback', 
            'body_measurements',
            'fit_zones'
        ]
        
        print(f"  Updating related records to temporary user_id {temp_id}...")
        for table in tables_to_update:
            try:
                cursor.execute(f"UPDATE {table} SET user_id = %s WHERE user_id = %s", (temp_id, active_user['id']))
                affected = cursor.rowcount
                if affected > 0:
                    print(f"    Updated {affected} records in {table}")
            except Exception as e:
                print(f"    No user_id column in {table} or no records to update")
        
        # Now change the user to id=1
        cursor.execute("UPDATE users SET id = 1 WHERE id = %s", (active_user['id'],))
        print(f"✅ User now has id=1")
        
        # Update all related records to use user_id=1
        print(f"  Updating related records to user_id=1...")
        for table in tables_to_update:
            try:
                cursor.execute(f"UPDATE {table} SET user_id = 1 WHERE user_id = %s", (temp_id,))
                affected = cursor.rowcount
                if affected > 0:
                    print(f"    Updated {affected} records in {table} to user_id=1")
            except Exception as e:
                print(f"    No user_id column in {table} or no records to update")
        
        # Commit the transaction
        cursor.execute("COMMIT")
        
        print(f"\n✅ Cleanup completed successfully!")
        
        # Verify the results
        cursor.execute("SELECT * FROM users ORDER BY id")
        final_users = cursor.fetchall()
        
        print(f"\n📊 Final user state:")
        for user in final_users:
            print(f"  User {user['id']}: {user['email']}")
        
        # Check user's garments
        cursor.execute("""
            SELECT ug.*, b.name as brand_name, c.name as category_name
            FROM user_garments ug
            JOIN brands b ON ug.brand_id = b.id
            JOIN categories c ON ug.category_id = c.id
            WHERE ug.user_id = 1
            ORDER BY ug.created_at
        """)
        
        garments = cursor.fetchall()
        print(f"\n👕 User's garments:")
        for garment in garments:
            print(f"  {garment['brand_name']} {garment['product_name']} - Size {garment['size_label']}")
        
        # Check user's feedback
        cursor.execute("""
            SELECT ugf.*, fc.feedback_text, ug.product_name
            FROM user_garment_feedback ugf
            JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
            JOIN user_garments ug ON ugf.user_garment_id = ug.id
            WHERE ug.user_id = 1
            ORDER BY ugf.created_at
        """)
        
        feedback = cursor.fetchall()
        print(f"\n💬 User's feedback:")
        for fb in feedback:
            print(f"  {fb['product_name']} - {fb['dimension']}: {fb['feedback_text']}")
        
    except Exception as e:
        cursor.execute("ROLLBACK")
        print(f"❌ Error during cleanup: {str(e)}")
        raise
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("🧹 V10 User Cleanup Tool")
    print("=" * 40)
    cleanup_users()
    print("\n✨ Done!") 