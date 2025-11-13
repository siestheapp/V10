#!/usr/bin/env python3
"""Update MP235 with the correct fit options discovered by the scraper"""

import psycopg2
from datetime import datetime
import sys
sys.path.append('/Users/seandavey/projects/V10')
from db_config import DB_CONFIG

def update_mp235():
    """Update MP235 product with correct fit options"""
    
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    cur = conn.cursor()
    
    print("=" * 70)
    print("UPDATING MP235 FIT OPTIONS")
    print("=" * 70)
    
    # First, show current state
    cur.execute("""
        SELECT product_code, product_name, fit_options, updated_at
        FROM jcrew_product_cache
        WHERE product_code = 'MP235'
    """)
    
    result = cur.fetchone()
    if result:
        code, name, current_fits, updated = result
        print(f"\n📍 Current state:")
        print(f"   Product: {code} - {name[:50] if name else 'Unknown'}...")
        print(f"   Current fits: {current_fits}")
        print(f"   Last updated: {updated}")
    
    # Update with correct fits
    new_fits = ['Classic', 'Slim', 'Tall']
    
    cur.execute("""
        UPDATE jcrew_product_cache
        SET fit_options = %s, updated_at = NOW()
        WHERE product_code = 'MP235'
        RETURNING product_code, fit_options, updated_at
    """, (new_fits,))
    
    updated_result = cur.fetchone()
    if updated_result:
        code, new_fits_db, new_updated = updated_result
        print(f"\n✅ Successfully updated!")
        print(f"   New fits: {new_fits_db}")
        print(f"   Updated at: {new_updated}")
    else:
        print(f"\n❌ Update failed - product not found")
    
    cur.close()
    conn.close()
    
    print("\n" + "=" * 70)
    print("✅ MP235 now has correct fit options: Classic, Slim, Tall")
    print("=" * 70)

if __name__ == "__main__":
    update_mp235()
