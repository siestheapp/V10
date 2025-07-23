#!/usr/bin/env python3
"""
Update Banana Republic shirt feedback to "Good Fit" for all dimensions
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

def get_connection():
    """Get database connection"""
    return psycopg2.connect(**DB_CONFIG)

def update_br_feedback():
    """Update Banana Republic shirt feedback to 'Good Fit' for all dimensions"""
    
    print("🔄 UPDATING BANANA REPUBLIC SHIRT FEEDBACK")
    print("=" * 50)
    
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # First, let's see what feedback currently exists for the BR shirt
        print("\n📋 Current feedback for Banana Republic shirt:")
        cursor.execute("""
            SELECT 
                ug.id as garment_id,
                ug.product_name,
                b.name as brand_name,
                ugf.dimension,
                fc.feedback_text,
                ugf.created_at
            FROM user_garments ug
            JOIN brands b ON ug.brand_id = b.id
            JOIN user_garment_feedback ugf ON ug.id = ugf.user_garment_id
            JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
            WHERE b.name = 'Banana Republic' AND ug.user_id = 1
            ORDER BY ugf.dimension, ugf.created_at DESC
        """)
        
        current_feedback = cursor.fetchall()
        
        if not current_feedback:
            print("❌ No Banana Republic shirt found for user 1")
            return
        
        print(f"Found {len(current_feedback)} feedback entries:")
        for fb in current_feedback:
            print(f"  - {fb['dimension']}: {fb['feedback_text']} (ID: {fb['garment_id']})")
        
        # Get the "Good Fit" feedback code ID
        cursor.execute("SELECT id FROM feedback_codes WHERE feedback_text = 'Good Fit'")
        good_fit_code = cursor.fetchone()
        
        if not good_fit_code:
            print("❌ 'Good Fit' feedback code not found")
            return
        
        good_fit_id = good_fit_code['id']
        print(f"\n✅ Found 'Good Fit' feedback code ID: {good_fit_id}")
        
        # Get the garment ID for the BR shirt
        garment_id = current_feedback[0]['garment_id']
        print(f"📏 Updating garment ID: {garment_id}")
        
        # Get available dimensions for Banana Republic
        cursor.execute("""
            SELECT DISTINCT dimension
            FROM user_garment_feedback
            WHERE user_garment_id = %s
        """, (garment_id,))
        
        available_dimensions = [row['dimension'] for row in cursor.fetchall()]
        print(f"📐 Available dimensions to update: {available_dimensions}")
        
        # Update each dimension to "Good Fit"
        updated_count = 0
        for dimension in available_dimensions:
            cursor.execute("""
                UPDATE user_garment_feedback 
                SET feedback_code_id = %s, created_at = NOW()
                WHERE user_garment_id = %s AND dimension = %s
            """, (good_fit_id, garment_id, dimension))
            
            if cursor.rowcount > 0:
                updated_count += cursor.rowcount
                print(f"✅ Updated {dimension} feedback to 'Good Fit'")
        
        # Commit the changes
        conn.commit()
        
        print(f"\n📊 SUMMARY:")
        print(f"   Updated {updated_count} feedback entries")
        print(f"   All dimensions now set to 'Good Fit'")
        
        # Verify the changes
        print(f"\n🔍 Verifying changes:")
        cursor.execute("""
            SELECT 
                ugf.dimension,
                fc.feedback_text,
                ugf.created_at
            FROM user_garment_feedback ugf
            JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
            WHERE ugf.user_garment_id = %s
            ORDER BY ugf.dimension
        """, (garment_id,))
        
        verification = cursor.fetchall()
        for v in verification:
            print(f"  ✅ {v['dimension']}: {v['feedback_text']}")
        
        cursor.close()
        conn.close()
        
        print(f"\n🎉 Banana Republic shirt feedback successfully updated!")
        
    except Exception as e:
        print(f"❌ Error updating BR feedback: {e}")

if __name__ == "__main__":
    update_br_feedback() 