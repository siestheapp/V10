#!/usr/bin/env python3
"""
Test that the feedback shown in the closet is accurate after our changes
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import requests
import json

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

def test_closet_feedback_accuracy():
    """Test that the closet API returns accurate feedback"""
    
    print("🔍 TESTING CLOSET FEEDBACK ACCURACY")
    print("=" * 60)
    
    try:
        # 1. Get closet data from the API
        print("\n📱 Fetching closet data from API...")
        api_url = "http://localhost:8006/user/1/closet"
        response = requests.get(api_url)
        
        if response.status_code != 200:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        closet_data = response.json()
        print(f"✅ Found {len(closet_data)} garments in closet")
        
        # 2. Get actual feedback data from database
        print("\n🗄️  Fetching actual feedback data from database...")
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get all user garments with their feedback
        cursor.execute("""
            SELECT 
                ug.id as garment_id,
                ug.product_name,
                b.name as brand_name,
                ug.size_label,
                -- Get latest feedback for each dimension
                (SELECT fc.feedback_text 
                 FROM user_garment_feedback ugf 
                 JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
                 WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'overall' 
                 ORDER BY ugf.created_at DESC LIMIT 1) as overall_feedback,
                (SELECT fc.feedback_text 
                 FROM user_garment_feedback ugf 
                 JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
                 WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'chest' 
                 ORDER BY ugf.created_at DESC LIMIT 1) as chest_feedback,
                (SELECT fc.feedback_text 
                 FROM user_garment_feedback ugf 
                 JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
                 WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'sleeve' 
                 ORDER BY ugf.created_at DESC LIMIT 1) as sleeve_feedback,
                (SELECT fc.feedback_text 
                 FROM user_garment_feedback ugf 
                 JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
                 WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'neck' 
                 ORDER BY ugf.created_at DESC LIMIT 1) as neck_feedback,
                (SELECT fc.feedback_text 
                 FROM user_garment_feedback ugf 
                 JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
                 WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'waist' 
                 ORDER BY ugf.created_at DESC LIMIT 1) as waist_feedback,
                (SELECT fc.feedback_text 
                 FROM user_garment_feedback ugf 
                 JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
                 WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'length' 
                 ORDER BY ugf.created_at DESC LIMIT 1) as length_feedback
            FROM user_garments ug
            JOIN brands b ON ug.brand_id = b.id
            WHERE ug.user_id = 1 AND ug.owns_garment = true
            ORDER BY ug.created_at DESC
        """)
        
        db_feedback = cursor.fetchall()
        print(f"✅ Found {len(db_feedback)} garments with feedback in database")
        
        # 3. Compare API data with database data
        print("\n🔍 COMPARING API vs DATABASE FEEDBACK:")
        print("-" * 60)
        
        # Create a mapping of garment_id to API data
        api_garments = {g['id']: g for g in closet_data}
        
        discrepancies = []
        
        for db_garment in db_feedback:
            garment_id = db_garment['garment_id']
            brand_name = db_garment['brand_name']
            product_name = db_garment['product_name'] or "Unknown"
            
            print(f"\n👕 {brand_name} - {product_name} (ID: {garment_id})")
            print(f"   Size: {db_garment['size_label']}")
            
            # Check if garment exists in API response
            if garment_id not in api_garments:
                print(f"   ❌ NOT FOUND IN API RESPONSE")
                discrepancies.append(f"Garment {garment_id} missing from API")
                continue
            
            api_garment = api_garments[garment_id]
            
            # Compare each dimension
            dimensions = [
                ('overall', 'fitFeedback', 'Overall'),
                ('chest', 'chestFit', 'Chest'),
                ('sleeve', 'sleeveFit', 'Sleeve'),
                ('neck', 'neckFit', 'Neck'),
                ('waist', 'waistFit', 'Waist')
            ]
            
            for db_dim, api_key, dim_name in dimensions:
                db_value = db_garment[f'{db_dim}_feedback']
                api_value = api_garment.get(api_key)
                
                status = "✅"
                if db_value != api_value:
                    status = "❌"
                    discrepancies.append(f"Garment {garment_id} {dim_name}: DB='{db_value}' vs API='{api_value}'")
                
                print(f"   {status} {dim_name}: DB='{db_value}' | API='{api_value}'")
            
            # Check for length feedback (should be removed)
            length_feedback = db_garment['length_feedback']
            if length_feedback:
                print(f"   ⚠️  LENGTH FEEDBACK STILL EXISTS: {length_feedback}")
                discrepancies.append(f"Garment {garment_id} still has length feedback: {length_feedback}")
        
        # Summary
        print(f"\n📊 SUMMARY:")
        print(f"   Total garments: {len(db_feedback)}")
        print(f"   Discrepancies found: {len(discrepancies)}")
        
        if discrepancies:
            print(f"\n❌ DISCREPANCIES FOUND:")
            for disc in discrepancies:
                print(f"   - {disc}")
        else:
            print(f"\n✅ ALL FEEDBACK MATCHES BETWEEN API AND DATABASE!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error testing closet feedback accuracy: {e}")

if __name__ == "__main__":
    test_closet_feedback_accuracy() 