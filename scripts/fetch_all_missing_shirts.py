#!/usr/bin/env python3
"""
Fetch all missing J.Crew Men's Casual Shirts
Uses JCrewProductFetcher which automatically caches to database
"""

import sys
import time
import psycopg2
from datetime import datetime

# Add project root to path
sys.path.append('/Users/seandavey/projects/V10')
from db_config import DB_CONFIG
from src.ios_app.Backend.jcrew_fetcher import JCrewProductFetcher

# Missing product codes from our analysis
MISSING_PRODUCTS = [
    'BE076', 'BE077', 'BE163', 'BE164', 'BE546', 'BE554', 'BE986', 'BE998', 
    'BE999', 'BJ705', 'BN126', 'BT549', 'BT743', 'BT744', 'BX291', 'BZ532', 
    'CC100', 'CC101', 'CJ508', 'CM237', 'CM390', 'CN406', 'ME053', 'ME183', 
    'MP235', 'MP600', 'MP653', 'MP712'
]

def check_existing_products():
    """Check which products are already in database"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT DISTINCT UPPER(product_code) 
        FROM jcrew_product_cache 
        WHERE product_code IS NOT NULL
    """)
    existing = {row[0] for row in cur.fetchall()}
    
    cur.close()
    conn.close()
    
    return existing

def main():
    print("="*60)
    print("J.CREW MEN'S CASUAL SHIRTS - PRODUCT FETCHER")
    print("="*60)
    print(f"Target: Fetch {len(MISSING_PRODUCTS)} missing products")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Check what's already in database
    existing_before = check_existing_products()
    print(f"\n📊 Products in database before: {len(existing_before)}")
    
    # Filter to only truly missing products
    products_to_fetch = [p for p in MISSING_PRODUCTS if p not in existing_before]
    print(f"📋 Products to fetch: {len(products_to_fetch)}")
    
    if not products_to_fetch:
        print("✅ All products already in database!")
        return
    
    # Initialize fetcher (it handles caching automatically)
    fetcher = JCrewProductFetcher()
    
    successful = []
    failed = []
    
    # Fetch each product
    for i, product_code in enumerate(products_to_fetch, 1):
        print(f"\n[{i}/{len(products_to_fetch)}] Fetching {product_code}...")
        
        # Try different URL patterns
        urls = [
            f"https://www.jcrew.com/p/mens/categories/clothing/shirts/{product_code}",
            f"https://www.jcrew.com/p/mens/categories/clothing/shirts/casual/{product_code}",
            f"https://www.jcrew.com/p/{product_code}",
        ]
        
        fetched = False
        for url in urls:
            try:
                print(f"  Trying: {url}")
                product_data = fetcher.fetch_product(url)
                
                if product_data and product_data.get('product_name'):
                    print(f"  ✅ Success: {product_data['product_name'][:50]}...")
                    print(f"     Colors: {len(product_data.get('colors_available', []))}")
                    print(f"     Fits: {len(product_data.get('fit_options', []))}")
                    successful.append(product_code)
                    fetched = True
                    break
                    
            except Exception as e:
                print(f"  ⚠️ Error: {e}")
                continue
        
        if not fetched:
            print(f"  ❌ Failed to fetch {product_code}")
            failed.append(product_code)
        
        # Rate limiting - be respectful
        time.sleep(2)
    
    # Check final state
    existing_after = check_existing_products()
    
    # Print summary
    print("\n" + "="*60)
    print("FETCH SUMMARY")
    print("="*60)
    print(f"Products in database before: {len(existing_before)}")
    print(f"Products in database after:  {len(existing_after)}")
    print(f"New products added:          {len(existing_after) - len(existing_before)}")
    print(f"Successfully fetched:        {len(successful)}")
    print(f"Failed to fetch:             {len(failed)}")
    
    if failed:
        print(f"\n❌ Failed product codes:")
        for code in failed:
            print(f"   {code}")
    
    # Get details of new products
    if len(existing_after) > len(existing_before):
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        new_codes = existing_after - existing_before
        cur.execute("""
            SELECT product_code, product_name, 
                   array_length(colors_available, 1) as colors,
                   array_length(fit_options, 1) as fits
            FROM jcrew_product_cache 
            WHERE UPPER(product_code) IN %s
        """, (tuple(new_codes),))
        
        print(f"\n✅ New products added:")
        for row in cur.fetchall():
            print(f"   {row[0]}: {row[1][:40]:40} - {row[2] or 0} colors, {row[3] or 0} fits")
        
        cur.close()
        conn.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Fetch missing J.Crew products')
    parser.add_argument('--test', action='store_true', help='Test with first 5 products only')
    
    args = parser.parse_args()
    
    if args.test:
        MISSING_PRODUCTS = MISSING_PRODUCTS[:5]
        print("🧪 TEST MODE - Processing first 5 products only\n")
    
    main()

