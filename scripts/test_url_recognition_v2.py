#!/usr/bin/env python3
"""
Test script to simulate what the V10 app would show when various J.Crew URLs are entered.
V2: Shows ALL available colors and options, not just the one in the URL.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import re
import json
from urllib.parse import urlparse, parse_qs

def extract_product_code_from_url(url):
    """Extract just the product code from J.Crew URL"""
    info = {
        'url': url,
        'product_code': None,
        'url_color': None,  # Just for reference, not for filtering
        'url_fit': None,     # Just for reference, not for filtering
    }
    
    # Extract product code from URL path
    if '/p/' in url or '/m/' in url:
        match = re.search(r'/([A-Z0-9]+)\?', url)
        if match:
            info['product_code'] = match.group(1)
        else:
            # Try without query params
            parts = url.split('/')
            for part in parts:
                if part and part[0].isupper() and len(part) <= 6:
                    info['product_code'] = part
                    break
    
    # Note what was in the URL (but we won't filter by this)
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    
    if 'fit' in params:
        info['url_fit'] = params['fit'][0]
    
    if 'color_name' in params:
        info['url_color'] = params['color_name'][0].replace('-', ' ').title()
    
    return info

def get_product_from_database(cur, product_code):
    """Get full product details from database"""
    cur.execute('''
        SELECT 
            product_code,
            product_name,
            category,
            subcategory,
            brand_name,
            colors_available,
            fit_options,
            sizes_available,
            price,
            garment_type,
            standard_category,
            product_url
        FROM jcrew_product_cache
        WHERE product_code = %s
    ''', (product_code,))
    
    return cur.fetchone()

def format_color_display(colors):
    """Format colors for display"""
    if not colors:
        return []
    
    formatted = []
    for color in colors:
        # Handle both string and dict formats
        if isinstance(color, str):
            # Try to parse as JSON first
            try:
                color_dict = json.loads(color)
                formatted.append(color_dict.get('name', color))
            except:
                formatted.append(color)
        elif isinstance(color, dict):
            formatted.append(color.get('name', str(color)))
        else:
            formatted.append(str(color))
    
    return formatted

def simulate_app_display(url_info, db_product):
    """Simulate what the app would actually display to the user"""
    
    if not url_info['product_code']:
        return {
            'status': 'ERROR',
            'message': '❌ Invalid URL - Could not extract product code',
            'display': None
        }
    
    if not db_product:
        return {
            'status': 'NOT_FOUND',
            'message': f'❌ Product {url_info["product_code"]} not in database - Need to update product cache',
            'display': None
        }
    
    # Product found - show ALL available options
    colors = format_color_display(db_product['colors_available'])
    
    display = {
        'product_code': db_product['product_code'],
        'product_name': db_product['product_name'],
        'category': f"{db_product['category']} > {db_product['subcategory']}",
        'price': f"${db_product['price']:.2f}" if db_product['price'] else 'Price not available',
        'garment_type': db_product['garment_type'] or 'Not classified',
        
        # ALL available options - this is what the app shows
        'all_colors': colors,
        'all_fits': db_product['fit_options'] or ['Standard'],
        'all_sizes': db_product['sizes_available'] or [],
        
        # Note what was in the URL (for pre-selection)
        'url_had_color': url_info['url_color'],
        'url_had_fit': url_info['url_fit']
    }
    
    return {
        'status': 'SUCCESS',
        'message': '✅ Product found in database!',
        'display': display
    }

def main():
    # Test URLs
    test_urls = [
        "https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/business-casual-shirts/bowery-performance-stretch-dress-shirt-with-spread-collar/BX291?display=standard&fit=Classic&color_name=jim-stripe-blue-white&colorProductCode=BX291",
        "https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/ludlow-premium-dress-shirts/ludlow-pleated-bib-tuxedo-shirt/BN777?display=standard&fit=Classic&color_name=white&colorProductCode=BN777",
        "https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/ludlow-premium-dress-shirts/ludlow-premium-fine-cotton-dress-shirt/BM493?display=standard&fit=Classic&color_name=white&colorProductCode=BM493",
        "https://www.jcrew.com/m/mens/categories/clothing/shirts/linen/baird-mcnutt-irish-linen-shirt/MP123?display=standard&fit=Classic&color_name=amalfi-blue-linen-yd&colorProductCode=BE554",
        "https://www.jcrew.com/p/mens/categories/clothing/shirts/secret-wash/secret-wash-cotton-poplin-shirt-with-point-collar/CF783?display=standard&fit=Classic&color_name=jimmy-brown-multi&colorProductCode=CF783"
    ]
    
    # Connect to database
    conn = psycopg2.connect(
        database='postgres',
        user='fs_core_rw',
        password='CHANGE_ME',
        host='aws-1-us-east-1.pooler.supabase.com',
        port='5432',
        cursor_factory=RealDictCursor,
        connect_timeout=10
    )
    cur = conn.cursor()
    
    print("📱 V10 App Display Simulation")
    print("=" * 80)
    print("Showing what the app would display when user enters each URL")
    print("Note: App shows ALL available options, not just what's in the URL\n")
    
    results = []
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n{'='*80}")
        print(f"📱 TEST #{i}")
        print(f"URL entered: {url[:70]}...")
        
        # Extract product code
        url_info = extract_product_code_from_url(url)
        print(f"\n🔍 Extracted product code: {url_info['product_code']}")
        
        # Get from database
        db_product = None
        if url_info['product_code']:
            db_product = get_product_from_database(cur, url_info['product_code'])
        
        # Simulate display
        result = simulate_app_display(url_info, db_product)
        results.append(result)
        
        print(f"{result['message']}")
        
        if result['status'] == 'SUCCESS' and result['display']:
            display = result['display']
            
            print(f"\n📦 APP WOULD DISPLAY:")
            print(f"   Product: {display['product_name']}")
            print(f"   Category: {display['category']}")
            print(f"   Type: {display['garment_type']}")
            print(f"   Price: {display['price']}")
            
            print(f"\n   🎨 COLOR OPTIONS ({len(display['all_colors'])} available):")
            for j, color in enumerate(display['all_colors'][:5], 1):
                pre_selected = "← (from URL)" if display['url_had_color'] and display['url_had_color'].lower() in color.lower() else ""
                print(f"      {j}. {color} {pre_selected}")
            if len(display['all_colors']) > 5:
                print(f"      ... and {len(display['all_colors']) - 5} more colors")
            
            print(f"\n   👔 FIT OPTIONS ({len(display['all_fits'])} available):")
            for fit in display['all_fits']:
                pre_selected = "← (from URL)" if display['url_had_fit'] and display['url_had_fit'].lower() == fit.lower() else ""
                print(f"      • {fit} {pre_selected}")
            
            print(f"\n   📏 SIZE OPTIONS: {len(display['all_sizes'])} sizes available")
            if display['all_sizes']:
                print(f"      {', '.join(display['all_sizes'][:5])}", end="")
                if len(display['all_sizes']) > 5:
                    print(f", ... and {len(display['all_sizes']) - 5} more")
                else:
                    print()
    
    # Summary
    print(f"\n{'='*80}")
    print("📊 SUMMARY")
    print("=" * 80)
    
    success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
    not_found_count = sum(1 for r in results if r['status'] == 'NOT_FOUND')
    error_count = sum(1 for r in results if r['status'] == 'ERROR')
    
    print(f"✅ Products Found: {success_count}/{len(test_urls)}")
    print(f"❌ Not in Database: {not_found_count}/{len(test_urls)}")
    print(f"⚠️  Invalid URLs: {error_count}/{len(test_urls)}")
    
    if not_found_count > 0:
        print("\n🔴 Missing Products (need to add to database):")
        for r in results:
            if r['status'] == 'NOT_FOUND':
                # Extract product code from message
                import re
                match = re.search(r'Product (\w+)', r['message'])
                if match:
                    print(f"   - {match.group(1)}")
    
    # Check data completeness
    print("\n📊 Data Completeness for Found Products:")
    for r in results:
        if r['status'] == 'SUCCESS' and r['display']:
            d = r['display']
            print(f"\n   {d['product_code']}: {d['product_name'][:40]}...")
            print(f"      Colors: {len(d['all_colors'])} options")
            print(f"      Fits: {len(d['all_fits'])} options")
            print(f"      Sizes: {len(d['all_sizes'])} options")
    
    conn.close()
    
    print("\n💡 Note: The app should display ALL available options for each product,")
    print("   allowing users to select any color/fit/size combination, not just")
    print("   what was in the original URL they pasted.")

if __name__ == "__main__":
    main()




