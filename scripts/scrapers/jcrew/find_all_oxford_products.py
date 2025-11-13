#!/usr/bin/env python3
"""Find ALL Oxford products in database by checking URLs and names"""

import psycopg2
from db_config import DB_CONFIG
import re

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*80}")
    print(f"{title}")
    print('='*80)

try:
    conn = psycopg2.connect(**DB_CONFIG, connect_timeout=5)
    cur = conn.cursor()
    
    print_section("FINDING ALL J.CREW OXFORD PRODUCTS")
    
    # 1. Find all products with 'oxford' in URL
    print_section("PRODUCTS WITH 'OXFORD' IN URL")
    
    cur.execute('''
        SELECT product_code, product_name, subcategory, product_url, fit_options
        FROM jcrew_product_cache
        WHERE LOWER(product_url) LIKE '%oxford%'
        ORDER BY product_code
    ''')
    
    url_oxford_products = cur.fetchall()
    print(f"Found {len(url_oxford_products)} products with 'oxford' in URL:")
    
    correctly_categorized = []
    needs_update = []
    
    for code, name, subcat, url, fits in url_oxford_products:
        if subcat == 'Oxford':
            correctly_categorized.append((code, name, fits))
            print(f"✅ {code}: {name[:50]}... [Correct category: Oxford]")
        else:
            needs_update.append((code, name, subcat, fits))
            print(f"⚠️  {code}: {name[:50]}... [Wrong category: {subcat}]")
        
        # Show URL pattern
        if '/broken-in-oxford/' in url:
            print(f"     → URL indicates: Broken-in Oxford")
        elif '/oxford/' in url:
            print(f"     → URL indicates: Oxford category")
        
        if fits:
            print(f"     Fits: {fits}")
    
    # 2. Check for products with oxford-like characteristics but no "oxford" in URL
    print_section("CHECKING BOWERY & CASUAL SHIRTS FOR POTENTIAL OXFORDS")
    
    cur.execute('''
        SELECT product_code, product_name, subcategory, product_url, fit_options
        FROM jcrew_product_cache
        WHERE subcategory IN ('Bowery', 'Casual Shirts', 'Dress Shirts')
        AND LOWER(product_url) NOT LIKE '%oxford%'
        ORDER BY subcategory, product_code
        LIMIT 50
    ''')
    
    other_shirts = cur.fetchall()
    
    potential_oxfords = []
    for code, name, subcat, url, fits in other_shirts:
        # Check if name suggests it might be oxford
        name_lower = name.lower() if name else ""
        if any(term in name_lower for term in ['oxford', 'button-down', 'ocbd']):
            potential_oxfords.append((code, name, subcat, url, fits))
            print(f"🔍 {code}: {name[:50]}... [{subcat}]")
            if url:
                print(f"     URL: {url[:80]}...")
    
    # 3. Summary of findings
    print_section("ANALYSIS SUMMARY")
    
    print(f"\n📊 Oxford Products Found:")
    print(f"   • Correctly categorized as 'Oxford': {len(correctly_categorized)}")
    print(f"   • Need subcategory update to 'Oxford': {len(needs_update)}")
    print(f"   • Total Oxford products (by URL): {len(url_oxford_products)}")
    
    if needs_update:
        print(f"\n⚠️  Products to Update (subcategory → 'Oxford'):")
        for code, name, current_cat, fits in needs_update:
            print(f"   {code}: {name[:60]}...")
            print(f"      Current: '{current_cat}' → Should be: 'Oxford'")
            if fits:
                fit_list = ', '.join(fits) if isinstance(fits, list) else fits
                print(f"      Fits: {fit_list}")
    
    # 4. Generate SQL update statements
    print_section("SQL UPDATE STATEMENTS")
    
    if needs_update:
        print("-- Run these updates to fix Oxford categorization:")
        print("BEGIN;")
        for code, name, current_cat, fits in needs_update:
            print(f"""
UPDATE jcrew_product_cache
SET subcategory = 'Oxford',
    updated_at = NOW()
WHERE product_code = '{code}';
-- Was: {current_cat}, Name: {name[:50]}...""")
        print("\nCOMMIT;")
    
    # 5. Check for missing Giant-fit
    print_section("MISSING PRODUCTS FROM WEBSITE")
    
    print("\n❌ ME183: Giant-fit oxford shirt")
    print("   Status: NOT IN DATABASE")
    print("   URL: https://www.jcrew.com/p/mens/categories/clothing/shirts/broken-in-oxford/giant-fit-oxford-shirt/ME183")
    print("   Fits: ['Giant']")
    
    print("\n-- SQL to add ME183:")
    print("""
INSERT INTO jcrew_product_cache (
    product_code, 
    product_name, 
    product_url,
    fit_options,
    category,
    subcategory,
    created_at
) VALUES (
    'ME183',
    'Giant-fit oxford shirt',
    'https://www.jcrew.com/p/mens/categories/clothing/shirts/broken-in-oxford/giant-fit-oxford-shirt/ME183',
    ARRAY['Giant'],
    'Casual Shirts',
    'Oxford',
    NOW()
) ON CONFLICT (product_code) DO NOTHING;""")
    
    # 6. Final count after proposed changes
    print_section("PROJECTED TOTALS AFTER UPDATES")
    
    total_after_updates = len(correctly_categorized) + len(needs_update) + 1  # +1 for ME183
    
    print(f"\n📈 After all updates:")
    print(f"   • Total Oxford products: {total_after_updates}")
    print(f"   • J.Crew website shows: 34 (includes color duplicates)")
    print(f"   • Gap to investigate: {34 - total_after_updates} items")
    print(f"\n💡 Note: Website count includes color variants. Each product")
    print(f"   with multiple colors is counted separately on the website.")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
