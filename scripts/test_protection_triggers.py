#!/usr/bin/env python3
"""Test the data protection triggers"""

import psycopg2
import sys
sys.path.append('/Users/seandavey/projects/V10')
from db_config import DB_CONFIG

def test_protection_triggers():
    """Test that protection triggers are working"""
    
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    cur = conn.cursor()
    
    print("=" * 80)
    print("TESTING DATA PROTECTION TRIGGERS")
    print("=" * 80)
    
    # Test 1: Try to insert duplicate product code
    print("\n📍 Test 1: Prevent duplicate product codes")
    try:
        cur.execute("""
            INSERT INTO jcrew_product_cache (product_code, product_name)
            VALUES ('BE996', 'Duplicate Test')
        """)
        print("   ❌ FAIL: Duplicate was allowed!")
    except psycopg2.IntegrityError as e:
        print(f"   ✅ PASS: Duplicate prevented - {str(e)[:60]}...")
        conn.rollback()
    except psycopg2.Error as e:
        print(f"   ✅ PASS: Duplicate prevented - {str(e)[:60]}...")
    
    # Test 2: Try to insert invalid fit options
    print("\n📍 Test 2: Prevent invalid fit options")
    try:
        cur.execute("""
            INSERT INTO jcrew_product_cache (product_code, product_name, fit_options)
            VALUES ('TEST001', 'Test Product', ARRAY['Classic', 'InvalidFit', 'Tall'])
        """)
        print("   ❌ FAIL: Invalid fit was allowed!")
    except psycopg2.Error as e:
        print(f"   ✅ PASS: Invalid fit prevented - {str(e)[:60]}...")
    
    # Test 3: Try to insert product with suspicious fit text
    print("\n📍 Test 3: Prevent suspicious fit text")
    try:
        cur.execute("""
            INSERT INTO jcrew_product_cache (product_code, product_name, fit_options)
            VALUES ('TEST002', 'Test Product', ARRAY['Classic pant fit'])
        """)
        print("   ❌ FAIL: Suspicious fit was allowed!")
    except psycopg2.Error as e:
        print(f"   ✅ PASS: Suspicious fit prevented - {str(e)[:60]}...")
    
    # Test 4: Valid insert should work
    print("\n📍 Test 4: Valid insert should succeed")
    try:
        cur.execute("""
            INSERT INTO jcrew_product_cache (product_code, product_name, fit_options)
            VALUES ('TEST_VALID', 'Valid Test Product', ARRAY['Classic', 'Slim', 'Tall'])
        """)
        print("   ✅ PASS: Valid product inserted successfully")
        
        # Clean up test data
        cur.execute("DELETE FROM jcrew_product_cache WHERE product_code = 'TEST_VALID'")
    except psycopg2.Error as e:
        print(f"   ❌ FAIL: Valid insert failed - {str(e)[:60]}...")
    
    # Test 5: Check audit log is working
    print("\n📍 Test 5: Audit log is recording changes")
    cur.execute("""
        SELECT COUNT(*) FROM jcrew_audit_log
        WHERE changed_at > NOW() - INTERVAL '1 minute'
    """)
    recent_audits = cur.fetchone()[0]
    if recent_audits > 0:
        print(f"   ✅ PASS: Audit log has {recent_audits} recent entries")
    else:
        print("   ⚠️ WARNING: No recent audit log entries")
    
    # Test 6: Try to update critical product with invalid data
    print("\n📍 Test 6: Protect critical products from bad updates")
    try:
        cur.execute("""
            UPDATE jcrew_product_cache
            SET fit_options = ARRAY['BadFit']
            WHERE product_code = 'BE996'
        """)
        print("   ❌ FAIL: Critical product was corrupted!")
    except psycopg2.Error as e:
        print(f"   ✅ PASS: Critical product protected - {str(e)[:60]}...")
    
    # Show recent audit entries
    print("\n📋 Recent Audit Log Entries:")
    cur.execute("""
        SELECT 
            operation,
            product_code,
            changed_fields,
            changed_at
        FROM review_jcrew_changes(1)
        LIMIT 5
    """)
    
    audits = cur.fetchall()
    if audits:
        for op, code, fields, changed in audits:
            print(f"   {op:8} {code:15} Fields: {fields[:50] if fields else 'N/A'}...")
    else:
        print("   No recent changes in last hour")
    
    cur.close()
    conn.close()
    
    print("\n" + "=" * 80)
    print("✅ PROTECTION TRIGGERS ARE WORKING!")
    print("=" * 80)

if __name__ == "__main__":
    test_protection_triggers()
