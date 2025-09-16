#!/usr/bin/env python3
"""Check J.Crew Oxford shirt data with progress indicators"""

import psycopg2
from db_config import DB_CONFIG
import time
import sys

def print_progress(message):
    """Print with timestamp"""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")
    sys.stdout.flush()

try:
    print_progress("Starting J.Crew Oxford shirt check...")
    
    # Connect with timeout
    print_progress("Connecting to database...")
    conn = psycopg2.connect(**DB_CONFIG, connect_timeout=5)
    conn.autocommit = True
    cur = conn.cursor()
    print_progress("✅ Connected to database")
    
    print('=' * 80)
    print('CHECKING OXFORD PRODUCTS')
    print('=' * 80)
    
    # Check if ME183 exists
    print_progress("Checking if ME183 exists...")
    cur.execute('''
        SELECT product_code, product_name, fit_options, subcategory
        FROM jcrew_product_cache
        WHERE product_code = 'ME183'
    ''')
    
    result = cur.fetchone()
    if result:
        print(f'✅ ME183 exists: {result[1]}')
        print(f'   Fits: {result[2]}')
        print(f'   Subcategory: {result[3]}')
    else:
        print('⚠️  ME183 not found - would need to be added')
    
    # Check BE996
    print_progress("\nChecking BE996 status...")
    cur.execute('''
        SELECT product_code, product_name, fit_options, subcategory
        FROM jcrew_product_cache
        WHERE product_code = 'BE996'
    ''')
    
    result = cur.fetchone()
    if result:
        print(f'✅ BE996 exists: {result[1]}')
        print(f'   Fits: {result[2]}')
        print(f'   Subcategory: {result[3]}')
    else:
        print('⚠️  BE996 not found')
    
    # Count Oxford shirts
    print_progress("\nCounting Oxford shirts...")
    cur.execute('''
        SELECT COUNT(*)
        FROM jcrew_product_cache
        WHERE LOWER(subcategory) = 'oxford'
        OR (LOWER(product_name) LIKE '%oxford shirt%' 
            AND LOWER(product_name) NOT LIKE '%t-shirt%')
    ''')
    
    total = cur.fetchone()[0]
    print(f'\n✅ Total Oxford shirts: {total}')
    
    # Show sample of Oxford shirts
    print_progress("\nFetching sample Oxford shirts...")
    cur.execute('''
        SELECT product_code, product_name, fit_options
        FROM jcrew_product_cache
        WHERE LOWER(subcategory) = 'oxford'
        OR (LOWER(product_name) LIKE '%oxford shirt%' 
            AND LOWER(product_name) NOT LIKE '%t-shirt%')
        ORDER BY product_code
        LIMIT 5
    ''')
    
    print("\n📋 Sample Oxford shirts:")
    for code, name, fits in cur.fetchall():
        print(f"   {code}: {name[:50]}...")
        if fits:
            print(f"      Fits: {fits}")
    
    print_progress("\nClosing database connection...")
    cur.close()
    conn.close()
    print_progress("✅ Check complete!")
    
except psycopg2.OperationalError as e:
    print(f"❌ Database connection error: {e}")
    print("The database might be unavailable or the connection is timing out.")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
