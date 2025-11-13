#!/usr/bin/env python3
"""
Crawl J.Crew Men's Linen Shirts
Specifically targets the 21 linen shirts to get all color data
"""

import requests
from bs4 import BeautifulSoup
import time
import re
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ios_app.Backend.jcrew_fetcher import JCrewProductFetcher

def extract_linen_shirt_urls():
    """Extract product URLs from the linen shirts page"""
    
    url = "https://www.jcrew.com/plp/mens/categories/clothing/shirts?sub-categories=men-shirts-linen"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }
    
    print(f"🔍 Fetching linen shirts page...")
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find product links - J.Crew uses specific patterns
    product_urls = set()
    
    # Look for product links in the listing
    # Common patterns: /p/mens/categories/clothing/shirts/...
    for link in soup.find_all('a', href=True):
        href = link['href']
        # Match J.Crew product URLs
        if '/p/mens/' in href and ('/shirts/' in href or '/shirt/' in href):
            # Make absolute URL
            if href.startswith('/'):
                href = f"https://www.jcrew.com{href}"
            # Remove query parameters for base URL
            base_url = href.split('?')[0]
            # Only add if it looks like a product URL (has product code)
            if re.search(r'/[A-Z0-9]{4,6}(?:\?|$|/)', base_url):
                product_urls.add(base_url)
    
    # Also look for product codes in data attributes
    for element in soup.find_all(attrs={'data-product-id': True}):
        product_id = element.get('data-product-id')
        if product_id:
            # Try to construct URL from product ID
            # This is a fallback if direct links aren't found
            pass
    
    return list(product_urls)

def crawl_linen_shirts():
    """Crawl all linen shirts and cache their data"""
    
    print("=" * 60)
    print("J.CREW LINEN SHIRTS CRAWLER")
    print("=" * 60)
    
    # Extract product URLs
    product_urls = extract_linen_shirt_urls()
    
    if not product_urls:
        print("❌ No product URLs found. The page structure may have changed.")
        print("\n🔧 Fallback: Using known linen shirt product codes...")
        
        # Fallback: Known linen shirt product codes from the page
        known_codes = [
            "BE996",  # Baird McNutt Irish linen shirt (long sleeve)
            "BH290",  # Short-sleeve Baird McNutt Irish linen shirt
            "BW307",  # Baird McNutt garment-dyed Irish linen shirt
            "BV846",  # Short-sleeve garment-dyed version
        ]
        
        product_urls = [
            f"https://www.jcrew.com/p/mens/categories/clothing/shirts/linen/{code}"
            for code in known_codes
        ]
    
    print(f"\n📋 Found {len(product_urls)} product URLs to crawl")
    
    # Initialize fetcher
    fetcher = JCrewProductFetcher()
    
    successful = 0
    failed = 0
    
    # Process each product
    for i, url in enumerate(product_urls, 1):
        print(f"\n[{i}/{len(product_urls)}] Processing: {url}")
        
        try:
            # Fetch product data (this will cache it automatically)
            product_data = fetcher.fetch_product(url)
            
            if product_data:
                colors = product_data.get('colors_available', [])
                color_count = len(colors) if colors else 0
                
                print(f"✅ Success: {product_data.get('product_name', 'Unknown')}")
                print(f"   Product Code: {product_data.get('product_code', 'N/A')}")
                print(f"   Colors Found: {color_count}")
                
                # Show first 3 colors as sample
                if isinstance(colors, list) and len(colors) > 0:
                    for j, color in enumerate(colors[:3], 1):
                        if isinstance(color, dict):
                            name = color.get('name', 'N/A')
                            hex_code = color.get('hex', 'N/A')
                            print(f"     {j}. {name} ({hex_code})")
                        else:
                            print(f"     {j}. {color}")
                    
                    if len(colors) > 3:
                        print(f"     ... and {len(colors) - 3} more colors")
                
                successful += 1
            else:
                print(f"⚠️  No data returned for {url}")
                failed += 1
                
        except Exception as e:
            print(f"❌ Error: {e}")
            failed += 1
        
        # Be polite - wait between requests
        if i < len(product_urls):
            print(f"⏳ Waiting 1.5 seconds...")
            time.sleep(1.5)
    
    # Summary
    print("\n" + "=" * 60)
    print("CRAWL COMPLETE")
    print("=" * 60)
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {len(product_urls)}")
    
    # Check cache status
    import psycopg2
    from db_config import DB_CONFIG
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Get count of products with rich color data
        cur.execute("""
            SELECT COUNT(*) 
            FROM jcrew_product_cache 
            WHERE category = 'Shirts'
            AND colors_available IS NOT NULL
            AND colors_available::text LIKE '%"hex"%'
        """)
        
        rich_colors = cur.fetchone()[0]
        
        print(f"\n📈 Cache Status:")
        print(f"   Shirts with rich color data: {rich_colors}")
        
        # Show a sample of cached colors
        cur.execute("""
            SELECT product_name, colors_available
            FROM jcrew_product_cache
            WHERE category = 'Shirts'
            AND colors_available IS NOT NULL
            AND jsonb_array_length(colors_available::jsonb) > 5
            LIMIT 1
        """)
        
        sample = cur.fetchone()
        if sample:
            import json
            print(f"\n🎨 Sample Product: {sample[0]}")
            colors = json.loads(sample[1]) if isinstance(sample[1], str) else sample[1]
            if isinstance(colors, list):
                print(f"   Total colors: {len(colors)}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Could not check cache status: {e}")

if __name__ == "__main__":
    crawl_linen_shirts()

