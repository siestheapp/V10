#!/usr/bin/env python3
"""
Fetch J.Crew Men's Dress Shirts
"""

import sys
import time
import psycopg2
from datetime import datetime

# Add project root to path
sys.path.append('/Users/seandavey/projects/V10')
from db_config import DB_CONFIG
from src.ios_app.Backend.jcrew_fetcher import JCrewProductFetcher

# Dress shirt product codes found
DRESS_SHIRT_CODES = ['BG659', 'BG663', 'BM199', 'CD173', 'CG334', 'MP573', 'MP759']

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
    print("J.CREW MEN'S DRESS SHIRTS - PRODUCT FETCHER")
    print("="*60)
    print(f"Target: Fetch {len(DRESS_SHIRT_CODES)} dress shirt products")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Check what's already in database
    existing_before = check_existing_products()
    print(f"\n📊 Products in database before: {len(existing_before)}")
    
    # Filter to only missing products
    products_to_fetch = [p for p in DRESS_SHIRT_CODES if p not in existing_before]
    print(f"📋 Products to fetch: {len(products_to_fetch)}")
    
    if not products_to_fetch:
        print("✅ All products already in database!")
        return
    
    # Initialize fetcher
    fetcher = JCrewProductFetcher()
    
    successful = []
    failed = []
    
    # Fetch each product
    for i, product_code in enumerate(products_to_fetch, 1):
        print(f"\n[{i}/{len(products_to_fetch)}] Fetching {product_code}...")
        
        # Try different URL patterns for dress shirts
        urls = [
            f"https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/{product_code}",
            f"https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/business-casual-shirts/{product_code}",
            f"https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/ludlow-premium-dress-shirts/{product_code}",
            f"https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/bowery-shirts/{product_code}",
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
        
        # Rate limiting
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

if __name__ == "__main__":
    main()

