#!/usr/bin/env python3
"""
Fix Uniqlo shirt sizes in user1's closet - remove incorrect sizes, keep only Medium
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

def fix_uniqlo_shirt_sizes():
    """Remove incorrect Uniqlo shirt sizes, keep only Medium"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print("🔍 Analyzing Uniqlo shirts in user1's closet...")
        
        # Find all Uniqlo SUPIMA Cotton T-Shirt entries for user1
        cursor.execute("""
            SELECT ug.id, ug.size_label, ug.created_at, ug.owns_garment
            FROM user_garments ug
            JOIN brands b ON ug.brand_id = b.id
            WHERE ug.user_id = 1 
            AND b.name = 'Uniqlo'
            AND ug.product_name ILIKE '%SUPIMA Cotton T-Shirt%'
            ORDER BY ug.size_label, ug.created_at
        """)
        
        uniqlo_shirts = cursor.fetchall()
        
        if not uniqlo_shirts:
            print("✅ No Uniqlo SUPIMA Cotton T-Shirts found in user1's closet.")
            return
        
        print(f"\n📋 Found {len(uniqlo_shirts)} Uniqlo SUPIMA Cotton T-Shirts:")
        print("-" * 60)
        for shirt in uniqlo_shirts:
            print(f"ID: {shirt['id']} | Size: {shirt['size_label']} | Owns: {shirt['owns_garment']} | Created: {shirt['created_at']}")
        
        # Check which sizes exist
        sizes = [shirt['size_label'] for shirt in uniqlo_shirts]
        print(f"\n📏 Sizes found: {', '.join(sizes)}")
        
        # Find Medium size
        medium_shirts = [s for s in uniqlo_shirts if s['size_label'].upper() in ['M', 'MEDIUM', 'MED']]
        
        if not medium_shirts:
            print("❌ No Medium size found! User should have Medium size.")
            print("Please add the correct Medium size shirt first.")
            return
        
        print(f"\n✅ Found {len(medium_shirts)} Medium size shirt(s):")
        for shirt in medium_shirts:
            print(f"  ID: {shirt['id']} | Size: {shirt['size_label']}")
        
        # Find incorrect sizes to remove
        incorrect_shirts = [s for s in uniqlo_shirts if s['size_label'].upper() not in ['M', 'MEDIUM', 'MED']]
        
        if not incorrect_shirts:
            print("✅ All Uniqlo shirts are already Medium size!")
            return
        
        print(f"\n🗑️  Found {len(incorrect_shirts)} incorrect sizes to remove:")
        for shirt in incorrect_shirts:
            print(f"  ID: {shirt['id']} | Size: {shirt['size_label']}")
        
        # Confirm deletion
        confirm = input(f"\n❓ Are you sure you want to delete {len(incorrect_shirts)} incorrect size shirts? (yes/no): ")
        if confirm.lower() != 'yes':
            print("❌ Deletion cancelled.")
            return
        
        # Delete incorrect sizes
        incorrect_ids = [shirt['id'] for shirt in incorrect_shirts]
        
        # First, delete any feedback for these garments
        cursor.execute("""
            DELETE FROM user_garment_feedback 
            WHERE user_garment_id = ANY(%s)
        """, (incorrect_ids,))
        
        feedback_deleted = cursor.rowcount
        print(f"🗑️  Deleted {feedback_deleted} feedback entries for incorrect sizes")
        
        # Then delete the garments
        cursor.execute("""
            DELETE FROM user_garments 
            WHERE id = ANY(%s)
        """, (incorrect_ids,))
        
        garments_deleted = cursor.rowcount
        conn.commit()
        
        print(f"✅ Successfully deleted {garments_deleted} incorrect size shirts!")
        
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
                print(f"  ID: {shirt['id']} | Size: {shirt['size_label']} | Owns: {shirt['owns_garment']}")
        else:
            print("  No Uniqlo shirts remaining")
        
        print(f"\n🎉 Cleanup complete! User1 now has only the correct Medium size Uniqlo shirt.")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    fix_uniqlo_shirt_sizes()

