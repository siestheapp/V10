#!/usr/bin/env python3
"""
Validate J.Crew linen products data accuracy
Checks fits, colors, and completeness
"""

import sys
import json
sys.path.append('/Users/seandavey/projects/V10')
import psycopg2
from db_config import DB_CONFIG

def validate_linen_products():
    """Validate linen products data"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    print("=" * 80)
    print("VALIDATING J.CREW LINEN PRODUCTS DATA")
    print("=" * 80)
    
    # Load scraped data
    with open('jcrew_linen_test_20250916_135758.json', 'r') as f:
        scraped_data = json.load(f)
    
    scraped_products = {p['product_code']: p for p in scraped_data['all_products']}
    
    # Get database data for these products
    product_codes = list(scraped_products.keys())
    placeholders = ','.join(['%s'] * len(product_codes))
    
    cur.execute(f"""
        SELECT product_code, product_name, fit_options, colors_available, product_url
        FROM jcrew_product_cache
        WHERE product_code IN ({placeholders})
        ORDER BY product_code
    """, product_codes)
    
    db_products = {row[0]: row for row in cur.fetchall()}
    
    # Compare each product
    issues = []
    correct = []
    
    print("\n📋 PRODUCT-BY-PRODUCT VALIDATION:\n")
    
    for code, scraped in scraped_products.items():
        if code not in db_products:
            print(f"❌ {code}: Not in database!")
            issues.append(f"{code}: Missing from database")
            continue
        
        db_code, db_name, db_fits, db_colors, db_url = db_products[code]
        
        print(f"📍 {code}: {db_name[:50]}...")
        
        # Compare fit options
        scraped_fits = set(scraped['fit_options']) if scraped['fit_options'] else set()
        db_fits_set = set(db_fits) if db_fits else set()
        
        if scraped_fits and db_fits_set:
            # Check if database has MORE fits (which is good)
            if db_fits_set >= scraped_fits:
                print(f"   ✅ Fits: DB has all scraped fits and possibly more")
                print(f"      DB: {sorted(db_fits_set)}")
                print(f"      Scraped: {sorted(scraped_fits)}")
            elif scraped_fits - db_fits_set:
                print(f"   ⚠️ Fits: Scraped found fits not in DB")
                print(f"      Missing in DB: {scraped_fits - db_fits_set}")
                issues.append(f"{code}: Missing fits {scraped_fits - db_fits_set}")
            else:
                print(f"   ✅ Fits match")
        elif db_fits_set and not scraped_fits:
            print(f"   ✅ Fits: DB has {sorted(db_fits_set)}, scraper didn't extract from listing")
        elif scraped_fits and not db_fits_set:
            print(f"   ⚠️ Fits: DB missing fits that scraper found: {sorted(scraped_fits)}")
            issues.append(f"{code}: DB missing fits")
        else:
            print(f"   ℹ️ Fits: None in both (single fit product)")
        
        # Check colors
        if db_colors:
            print(f"   ✅ Colors: {len(db_colors)} in DB")
        else:
            print(f"   ⚠️ Colors: None in DB")
        
        # Check URL
        if db_url:
            print(f"   ✅ URL: Present")
        else:
            print(f"   ⚠️ URL: Missing")
            issues.append(f"{code}: Missing URL")
        
        print()
    
    # Check for other linen products not in scrape
    print("\n🔍 CHECKING FOR OTHER LINEN PRODUCTS IN DB:\n")
    
    cur.execute("""
        SELECT product_code, product_name, fit_options, colors_available
        FROM jcrew_product_cache
        WHERE (LOWER(product_name) LIKE '%linen%' 
               OR LOWER(subcategory) LIKE '%linen%')
        AND product_code NOT IN %s
        ORDER BY product_code
    """, (tuple(product_codes),))
    
    other_linen = cur.fetchall()
    if other_linen:
        print(f"Found {len(other_linen)} other linen products not in scrape:")
        for code, name, fits, colors in other_linen:
            print(f"   {code}: {name[:50]}...")
            if fits:
                print(f"      Fits: {fits}")
    else:
        print("No other linen products found in database")
    
    # Summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    
    print(f"\n📊 Results:")
    print(f"   Products validated: {len(scraped_products)}")
    print(f"   Issues found: {len(issues)}")
    
    if issues:
        print(f"\n⚠️ Issues to investigate:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print(f"\n✅ All products validated successfully!")
    
    # Data quality metrics
    products_with_fits = sum(1 for _, _, fits, _, _ in db_products.values() if fits)
    products_with_colors = sum(1 for _, _, _, colors, _ in db_products.values() if colors)
    
    print(f"\n📈 Data Quality Metrics:")
    print(f"   Products with fit options: {products_with_fits}/{len(db_products)} ({products_with_fits*100//len(db_products)}%)")
    print(f"   Products with colors: {products_with_colors}/{len(db_products)} ({products_with_colors*100//len(db_products)}%)")
    
    # Check if we need to handle color variants
    print(f"\n🎨 COLOR VARIANT ANALYSIS:")
    
    # Look at the scraped URLs for colorProductCode parameters
    import re
    color_codes_found = set()
    for product in scraped_data['all_products']:
        if product['product_url']:
            match = re.search(r'colorProductCode=([A-Z0-9]+)', product['product_url'])
            if match:
                color_codes_found.add(match.group(1))
    
    if color_codes_found:
        print(f"   Found {len(color_codes_found)} unique color codes in URLs:")
        for cc in sorted(color_codes_found)[:10]:
            print(f"      - {cc}")
        
        print(f"\n   💡 Recommendation:")
        print(f"   These color codes could be used to create variant products")
        print(f"   Example: MP123-BE554 for white variant")
        print(f"   This would match J.Crew's system and avoid duplicates")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    validate_linen_products()
