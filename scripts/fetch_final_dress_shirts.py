#!/usr/bin/env python3
"""
Fetch all remaining J.Crew Men's Dress Shirts
"""

import sys
import time
import psycopg2
from datetime import datetime

# Add project root to path
sys.path.append('/Users/seandavey/projects/V10')
from db_config import DB_CONFIG
from src.ios_app.Backend.jcrew_fetcher import JCrewProductFetcher

# Real dress shirt product codes to fetch
DRESS_SHIRT_CODES = [
    'BG665', 'BK0001', 'BL7729', 'BL7786', 'BM422', 'BM423', 'BW032', 'BW034',
    'CA351', 'CA352', 'CD174', 'CD175', 'CP683', 'CP684'
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
    
    # Count dress shirts specifically
    cur.execute("""
        SELECT COUNT(DISTINCT product_code)
        FROM jcrew_product_cache 
        WHERE LOWER(product_name) LIKE '%dress shirt%'
           OR LOWER(product_name) LIKE '%bowery%'
           OR LOWER(product_name) LIKE '%ludlow%'
           OR LOWER(product_name) LIKE '%thomas mason%'
           OR LOWER(product_name) LIKE '%portuguese cotton oxford dress%'
    """)
    dress_shirt_count = cur.fetchone()[0]
    
    cur.close()
    conn.close()
    
    return existing, dress_shirt_count

def main():
    print("="*60)
    print("J.CREW MEN'S DRESS SHIRTS - FINAL FETCH")
    print("="*60)
    print(f"Target: Complete dress shirts collection")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Check initial state
    existing_before, dress_shirts_before = check_existing_products()
    print(f"\n📊 Initial State:")
    print(f"  Total products in database: {len(existing_before)}")
    print(f"  Dress shirts in database:   {dress_shirts_before}")
    
    # Filter to only missing products
    products_to_fetch = [p for p in DRESS_SHIRT_CODES if p not in existing_before]
    print(f"\n📋 Products to fetch: {len(products_to_fetch)}")
    
    if not products_to_fetch:
        print("✅ All products already in database!")
        return
    
    print(f"  Codes: {' '.join(products_to_fetch)}")
    
    # Initialize fetcher
    fetcher = JCrewProductFetcher()
    
    successful = []
    failed = []
    
    # Fetch each product
    for i, product_code in enumerate(products_to_fetch, 1):
        print(f"\n[{i}/{len(products_to_fetch)}] Fetching {product_code}...")
        
        # Try different URL patterns for dress shirts
        url_patterns = [
            f"https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/{product_code}",
            f"https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/bowery-shirts/{product_code}",
            f"https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/ludlow-premium-dress-shirts/{product_code}",
            f"https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/business-casual-shirts/{product_code}",
            f"https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/thomas-mason-for-j-crew/{product_code}",
            f"https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/somelos/{product_code}",
            f"https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/tech/{product_code}",
            f"https://www.jcrew.com/p/{product_code}",
        ]
        
        fetched = False
        for url in url_patterns:
            try:
                print(f"  Trying: {url}")
                product_data = fetcher.fetch_product(url)
                
                if product_data and product_data.get('product_name'):
                    print(f"  ✅ Success: {product_data['product_name'][:60]}...")
                    
                    # Show details
                    colors = product_data.get('colors_available', [])
                    fits = product_data.get('fit_options', [])
                    print(f"     Colors: {len(colors)} - {', '.join(colors[:3])}{'...' if len(colors) > 3 else ''}")
                    print(f"     Fits: {len(fits)} - {', '.join(fits)}")
                    
                    successful.append(product_code)
                    fetched = True
                    break
                    
            except Exception as e:
                # Only print error if it's not a 503 (common for non-existent URLs)
                if '503' not in str(e):
                    print(f"  ⚠️ Error: {str(e)[:100]}")
                continue
        
        if not fetched:
            print(f"  ❌ Failed to fetch {product_code}")
            failed.append(product_code)
        
        # Rate limiting
        time.sleep(2)
    
    # Check final state
    existing_after, dress_shirts_after = check_existing_products()
    
    # Print summary
    print("\n" + "="*60)
    print("FETCH SUMMARY")
    print("="*60)
    print(f"📊 Database State:")
    print(f"  Total products before:      {len(existing_before)}")
    print(f"  Total products after:       {len(existing_after)}")
    print(f"  Dress shirts before:        {dress_shirts_before}")
    print(f"  Dress shirts after:         {dress_shirts_after}")
    
    print(f"\n📈 Results:")
    print(f"  New products added:         {len(existing_after) - len(existing_before)}")
    print(f"  New dress shirts added:     {dress_shirts_after - dress_shirts_before}")
    print(f"  Successfully fetched:       {len(successful)}")
    print(f"  Failed to fetch:            {len(failed)}")
    
    if successful:
        print(f"\n✅ Successfully fetched: {' '.join(successful)}")
    
    if failed:
        print(f"\n⚠️ Could not fetch: {' '.join(failed)}")
        print("  (These may be discontinued or color codes)")
    
    # Calculate coverage
    print(f"\n📊 DRESS SHIRT COVERAGE:")
    print(f"  Target from website: ~48 unique dress shirts")
    print(f"  Current in database: {dress_shirts_after}")
    coverage = (dress_shirts_after / 48 * 100)
    print(f"  Coverage: {coverage:.1f}%")
    
    if coverage >= 95:
        print("\n🎉 EXCELLENT! Dress shirts collection is essentially complete!")
    elif coverage >= 80:
        print("\n✅ GOOD! Most dress shirts are now in the database.")
    else:
        print(f"\n⚠️ Still missing approximately {48 - dress_shirts_after} dress shirts.")

if __name__ == "__main__":
    main()

