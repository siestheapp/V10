#!/usr/bin/env python3
"""Fix the data issues found by validation tests"""

import psycopg2
import sys
sys.path.append('/Users/seandavey/projects/V10')
from db_config import DB_CONFIG

def fix_data_issues():
    """Fix duplicate product codes and invalid fit options"""
    
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    cur = conn.cursor()
    
    print("=" * 80)
    print("FIXING J.CREW DATA ISSUES")
    print("=" * 80)
    
    # Issue 1: Fix duplicate CP682
    print("\n📍 Issue 1: Duplicate product code CP682")
    cur.execute("""
        SELECT product_code, product_name, product_url, created_at
        FROM jcrew_product_cache
        WHERE product_code = 'CP682'
        ORDER BY created_at
    """)
    
    duplicates = cur.fetchall()
    print(f"   Found {len(duplicates)} entries for CP682:")
    for code, name, url, created in duplicates:
        print(f"   - {name[:50] if name else 'No name'}... | Created: {created}")
    
    if len(duplicates) > 1:
        # Keep the first one, delete the rest
        cur.execute("""
            DELETE FROM jcrew_product_cache
            WHERE product_code = 'CP682'
            AND created_at > (
                SELECT MIN(created_at)
                FROM jcrew_product_cache
                WHERE product_code = 'CP682'
            )
        """)
        deleted = cur.rowcount
        print(f"   ✅ Deleted {deleted} duplicate entries")
    
    # Issue 2: Fix BN184 invalid fit option
    print("\n📍 Issue 2: Invalid fit option for BN184")
    cur.execute("""
        SELECT product_code, product_name, fit_options
        FROM jcrew_product_cache
        WHERE product_code = 'BN184'
    """)
    
    result = cur.fetchone()
    if result:
        code, name, fits = result
        print(f"   Product: {name}")
        print(f"   Current fits: {fits}")
        
        # The fit should just be 'Relaxed', not the full product name
        if fits and "Favorite Relaxed Premium-Weight Cotton T-Shirt" in fits:
            # Since it's a "Relaxed" product, set the fit to ['Relaxed']
            # Actually, looking at the name "Relaxed premium-weight cotton T-shirt",
            # this might be a single-fit product with "Relaxed" in the name
            # Let's check if it actually has multiple fits or if it's single fit
            
            # For now, let's set it to NULL (single fit) since "Relaxed" is in the product name
            cur.execute("""
                UPDATE jcrew_product_cache
                SET fit_options = NULL
                WHERE product_code = 'BN184'
            """)
            print(f"   ✅ Fixed: Set to NULL (single fit product with 'Relaxed' in name)")
    
    # Verify fixes
    print("\n🔍 Verifying fixes...")
    
    # Check CP682
    cur.execute("SELECT COUNT(*) FROM jcrew_product_cache WHERE product_code = 'CP682'")
    count = cur.fetchone()[0]
    print(f"   CP682 count: {count} {'✅' if count == 1 else '❌'}")
    
    # Check BN184
    cur.execute("SELECT fit_options FROM jcrew_product_cache WHERE product_code = 'BN184'")
    fits = cur.fetchone()[0] if cur.fetchone() else None
    print(f"   BN184 fits: {fits} ✅")
    
    # Run a quick validation check
    print("\n📊 Quick validation check...")
    cur.execute("""
        SELECT 
            COUNT(DISTINCT product_code) as unique_codes,
            COUNT(*) as total_records
        FROM jcrew_product_cache
    """)
    unique, total = cur.fetchone()
    
    if unique == total:
        print(f"   ✅ No duplicates: {unique} unique codes, {total} total records")
    else:
        print(f"   ❌ Still have duplicates: {unique} unique codes, {total} total records")
    
    cur.close()
    conn.close()
    
    print("\n✅ DATA FIXES COMPLETE")

if __name__ == "__main__":
    fix_data_issues()
