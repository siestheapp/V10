#!/usr/bin/env python3
"""
Debug script to test J.Crew analysis components step by step
"""

import sys
import os
sys.path.append('/Users/seandavey/projects/V10')

print("🔍 Debug J.Crew Analysis Script")
print("=" * 50)

# Step 1: Test imports
print("Step 1: Testing imports...")
try:
    import psycopg2
    print("✅ psycopg2 imported successfully")
except ImportError as e:
    print(f"❌ Failed to import psycopg2: {e}")
    sys.exit(1)

try:
    from db_config import DB_CONFIG
    print("✅ DB_CONFIG imported successfully")
    print(f"   Database host: {DB_CONFIG.get('host', 'N/A')}")
except ImportError as e:
    print(f"❌ Failed to import DB_CONFIG: {e}")
    sys.exit(1)

# Step 2: Test database connection
print("\nStep 2: Testing database connection...")
try:
    conn = psycopg2.connect(**DB_CONFIG)
    print("✅ Database connection established")
    
    cur = conn.cursor()
    cur.execute("SELECT version()")
    version = cur.fetchone()
    print(f"   PostgreSQL version: {version[0][:50]}...")
    
    cur.close()
    conn.close()
    print("✅ Database connection closed successfully")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    print("   This is likely the issue causing the script to hang")
    sys.exit(1)

# Step 3: Test network connectivity
print("\nStep 3: Testing basic network connectivity...")
try:
    import urllib.request
    import urllib.parse
    
    # Test simple HTTP request
    req = urllib.request.Request("https://httpbin.org/get")
    with urllib.request.urlopen(req, timeout=10) as response:
        data = response.read()
        print(f"✅ Basic HTTP request successful ({len(data)} bytes)")
except Exception as e:
    print(f"❌ Network request failed: {e}")

# Step 4: Test Jina proxy
print("\nStep 4: Testing Jina.ai proxy...")
try:
    proxy_url = "https://r.jina.ai/http://httpbin.org/get"
    req = urllib.request.Request(proxy_url)
    with urllib.request.urlopen(req, timeout=15) as response:
        data = response.read()
        print(f"✅ Jina proxy request successful ({len(data)} bytes)")
except Exception as e:
    print(f"❌ Jina proxy request failed: {e}")
    print("   This could be why J.Crew scraping fails")

# Step 5: Test simple database query
print("\nStep 5: Testing database queries...")
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # Check if jcrew_product_cache exists
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'jcrew_product_cache'
        )
    """)
    cache_exists = cur.fetchone()[0]
    print(f"   jcrew_product_cache table exists: {cache_exists}")
    
    # Check if brands table exists
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'brands'
        )
    """)
    brands_exists = cur.fetchone()[0]
    print(f"   brands table exists: {brands_exists}")
    
    if brands_exists:
        cur.execute("SELECT COUNT(*) FROM brands WHERE LOWER(name) LIKE '%j.crew%'")
        jcrew_brands = cur.fetchone()[0]
        print(f"   J.Crew brands found: {jcrew_brands}")
    
    cur.close()
    conn.close()
    print("✅ Database queries completed successfully")
    
except Exception as e:
    print(f"❌ Database query failed: {e}")

print("\n" + "=" * 50)
print("🎯 Debug completed!")
print("If all steps passed, the main script should work.")
print("If any step failed, that's likely causing the hang/crash.")

