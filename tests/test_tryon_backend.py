#!/usr/bin/env python3
"""
Test script to verify try-on backend is working correctly
Run this to test the database integration without the iOS app
"""

import requests
import json
from datetime import datetime
import psycopg2
from db_config import DB_CONFIG

# Backend URL (make sure backend is running)
BASE_URL = "http://localhost:8000"

def test_database_connection():
    """Test that we can connect to the database"""
    print("1️⃣ Testing database connection...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM try_on_sessions")
        count = cur.fetchone()[0]
        print(f"   ✅ Connected! Found {count} existing sessions")
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
        return False

def test_create_session():
    """Test creating a try-on session"""
    print("\n2️⃣ Testing session creation...")
    
    # First, add the endpoint to your app.py if it doesn't exist
    try:
        response = requests.post(f"{BASE_URL}/tryon/start", json={
            "product_url": "https://www.jcrew.com/p/mens/categories/clothing/shirts/casual/BH290",
            "user_id": "1"
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Session created!")
            print(f"      Session ID: {data.get('session_id', 'N/A')}")
            print(f"      Brand: {data.get('brand', 'N/A')}")
            return data.get('session_id')
        else:
            print(f"   ❌ Failed: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Cannot connect to backend. Is it running?")
        print(f"      Run: cd src/ios_app/Backend && python app.py")
        return None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def test_submit_feedback(session_id=None):
    """Test submitting feedback"""
    print("\n3️⃣ Testing feedback submission...")
    
    if not session_id:
        session_id = "test_session_" + str(int(datetime.now().timestamp()))
    
    try:
        response = requests.post(f"{BASE_URL}/tryon/submit", json={
            "session_id": session_id,
            "product_url": "https://www.jcrew.com/p/mens/categories/clothing/shirts/casual/BH290",
            "brand_id": 4,  # J.Crew
            "size_tried": "M",
            "feedback": {
                "overall": 4,
                "chest": 3,
                "length": 4
            },
            "notes": "Test feedback from script",
            "try_on_location": "Home"
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Feedback submitted!")
            return True
        else:
            print(f"   ❌ Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def verify_data_saved():
    """Check if data was actually saved to database"""
    print("\n4️⃣ Verifying data in database...")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Check sessions
        cur.execute("""
            SELECT id, user_id, store_brand, status, created_at 
            FROM try_on_sessions 
            ORDER BY created_at DESC 
            LIMIT 1
        """)
        session = cur.fetchone()
        if session:
            print(f"   ✅ Latest session:")
            print(f"      ID: {session[0]}")
            print(f"      User: {session[1]}")
            print(f"      Brand: {session[2]}")
            print(f"      Status: {session[3]}")
        else:
            print(f"   ⚠️ No sessions found in database")
        
        # Check items
        cur.execute("""
            SELECT id, session_id, size_tried, final_decision 
            FROM try_on_items 
            ORDER BY id DESC 
            LIMIT 1
        """)
        item = cur.fetchone()
        if item:
            print(f"   ✅ Latest try-on item:")
            print(f"      ID: {item[0]}")
            print(f"      Session: {item[1]}")
            print(f"      Size: {item[2]}")
            print(f"      Decision: {item[3]}")
        else:
            print(f"   ⚠️ No try-on items found in database")
        
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"   ❌ Database check failed: {e}")
        return False

def create_test_data():
    """Create test data directly in database"""
    print("\n5️⃣ Creating test data directly...")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Create a test session
        cur.execute("""
            INSERT INTO try_on_sessions (
                user_id, store_location, store_brand, 
                session_date, status, created_at
            ) VALUES (1, 'Home', 'J.Crew', NOW(), 'active', NOW())
            RETURNING id
        """)
        session_id = cur.fetchone()[0]
        print(f"   ✅ Created session #{session_id}")
        
        # Create a test garment if needed
        cur.execute("""
            SELECT id FROM garments WHERE product_name LIKE '%Test Shirt%' LIMIT 1
        """)
        result = cur.fetchone()
        
        if result:
            garment_id = result[0]
        else:
            cur.execute("""
                INSERT INTO garments (
                    brand_id, category_id, product_name, 
                    product_url, created_at
                ) VALUES (4, 1, 'Test Shirt', 'https://test.com', NOW())
                RETURNING id
            """)
            garment_id = cur.fetchone()[0]
            print(f"   ✅ Created test garment #{garment_id}")
        
        # Create a test try-on item
        cur.execute("""
            INSERT INTO try_on_items (
                session_id, garment_id, size_tried, 
                try_order, final_decision, created_at
            ) VALUES (%s, %s, 'M', 1, 'pending', NOW())
            RETURNING id
        """, (session_id, garment_id))
        item_id = cur.fetchone()[0]
        print(f"   ✅ Created try-on item #{item_id}")
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            "session_id": session_id,
            "garment_id": garment_id,
            "item_id": item_id
        }
    except Exception as e:
        print(f"   ❌ Failed to create test data: {e}")
        return None

def main():
    print("=" * 60)
    print("🧪 TRY-ON BACKEND TEST SUITE")
    print("=" * 60)
    
    # Test 1: Database
    if not test_database_connection():
        print("\n❌ Cannot proceed without database connection")
        return
    
    # Test 2: Create session via API
    session_id = test_create_session()
    
    # Test 3: Submit feedback
    if session_id:
        test_submit_feedback(session_id)
    
    # Test 4: Verify in database
    verify_data_saved()
    
    # Test 5: Create test data directly
    test_data = create_test_data()
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    # Final check
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) FROM try_on_sessions")
    session_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM try_on_items")
    item_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM user_garment_feedback")
    feedback_count = cur.fetchone()[0]
    
    print(f"✅ Database has:")
    print(f"   - {session_count} try-on sessions")
    print(f"   - {item_count} try-on items")
    print(f"   - {feedback_count} feedback records")
    
    if test_data:
        print(f"\n📝 Use these IDs for testing:")
        print(f"   - Session ID: {test_data['session_id']}")
        print(f"   - Garment ID: {test_data['garment_id']}")
        print(f"   - Item ID: {test_data['item_id']}")
    
    cur.close()
    conn.close()
    
    print("\n✨ Done! Your backend is " + 
          ("ready" if session_count > 0 or item_count > 0 else "not saving data properly"))

if __name__ == "__main__":
    main()
