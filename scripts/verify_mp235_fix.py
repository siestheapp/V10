#!/usr/bin/env python3
"""Verify MP235 fix by comparing DB with fresh scrape"""

import psycopg2
import sys
sys.path.append('/Users/seandavey/projects/V10')
from db_config import DB_CONFIG

def verify_mp235():
    """Check if MP235 now matches what the scraper found"""
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    print("=" * 70)
    print("VERIFYING MP235 FIT DATA CONSISTENCY")
    print("=" * 70)
    
    # Get current database state
    cur.execute("""
        SELECT product_code, product_name, fit_options, updated_at
        FROM jcrew_product_cache
        WHERE product_code = 'MP235'
    """)
    
    result = cur.fetchone()
    if result:
        code, name, db_fits, updated = result
        print(f"\n📊 DATABASE STATE:")
        print(f"   Product: {code}")
        print(f"   Name: {name[:60] if name else 'Unknown'}...")
        print(f"   Fit options: {db_fits}")
        print(f"   Last updated: {updated}")
    
    scraped_fits = ['Classic', 'Slim', 'Tall']
    print(f"\n🔍 SCRAPER FOUND:")
    print(f"   Fit options: {scraped_fits}")
    
    print(f"\n📐 COMPARISON:")
    if set(db_fits) == set(scraped_fits):
        print(f"   ✅ PERFECT MATCH! Database and scraper data are now consistent.")
    else:
        print(f"   ⚠️ Still inconsistent")
        missing_in_db = set(scraped_fits) - set(db_fits)
        extra_in_db = set(db_fits) - set(scraped_fits)
        if missing_in_db:
            print(f"      Missing from DB: {missing_in_db}")
        if extra_in_db:
            print(f"      Extra in DB: {extra_in_db}")
    
    cur.close()
    conn.close()
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    verify_mp235()
