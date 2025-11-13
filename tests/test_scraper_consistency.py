#!/usr/bin/env python3
"""Test scraper consistency by comparing DB data with fresh scrape"""

import psycopg2
import json
from datetime import datetime
import sys
import os

# Add paths for imports
sys.path.append('/Users/seandavey/projects/V10')
sys.path.append('/Users/seandavey/projects/V10/scripts')

from db_config import DB_CONFIG

def get_random_products():
    """Get 5 random J.Crew products from the database"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    print("=" * 80)
    print("TESTING J.CREW SCRAPER CONSISTENCY")
    print("=" * 80)
    print("\n📊 Selecting 5 random products from jcrew_product_cache...\n")
    
    # Get 5 random products that have URLs (needed for scraping)
    cur.execute("""
        SELECT 
            product_code,
            product_name,
            product_url,
            fit_options,
            colors_available,
            sizes_available,
            updated_at
        FROM jcrew_product_cache
        WHERE product_url IS NOT NULL
        ORDER BY RANDOM()
        LIMIT 5
    """)
    
    products = cur.fetchall()
    
    print("🎲 RANDOMLY SELECTED PRODUCTS:\n")
    print("-" * 80)
    
    selected_products = []
    
    for idx, (code, name, url, fits, colors, sizes, updated) in enumerate(products, 1):
        print(f"\n{idx}. Product Code: {code}")
        print(f"   Name: {name[:60] if name else '[No name]'}...")
        print(f"   URL: {url[:80] if url else '[No URL]'}...")
        print(f"   Last Updated: {updated}")
        print(f"\n   📐 CURRENT FIT OPTIONS IN DB:")
        if fits and len(fits) > 0:
            print(f"      {fits}")
        else:
            print(f"      None (single fit or no data)")
        
        print(f"\n   🎨 CURRENT COLORS IN DB:")
        if colors and len(colors) > 0:
            print(f"      Count: {len(colors)} colors")
            # Show first 5 colors as sample
            for color in colors[:5]:
                print(f"      - {color}")
            if len(colors) > 5:
                print(f"      ... and {len(colors) - 5} more")
        else:
            print(f"      None stored")
        
        print(f"\n   📏 CURRENT SIZES IN DB:")
        if sizes and len(sizes) > 0:
            print(f"      {sizes}")
        else:
            print(f"      None stored")
        
        print("-" * 80)
        
        selected_products.append({
            'product_code': code,
            'product_name': name,
            'product_url': url,
            'db_fits': fits,
            'db_colors': colors,
            'db_sizes': sizes
        })
    
    cur.close()
    conn.close()
    
    # Save to JSON for the scraper to use
    with open('test_products.json', 'w') as f:
        json.dump(selected_products, f, indent=2)
    
    print(f"\n✅ Saved {len(selected_products)} products to test_products.json")
    print("\n📝 Next step: Run the scraper on these products to compare results")
    print("\nRun this command to test the scraper:")
    print("python scripts/jcrew_fit_crawler.py --test-file test_products.json\n")
    
    return selected_products

if __name__ == "__main__":
    get_random_products()
