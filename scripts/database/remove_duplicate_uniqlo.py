#!/usr/bin/env python3
"""
Remove duplicate Medium Uniqlo shirt - keep the older one, delete the newer one
"""

import psycopg2
from psycopg2.extras import RealDictCursor

# Database configuration
DB_CONFIG = {
    "database": "postgres",
    "user": "postgres.lbilxlkchzpducggkrxx",
    "password": "efvTower12",
    "host": "aws-0-us-east-2.pooler.supabase.com",
    "port": "6543"
}

def remove_duplicate_uniqlo():
    """Remove the newer duplicate Medium Uniqlo shirt"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print("🔍 Checking for duplicate Medium Uniqlo shirts...")
        
        # Find all Medium Uniqlo SUPIMA Cotton T-Shirt entries for user1
        cursor.execute("""
            SELECT ug.id, ug.size_label, ug.created_at, ug.owns_garment
            FROM user_garments ug
            JOIN brands b ON ug.brand_id = b.id
            WHERE ug.user_id = 1 
            AND b.name = 'Uniqlo'
            AND ug.product_name ILIKE '%SUPIMA Cotton T-Shirt%'
            AND ug.size_label = 'M'
            ORDER BY ug.created_at
        """)
        
        medium_shirts = cursor.fetchall()
        
        if len(medium_shirts) < 2:
            print("✅ No duplicates found - only one Medium shirt exists.")
            return
        
        print(f"\n📋 Found {len(medium_shirts)} Medium Uniqlo shirts:")
        print("-" * 60)
        for shirt in medium_shirts:
            print(f"ID: {shirt['id']} | Size: {shirt['size_label']} | Created: {shirt['created_at']}")
        
        # Keep the oldest one, delete the newer one(s)
        keep_shirt = medium_shirts[0]  # Oldest
        delete_shirts = medium_shirts[1:]  # Newer ones
        
        print(f"\n✅ Keeping oldest shirt:")
        print(f"  ID: {keep_shirt['id']} | Created: {keep_shirt['created_at']}")
        
        print(f"\n🗑️  Deleting {len(delete_shirts)} newer duplicate(s):")
        for shirt in delete_shirts:
            print(f"  ID: {shirt['id']} | Created: {shirt['created_at']}")
        
        # Confirm deletion
        confirm = input(f"\n❓ Are you sure you want to delete {len(delete_shirts)} duplicate shirt(s)? (yes/no): ")
        if confirm.lower() != 'yes':
            print("❌ Deletion cancelled.")
            return
        
        # Delete the newer duplicates
        delete_ids = [shirt['id'] for shirt in delete_shirts]
        
        # First, delete any feedback for these garments
        cursor.execute("""
            DELETE FROM user_garment_feedback 
            WHERE user_garment_id = ANY(%s)
        """, (delete_ids,))
        
        feedback_deleted = cursor.rowcount
        print(f"🗑️  Deleted {feedback_deleted} feedback entries for duplicates")
        
        # Then delete the garments
        cursor.execute("""
            DELETE FROM user_garments 
            WHERE id = ANY(%s)
        """, (delete_ids,))
        
        garments_deleted = cursor.rowcount
        conn.commit()
        
        print(f"✅ Successfully deleted {garments_deleted} duplicate shirt(s)!")
        
        # Verify results
        cursor.execute("""
            SELECT ug.id, ug.size_label, ug.created_at, ug.owns_garment
            FROM user_garments ug
            JOIN brands b ON ug.brand_id = b.id
            WHERE ug.user_id = 1 
            AND b.name = 'Uniqlo'
            AND ug.product_name ILIKE '%SUPIMA Cotton T-Shirt%'
            ORDER BY ug.size_label, ug.created_at
        """)
        
        remaining_shirts = cursor.fetchall()
        
        print(f"\n📊 Final Uniqlo shirts in closet:")
        if remaining_shirts:
            for shirt in remaining_shirts:
                print(f"  ID: {shirt['id']} | Size: {shirt['size_label']} | Created: {shirt['created_at']}")
        else:
            print("  No Uniqlo shirts remaining")
        
        print(f"\n🎉 Cleanup complete! User1 now has only one Medium Uniqlo shirt.")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    remove_duplicate_uniqlo()

