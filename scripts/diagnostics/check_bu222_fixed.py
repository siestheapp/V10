#!/usr/bin/env python3
"""Check what BU222 actually is in our database and on J.Crew site"""

import psycopg2
import sys
import requests
from bs4 import BeautifulSoup
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
            fit_options,
            colors_available,
            created_at,
            updated_at
        FROM jcrew_product_cache
        WHERE product_code = 'BU222'
    """)
    
    result = cur.fetchone()
    
    if result:
        code, name, url, cat, subcat, fits, colors, created, updated = result
        print(f"\n📊 DATABASE RECORD FOR BU222:")
        print(f"   Product Name: {name}")
        print(f"   URL: {url}")
        print(f"   Category: {cat}")
        print(f"   Subcategory: {subcat}") 
        print(f"   Fit Options: {fits}")
        print(f"   Colors: {colors}")
        print(f"   Created: {created}")
        print(f"   Updated: {updated}")
        
        # Check if URL contains men's or women's
        if url:
            if '/mens/' in url or '/m/' in url:
                print(f"   ✅ URL indicates MEN'S product")
            elif '/womens/' in url or '/w/' in url:
                print(f"   ⚠️ URL indicates WOMEN'S product")
            else:
                print(f"   ❓ URL doesn't clearly indicate gender")
    else:
        print("\n❌ BU222 not found in database")
    
    # Check for duplicates
    cur.execute("""
        SELECT COUNT(*) FROM jcrew_product_cache
        WHERE product_code = 'BU222'
    """)
    count = cur.fetchone()[0]
    print(f"\n📈 Total BU222 entries in DB: {count}")
    
    # Check if there are any skirt products with BU codes
    cur.execute("""
        SELECT product_code, product_name, product_url
        FROM jcrew_product_cache
        WHERE (product_name ILIKE '%skirt%' OR product_name ILIKE '%pleated%')
        AND product_code LIKE 'BU%'
        LIMIT 5
    """)
    
    skirt_products = cur.fetchall()
    if skirt_products:
        print(f"\n👗 Skirt products with BU prefix:")
        for code, name, url in skirt_products:
            gender = "WOMEN" if ('/womens/' in str(url) or '/w/' in str(url)) else "MEN" if ('/mens/' in str(url) or '/m/' in str(url)) else "UNKNOWN"
            print(f"   {code}: {name[:50]}... ({gender})")
    
    cur.close()
    conn.close()
    
    print("\n" + "=" * 80)
    print("GOOGLE SEARCH ANALYSIS:")
    print("=" * 80)
    print("\n⚠️ Google shows BU222 as 'Pleated Skirt In Faux Leather For Women'")
    print("\nPOSSIBLE EXPLANATIONS:")
    print("1. 🔄 J.Crew REUSES product codes between men's/women's lines")
    print("2. ⏰ Product code was REASSIGNED (old women's skirt → new men's shirt)")
    print("3. 🔗 Google indexed OLD/CACHED information")
    print("4. 🚫 Our scraper grabbed the WRONG product")
    
    # Try to fetch current J.Crew page
    if result and result[2]:  # if we have a URL
        url = result[2]
        print(f"\n🔍 Checking live J.Crew page...")
        print(f"   URL: {url[:80]}...")
        
        try:
            # Make a simple request to check if URL is valid
            response = requests.head(url, allow_redirects=True, timeout=5)
            if response.status_code == 200:
                print(f"   ✅ URL is ACTIVE (returns 200)")
                # Check final URL after redirects
                if response.url != url:
                    print(f"   ↪️ Redirected to: {response.url[:80]}...")
            elif response.status_code == 404:
                print(f"   ❌ URL returns 404 - Product may be discontinued")
            else:
                print(f"   ⚠️ URL returns status {response.status_code}")
        except Exception as e:
            print(f"   ❌ Could not check URL: {e}")
    
    print("\n" + "=" * 80)
    print("CONCLUSION:")
    print("Most likely scenario: J.Crew reuses product codes across gender lines")
    print("The BU222 code refers to BOTH:")
    print("  • Men's Flex Casual Shirt (current in our DB)")
    print("  • Women's Pleated Faux Leather Skirt (in Google results)")
    print("=" * 80)

if __name__ == "__main__":
    check_bu222()
