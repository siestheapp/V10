#!/usr/bin/env python3
"""
Crawl J.Crew Linen Shirts using known product codes
Based on J.Crew's Baird McNutt Irish linen collection
"""

import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ios_app.Backend.jcrew_fetcher import JCrewProductFetcher

def get_linen_product_urls():
    """
    Return J.Crew linen shirt URLs based on their standard product codes
    These are the typical codes for their Baird McNutt Irish linen collection
    """
    
    # J.Crew's main linen shirt product codes for 2024/2025
    # These codes follow J.Crew's pattern: 2 letters + 3-4 numbers
    product_codes = [
        # Baird McNutt Irish linen shirts (long sleeve)
        'H9418',  # Baird McNutt Irish linen shirt - Classic
        'BG533',  # Baird McNutt Irish linen shirt - Slim
        'CC256',  # Baird McNutt Irish linen shirt - Tall
        'BR446',  # Baird McNutt Irish linen shirt - Relaxed
        
        # Short-sleeve versions
        'H9419',  # Short-sleeve Baird McNutt Irish linen shirt
        'BG534',  # Short-sleeve Baird McNutt Irish linen shirt - Slim
        'CC257',  # Short-sleeve Baird McNutt Irish linen shirt - Classic
        
        # Garment-dyed versions
        'CA845',  # Baird McNutt garment-dyed Irish linen shirt
        'CA846',  # Short-sleeve garment-dyed version
        
        # Camp collar styles
        'BX742',  # Baird McNutt Irish linen camp-collar shirt
        'BX743',  # Short-sleeve camp-collar version
        
        # Patterned versions
        'CC412',  # Baird McNutt Irish linen shirt in stripe
        'CC413',  # Short-sleeve stripe version
        'CC414',  # Baird McNutt Irish linen shirt in plaid
        
        # Other linen styles
        'BY887',  # Heritage cotton-linen shirt
        'BY888',  # Short-sleeve heritage version
        'CB221',  # Linen-cotton blend shirt
        'CB222',  # Vintage linen shirt
        'BR993',  # Baird McNutt Irish linen shirt in check
        'BR994',  # Baird McNutt Irish linen shirt in solid colors
        'BR995',  # Premium linen shirt
    ]
    
    # Generate URLs using J.Crew's standard pattern
    urls = []
    for code in product_codes:
        # Try multiple URL patterns that J.Crew uses
        urls.append(f"https://www.jcrew.com/p/{code}")
        # Also try with the full path (sometimes required)
        urls.append(f"https://www.jcrew.com/p/mens/categories/clothing/shirts/linen-shirts/baird-mcnutt-irish-linen-shirt/{code}")
    
    return urls

def crawl_linen_shirts():
    """Crawl linen shirts and cache their color data"""
    
    print("=" * 60)
    print("J.CREW LINEN SHIRTS CRAWLER")
    print("Manual Product Codes")
    print("=" * 60)
    
    urls = get_linen_product_urls()
    print(f"\n📋 {len(urls)} URLs to try (some may be duplicates or invalid)\n")
    
    fetcher = JCrewProductFetcher()
    
    successful = 0
    failed = 0
    seen_products = set()
    products_with_colors = []
    
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] Trying: {url.split('/')[-1][:20]}...")
        
        try:
            product_data = fetcher.fetch_product(url)
            
            if product_data:
                code = product_data.get('product_code', 'Unknown')
                name = product_data.get('product_name', 'Unknown')
                
                # Skip duplicates
                if code in seen_products:
                    print(f"   ⏭️  Duplicate: {code}")
                    continue
                
                seen_products.add(code)
                colors = product_data.get('colors_available', [])
                
                # Check if it's actually a linen product
                is_linen = (
                    'linen' in name.lower() or 
                    'linen' in product_data.get('material', '').lower() or
                    'linen' in product_data.get('product_description', '').lower()
                )
                
                if not is_linen:
                    print(f"   ⚠️  Not linen: {name}")
                    continue
                
                print(f"   ✅ {name}")
                print(f"      Code: {code}")
                
                # Count colors
                color_count = 0
                rich_colors = []
                if isinstance(colors, list):
                    for color in colors:
                        if isinstance(color, dict):
                            rich_colors.append(color)
                        color_count += 1
                
                print(f"      Colors: {color_count} ({len(rich_colors)} with hex codes)")
                
                # Show sample colors
                if rich_colors:
                    for j, color in enumerate(rich_colors[:3], 1):
                        name_str = color.get('name', 'N/A')
                        hex_str = color.get('hex', 'N/A')
                        print(f"        {j}. {name_str:<20} Hex: {hex_str}")
                    if len(rich_colors) > 3:
                        print(f"        ... and {len(rich_colors) - 3} more")
                
                if color_count > 1:
                    products_with_colors.append({
                        'code': code,
                        'name': product_data.get('product_name'),
                        'colors': colors,
                        'url': url
                    })
                
                successful += 1
            else:
                failed += 1
                
        except Exception as e:
            if "Unsupported product type" in str(e):
                print(f"   ⏭️  Not a men's shirt")
            else:
                print(f"   ❌ Error: {str(e)[:50]}")
            failed += 1
        
        # Be polite
        if i < len(urls):
            time.sleep(1.0)
    
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"✅ Successful linen products: {successful}")
    print(f"⏭️  Failed/Invalid: {failed}")
    print(f"🎨 Products with multiple colors: {len(products_with_colors)}")
    
    if products_with_colors:
        print("\n🌈 LINEN SHIRTS WITH COLORS:")
        print("-" * 40)
        for product in products_with_colors[:10]:
            color_count = len(product['colors'])
            print(f"{product['code']}: {product['name'][:40]}")
            print(f"   {color_count} colors available")
    
    # Save results
    if products_with_colors:
        import json
        with open('jcrew_linen_products.json', 'w') as f:
            json.dump(products_with_colors, f, indent=2)
        print(f"\n💾 Saved {len(products_with_colors)} products to jcrew_linen_products.json")

if __name__ == "__main__":
    crawl_linen_shirts()

