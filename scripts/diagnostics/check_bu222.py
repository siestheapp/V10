#!/usr/bin/env python3
"""Check what BU222 actually is in our database"""

import psycopg2
import sys
sys.path.append('/Users/seandavey/projects/V10')
from db_config import DB_CONFIG

def check_bu222():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    print("=" * 80)
    print("INVESTIGATING BU222 PRODUCT CODE CONFUSION")
    print("=" * 80)
    
    # Check what's in our database
    cur.execute("""
        SELECT 
            product_code,
            product_name,
            product_url,
            category,
            subcategory,
            gender,
            created_at,
            updated_at
        FROM jcrew_product_cache
        WHERE product_code = 'BU222'
    """)
    
    result = cur.fetchone()
    
    if result:
        code, name, url, cat, subcat, gender, created, updated = result
        print(f"\n📊 DATABASE RECORD FOR BU222:")
        print(f"   Product Name: {name}")
        print(f"   URL: {url}")
        print(f"   Category: {cat}")
        print(f"   Subcategory: {subcat}")
        print(f"   Gender: {gender}")
        print(f"   Created: {created}")
        print(f"   Updated: {updated}")
    else:
        print("\n❌ BU222 not found in database")
    
    # Also check if BU222 appears anywhere else
    cur.execute("""
        SELECT COUNT(*) FROM jcrew_product_cache
        WHERE product_code = 'BU222'
    """)
    count = cur.fetchone()[0]
    print(f"\n📈 Total BU222 entries: {count}")
    
    # Check for any women's products with similar codes
    cur.execute("""
        SELECT product_code, product_name, gender
        FROM jcrew_product_cache
        WHERE product_code LIKE 'BU%'
        AND (gender = 'women' OR product_name ILIKE '%skirt%' OR product_name ILIKE '%women%')
        LIMIT 5
    """)
    
    women_products = cur.fetchall()
    if women_products:
        print(f"\n👗 Women's products with BU prefix:")
        for code, name, gender in women_products:
            print(f"   {code}: {name[:50]}... (Gender: {gender})")
    
    cur.close()
    conn.close()
    
    print("\n" + "=" * 80)
    print("\n⚠️ GOOGLE SEARCH ISSUE:")
    print("Google shows BU222 as 'Pleated Skirt In Faux Leather For Women'")
    print("This could mean:")
    print("1. J.Crew reuses product codes between men's and women's lines")
    print("2. The product code was reassigned over time")
    print("3. Google has cached/indexed incorrect information")
    print("4. Our database has the wrong product for this code")
    print("\nLet's check the actual J.Crew website...")
    print("=" * 80)

if __name__ == "__main__":
    check_bu222()
