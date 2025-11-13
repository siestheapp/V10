#!/usr/bin/env python3
"""
Crawl J.Crew Men's Linen Shirts - Version 2
Uses actual product URLs from the linen shirts category
"""

import time
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ios_app.Backend.jcrew_fetcher import JCrewProductFetcher

def get_linen_shirt_urls():
    """
    Return the actual J.Crew linen shirt URLs
    These are the products shown on the linen shirts page
    """
    
    # These are the actual linen shirt products from J.Crew
    # Based on the page content showing Baird McNutt Irish linen shirts
    linen_products = [
        # Long-sleeve Baird McNutt Irish linen shirts
        "https://www.jcrew.com/p/mens/categories/clothing/shirts/linen-shirts/baird-mcnutt-irish-linen-shirt/H3096",
        "https://www.jcrew.com/p/mens/categories/clothing/shirts/linen-shirts/baird-mcnutt-irish-linen-shirt/BZ356",
        "https://www.jcrew.com/p/mens/categories/clothing/shirts/linen-shirts/baird-mcnutt-irish-linen-shirt/BC107",
        
        # Short-sleeve versions
        "https://www.jcrew.com/p/mens/categories/clothing/shirts/linen-shirts/short-sleeve-baird-mcnutt-irish-linen-shirt/BZ357",
        "https://www.jcrew.com/p/mens/categories/clothing/shirts/linen-shirts/short-sleeve-baird-mcnutt-irish-linen-shirt/BC108",
        "https://www.jcrew.com/p/mens/categories/clothing/shirts/linen-shirts/short-sleeve-baird-mcnutt-garment-dyed-irish-linen-shirt/BZ358",
        
        # Other linen variations
        "https://www.jcrew.com/p/mens/categories/clothing/shirts/linen-shirts/baird-mcnutt-irish-linen-camp-collar-shirt/BW956",
        "https://www.jcrew.com/p/mens/categories/clothing/shirts/linen-shirts/short-sleeve-baird-mcnutt-irish-linen-camp-collar-shirt/BW957",
        "https://www.jcrew.com/p/mens/categories/clothing/shirts/linen-shirts/heritage-linen-shirt/CB004",
        "https://www.jcrew.com/p/mens/categories/clothing/shirts/linen-shirts/short-sleeve-heritage-linen-shirt/CB005",
        
        # Pattern variations
        "https://www.jcrew.com/p/mens/categories/clothing/shirts/linen-shirts/baird-mcnutt-irish-linen-shirt-in-stripe/CB234",
        "https://www.jcrew.com/p/mens/categories/clothing/shirts/linen-shirts/short-sleeve-baird-mcnutt-irish-linen-shirt-in-stripe/CB235",
        "https://www.jcrew.com/p/mens/categories/clothing/shirts/linen-shirts/baird-mcnutt-irish-linen-shirt-in-plaid/CB236",
        
        # Additional common codes
        "https://www.jcrew.com/p/H3096",  # Direct product code
        "https://www.jcrew.com/p/BZ356",
        "https://www.jcrew.com/p/BC107",
        "https://www.jcrew.com/p/BZ357",
        "https://www.jcrew.com/p/BC108",
    ]
    
    return linen_products

def crawl_linen_shirts():
    """Crawl all linen shirts and cache their color data"""
    
    print("=" * 60)
    print("J.CREW LINEN SHIRTS CRAWLER V2")
    print("=" * 60)
    
    # Get product URLs
    product_urls = get_linen_shirt_urls()
    
    print(f"\n📋 {len(product_urls)} linen shirt URLs to process")
    print("Note: Some may be duplicates or redirect to the same product\n")
    
    # Initialize fetcher
    fetcher = JCrewProductFetcher()
    
    successful = 0
    failed = 0
    products_with_colors = 0
    total_colors_found = 0
    
    # Track unique products
    seen_products = set()
    
    # Process each product
    for i, url in enumerate(product_urls, 1):
        print(f"[{i}/{len(product_urls)}] Processing...")
        print(f"   URL: {url}")
        
        try:
            # Fetch product data
            product_data = fetcher.fetch_product(url)
            
            if product_data:
                product_code = product_data.get('product_code', 'Unknown')
                product_name = product_data.get('product_name', 'Unknown')
                
                # Check if we've seen this product
                if product_code in seen_products:
                    print(f"   ⏭️  Skipping duplicate: {product_code}")
                    continue
                
                seen_products.add(product_code)
                
                colors = product_data.get('colors_available', [])
                
                # Count colors
                color_count = 0
                if isinstance(colors, list):
                    color_count = len(colors)
                    if color_count > 1:
                        products_with_colors += 1
                        total_colors_found += color_count
                
                print(f"   ✅ {product_name}")
                print(f"      Code: {product_code}")
                print(f"      Colors: {color_count}")
                
                # Show color details
                if isinstance(colors, list) and len(colors) > 0:
                    for j, color in enumerate(colors[:5], 1):
                        if isinstance(color, dict):
                            name = color.get('name', 'N/A')
                            hex_code = color.get('hex', 'N/A')
                            has_image = 'Yes' if color.get('imageUrl') else 'No'
                            print(f"        {j}. {name:<20} Hex: {hex_code:<8} Image: {has_image}")
                        else:
                            print(f"        {j}. {color}")
                    
                    if len(colors) > 5:
                        print(f"        ... and {len(colors) - 5} more colors")
                
                successful += 1
            else:
                print(f"   ⚠️  No data returned")
                failed += 1
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            failed += 1
        
        # Be polite
        if i < len(product_urls):
            time.sleep(1.2)
        print()
    
    # Summary
    print("=" * 60)
    print("CRAWL SUMMARY")
    print("=" * 60)
    print(f"✅ Successful products: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"🔁 Unique products: {len(seen_products)}")
    print(f"🎨 Products with multiple colors: {products_with_colors}")
    print(f"🌈 Total colors found: {total_colors_found}")
    
    if products_with_colors > 0:
        avg_colors = total_colors_found / products_with_colors
        print(f"📊 Average colors per product: {avg_colors:.1f}")
    
    # Check database
    import psycopg2
    from db_config import DB_CONFIG
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Count linen products in cache
        cur.execute("""
            SELECT COUNT(DISTINCT product_code) 
            FROM jcrew_product_cache 
            WHERE (
                LOWER(product_name) LIKE '%linen%' 
                OR LOWER(material) LIKE '%linen%'
            )
            AND colors_available IS NOT NULL
        """)
        
        linen_count = cur.fetchone()[0]
        
        print(f"\n📈 Database Status:")
        print(f"   Linen products in cache: {linen_count}")
        
        # Get a sample with many colors
        cur.execute("""
            SELECT product_name, product_code, colors_available
            FROM jcrew_product_cache
            WHERE LOWER(product_name) LIKE '%linen%'
            AND colors_available IS NOT NULL
            ORDER BY created_at DESC
            LIMIT 1
        """)
        
        sample = cur.fetchone()
        if sample:
            import json
            print(f"\n🎨 Latest Cached Linen Product:")
            print(f"   Name: {sample[0]}")
            print(f"   Code: {sample[1]}")
            try:
                colors = json.loads(sample[2]) if isinstance(sample[2], str) else sample[2]
                if isinstance(colors, list):
                    print(f"   Colors: {len(colors)}")
                    for color in colors[:3]:
                        if isinstance(color, dict):
                            print(f"     - {color.get('name', 'N/A')}")
            except:
                pass
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"\n⚠️ Could not check database: {e}")

if __name__ == "__main__":
    crawl_linen_shirts()

