#!/usr/bin/env python3
"""
Test script to verify measurement linking is working
"""

import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection
DB_CONFIG = {
    "database": "postgres",
    "user": "postgres.lbilxlkchzpducggkrxx",
    "password": "efvTower12",
    "host": "aws-0-us-east-2.pooler.supabase.com",
    "port": "6543"
}

def test_measurement_linking():
    """Test the measurement linking functionality"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    print("🧪 TESTING MEASUREMENT LINKING SYSTEM")
    print("=" * 50)
    
    # Test 1: Check existing garments
    print("\n1️⃣ CHECKING EXISTING GARMENTS:")
    cursor.execute("""
        SELECT ug.id, ug.size_label, ug.size_guide_id, ug.size_guide_entry_id,
               b.name as brand_name, c.name as category_name
        FROM user_garments ug
        JOIN brands b ON ug.brand_id = b.id
        JOIN categories c ON ug.category_id = c.id
        ORDER BY ug.id
    """)
    garments = cursor.fetchall()
    
    for g in garments:
        status = "✅ FULLY LINKED" if g['size_guide_entry_id'] else "⚠️ PARTIAL" if g['size_guide_id'] else "❌ NO LINK"
        print(f"  Garment {g['id']}: {g['brand_name']} {g['size_label']} - {status}")
    
    # Test 2: Show what combinations should work
    print("\n2️⃣ AVAILABLE SIZE GUIDE COMBINATIONS:")
    cursor.execute("""
        SELECT sg.id, b.name as brand_name, c.name as category_name, 
               sg.gender, sg.fit_type, COUNT(sge.id) as size_count
        FROM size_guides sg
        JOIN brands b ON sg.brand_id = b.id
        JOIN categories c ON sg.category_id = c.id
        LEFT JOIN size_guide_entries sge ON sg.id = sge.size_guide_id
        GROUP BY sg.id, b.name, c.name, sg.gender, sg.fit_type
        ORDER BY b.name
    """)
    guides = cursor.fetchall()
    
    for g in guides:
        print(f"  ✅ {g['brand_name']} | {g['category_name']} | {g['gender']} | {g['fit_type']} | {g['size_count']} sizes")
    
    # Test 3: Show available sizes for each guide
    print("\n3️⃣ AVAILABLE SIZES BY BRAND:")
    cursor.execute("""
        SELECT b.name as brand_name, sg.gender, sg.fit_type,
               STRING_AGG(sge.size_label, ', ' ORDER BY sge.size_label) as sizes
        FROM size_guides sg
        JOIN brands b ON sg.brand_id = b.id
        JOIN size_guide_entries sge ON sg.id = sge.size_guide_id
        GROUP BY b.name, sg.gender, sg.fit_type
        ORDER BY b.name
    """)
    size_info = cursor.fetchall()
    
    for s in size_info:
        print(f"  {s['brand_name']} ({s['gender']}, {s['fit_type']}): {s['sizes']}")
    
    # Test 4: Check feedback with measurements
    print("\n4️⃣ FEEDBACK WITH MEASUREMENT DATA:")
    cursor.execute("""
        SELECT ugf.dimension, fc.feedback_text, ug.id as garment_id,
               b.name as brand_name, ug.size_label,
               CASE 
                   WHEN ug.size_guide_entry_id IS NOT NULL THEN 'Has measurements'
                   ELSE 'No measurements'
               END as measurement_status
        FROM user_garment_feedback ugf
        JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
        JOIN user_garments ug ON ugf.user_garment_id = ug.id
        JOIN brands b ON ug.brand_id = b.id
        ORDER BY ugf.created_at DESC
    """)
    feedback = cursor.fetchall()
    
    if feedback:
        for f in feedback:
            print(f"  📝 {f['brand_name']} {f['size_label']} | {f['dimension']}: {f['feedback_text']} | {f['measurement_status']}")
    else:
        print("  📝 No feedback data yet")
    
    # Test 5: Sample measurement data
    print("\n5️⃣ SAMPLE MEASUREMENT DATA:")
    cursor.execute("""
        SELECT sge.size_label, sge.chest_range, sge.waist_range, sge.sleeve_range,
               b.name as brand_name
        FROM size_guide_entries sge
        JOIN size_guides sg ON sge.size_guide_id = sg.id
        JOIN brands b ON sg.brand_id = b.id
        WHERE sge.chest_range IS NOT NULL
        LIMIT 3
    """)
    measurements = cursor.fetchall()
    
    for m in measurements:
        print(f"  📏 {m['brand_name']} {m['size_label']}: Chest={m['chest_range']}, Waist={m['waist_range']}, Sleeve={m['sleeve_range']}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 50)
    print("🎯 NEXT STEPS:")
    print("1. Add a garment using the web interface")
    print("2. Check if it gets linked to measurements")
    print("3. Provide feedback and verify measurement association")
    print("4. Test recommendation engine with measurement data")

if __name__ == "__main__":
    test_measurement_linking() 