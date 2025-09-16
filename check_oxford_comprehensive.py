#!/usr/bin/env python3
"""Comprehensive Oxford shirt analysis - comparing DB to J.Crew website"""

import psycopg2
from db_config import DB_CONFIG
import json
import time

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*80}")
    print(f"{title}")
    print('='*80)

# Products that should be Oxford based on J.Crew website
EXPECTED_OXFORD_PRODUCTS = {
    'ME183': 'Giant-fit oxford shirt',
    'BE996': 'Broken-in organic cotton oxford shirt',
    'CM226': 'Classic oxford two-pocket workshirt',
    'MP235': 'Short-sleeve Broken-in organic cotton oxford shirt',
    'CH326': 'Limited-edition The New Yorker X J.Crew Broken-in oxford shirt'
}

try:
    conn = psycopg2.connect(**DB_CONFIG, connect_timeout=5)
    cur = conn.cursor()
    
    print_section("J.CREW OXFORD SHIRT DATABASE ANALYSIS")
    print(f"Checking against J.Crew website showing 34 items (includes color variants)")
    print(f"URL: https://www.jcrew.com/plp/mens/categories/clothing/shirts?sub-categories=men-shirts-brokeninoxford")
    
    # 1. Check all products that are currently categorized as Oxford
    print_section("CURRENT OXFORD PRODUCTS IN DATABASE")
    
    cur.execute('''
        SELECT product_code, product_name, subcategory, fit_options
        FROM jcrew_product_cache
        WHERE LOWER(subcategory) = 'oxford'
        ORDER BY product_code
    ''')
    
    oxford_products = cur.fetchall()
    print(f"✅ Products with subcategory='oxford': {len(oxford_products)}")
    for code, name, subcat, fits in oxford_products:
        print(f"   {code}: {name[:60]}...")
        if fits:
            print(f"      Fits: {fits}")
    
    # 2. Check products with "oxford" in the name but different subcategory
    print_section("PRODUCTS WITH 'OXFORD' IN NAME BUT DIFFERENT SUBCATEGORY")
    
    cur.execute('''
        SELECT product_code, product_name, subcategory, fit_options
        FROM jcrew_product_cache
        WHERE LOWER(product_name) LIKE '%oxford%'
        AND (LOWER(subcategory) != 'oxford' OR subcategory IS NULL)
        AND LOWER(product_name) NOT LIKE '%t-shirt%'
        ORDER BY product_code
    ''')
    
    miscat_oxford = cur.fetchall()
    print(f"⚠️  Found {len(miscat_oxford)} Oxford products with wrong/missing subcategory:")
    for code, name, subcat, fits in miscat_oxford:
        print(f"   {code}: {name[:60]}...")
        print(f"      Current subcategory: '{subcat}' (should be 'Oxford')")
        if fits:
            print(f"      Fits: {fits}")
    
    # 3. Check expected products
    print_section("CHECKING EXPECTED OXFORD PRODUCTS FROM J.CREW WEBSITE")
    
    found_count = 0
    missing_products = []
    wrong_category = []
    
    for product_code, expected_name in EXPECTED_OXFORD_PRODUCTS.items():
        cur.execute('''
            SELECT product_code, product_name, subcategory, fit_options
            FROM jcrew_product_cache
            WHERE product_code = %s
        ''', (product_code,))
        
        result = cur.fetchone()
        if result:
            code, name, subcat, fits = result
            found_count += 1
            status = "✅"
            if subcat != 'Oxford':
                status = "⚠️"
                wrong_category.append((code, name, subcat))
            print(f"{status} {code}: Found - {name[:50]}...")
            print(f"     Subcategory: {subcat} {'(needs update)' if subcat != 'Oxford' else ''}")
            if fits:
                print(f"     Fits: {fits}")
        else:
            missing_products.append((product_code, expected_name))
            print(f"❌ {product_code}: MISSING - {expected_name}")
    
    # 4. Search for more Oxford patterns
    print_section("SEARCHING FOR ADDITIONAL OXFORD PATTERNS")
    
    # Check for various Oxford naming patterns
    patterns = [
        ("Flex Casual Shirt oxford", "flex%oxford%"),
        ("Baird McNutt oxford", "baird%mcnutt%oxford%"),
        ("Lightweight oxford", "lightweight%oxford%"),
        ("Heritage oxford", "heritage%oxford%"),
        ("Garment-dyed oxford", "garment%dyed%oxford%"),
        ("Untucked oxford", "untucked%oxford%")
    ]
    
    for pattern_name, pattern_query in patterns:
        cur.execute('''
            SELECT COUNT(*)
            FROM jcrew_product_cache
            WHERE LOWER(product_name) LIKE %s
        ''', (pattern_query,))
        
        count = cur.fetchone()[0]
        if count > 0:
            print(f"  Found {count} {pattern_name} products")
    
    # 5. Summary and recommendations
    print_section("SUMMARY & RECOMMENDATIONS")
    
    # Get total unique Oxford products (properly categorized + name matches)
    cur.execute('''
        SELECT COUNT(DISTINCT product_code)
        FROM jcrew_product_cache
        WHERE LOWER(subcategory) = 'oxford'
        OR (LOWER(product_name) LIKE '%oxford%' 
            AND LOWER(product_name) NOT LIKE '%t-shirt%')
    ''')
    
    total_oxford = cur.fetchone()[0]
    
    print(f"\n📊 Database Status:")
    print(f"   • Total Oxford products in DB: {total_oxford}")
    print(f"   • Properly categorized as 'Oxford': {len(oxford_products)}")
    print(f"   • Miscategorized Oxford products: {len(miscat_oxford)}")
    print(f"   • Missing expected products: {len(missing_products)}")
    
    print(f"\n🎯 J.Crew Website Status:")
    print(f"   • Website shows: 34 items (includes color duplicates)")
    print(f"   • Estimated unique products: ~15-20 (after removing color variants)")
    
    if missing_products:
        print(f"\n❌ Missing Products to Add:")
        for code, name in missing_products:
            print(f"   • {code}: {name}")
    
    if wrong_category:
        print(f"\n⚠️  Products Needing Subcategory Update to 'Oxford':")
        for code, name, current_cat in wrong_category:
            print(f"   • {code}: {name[:50]}... (currently: '{current_cat}')")
    
    print(f"\n💡 Recommendations:")
    print(f"   1. Add missing product ME183 (Giant-fit oxford shirt)")
    print(f"   2. Update BE996 subcategory from 'Bowery' to 'Oxford'")
    print(f"   3. Run full Oxford product scrape to capture all variants")
    print(f"   4. Verify all products with 'oxford' in name have correct subcategory")
    
    # 6. Look for potential Oxford products without "oxford" in name
    print_section("CHECKING OTHER POTENTIAL OXFORD PRODUCTS")
    
    # Check Bowery category since BE996 is there
    cur.execute('''
        SELECT product_code, product_name, product_url
        FROM jcrew_product_cache
        WHERE LOWER(subcategory) = 'bowery'
        ORDER BY product_code
        LIMIT 10
    ''')
    
    bowery_products = cur.fetchall()
    if bowery_products:
        print(f"\n🔍 Sample 'Bowery' products (may include Oxfords):")
        for code, name, url in bowery_products:
            # Check if URL contains oxford
            is_oxford_url = 'oxford' in (url or '').lower()
            marker = "→ LIKELY OXFORD" if is_oxford_url else ""
            print(f"   {code}: {name[:50]}... {marker}")
            if url and is_oxford_url:
                print(f"      URL: {url[:80]}...")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
