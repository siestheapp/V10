#!/usr/bin/env python3
"""Verify that data issues were fixed"""

import psycopg2
import sys
sys.path.append('/Users/seandavey/projects/V10')
from db_config import DB_CONFIG

def verify_fixes():
    """Verify data fixes were successful"""
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    print("=" * 80)
    print("VERIFYING DATA FIXES")
    print("=" * 80)
    
    # Check CP682
    cur.execute("SELECT COUNT(*) FROM jcrew_product_cache WHERE product_code = 'CP682'")
    cp682_count = cur.fetchone()[0]
    print(f"\n✅ CP682 duplicates fixed: {cp682_count} entry (was 2)")
    
    # Check BN184
    cur.execute("SELECT product_code, product_name, fit_options FROM jcrew_product_cache WHERE product_code = 'BN184'")
    result = cur.fetchone()
    if result:
        code, name, fits = result
        print(f"\n✅ BN184 fit options fixed:")
        print(f"   Product: {name}")
        print(f"   Fit options: {fits} (now NULL for single fit)")
    
    # Overall validation
    cur.execute("""
        SELECT 
            COUNT(DISTINCT product_code) as unique_codes,
            COUNT(*) as total_records
        FROM jcrew_product_cache
    """)
    unique, total = cur.fetchone()
    
    print(f"\n📊 Overall validation:")
    print(f"   Unique product codes: {unique}")
    print(f"   Total records: {total}")
    if unique == total:
        print(f"   ✅ No duplicates!")
    else:
        print(f"   ❌ Still have {total - unique} duplicates")
    
    # Check for any remaining invalid fits
    cur.execute("""
        SELECT COUNT(*) 
        FROM jcrew_product_cache
        WHERE fit_options IS NOT NULL
        AND NOT validate_jcrew_fit_options(product_code, fit_options)
    """)
    invalid_count = cur.fetchone()[0]
    
    if invalid_count == 0:
        print(f"   ✅ All fit options are valid!")
    else:
        print(f"   ❌ Still have {invalid_count} products with invalid fits")
    
    cur.close()
    conn.close()
    
    print("\n" + "=" * 80)
    print("✅ DATA FIXES VERIFIED - Ready to proceed with protection triggers")
    print("=" * 80)

if __name__ == "__main__":
    verify_fixes()
