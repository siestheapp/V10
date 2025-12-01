#!/usr/bin/env python3
"""
Test script to simulate what the V10 app would show when various J.Crew URLs are entered.
Checks if products are in the database and what information would be displayed.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import re
from urllib.parse import urlparse, parse_qs
from datetime import datetime

def extract_product_info_from_url(url):
    """Extract product code, color, and fit from J.Crew URL"""
    info = {
        'url': url,
        'product_code': None,
        'requested_color': None,
        'requested_fit': None,
        'is_mobile': '/m/' in url
    }
    
    # Extract product code from URL path
    if '/p/' in url or '/m/' in url:
        # Pattern: /p/.../{product_code} or /m/.../{product_code}
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
    
    # Extract query parameters
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    
    if 'fit' in params:
        info['requested_fit'] = params['fit'][0]
    
    if 'color_name' in params:
        info['requested_color'] = params['color_name'][0].replace('-', ' ').title()
    
    if 'colorProductCode' in params:
        # Sometimes the color product code is different from main code
        info['color_product_code'] = params['colorProductCode'][0]
    
    return info

def check_product_in_database(cur, product_code):
    """Check if product exists in database and return its details"""
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

def simulate_app_response(url_info, db_product):
    """Simulate what the app would show"""
    response = {
        'url': url_info['url'],
        'product_code': url_info['product_code'],
        'status': 'NOT_FOUND',
        'message': None,
        'display_data': None
    }
    
    if not url_info['product_code']:
        response['status'] = 'INVALID_URL'
        response['message'] = '❌ Could not extract product code from URL'
        return response
    
    if not db_product:
        response['status'] = 'NOT_IN_DATABASE'
        response['message'] = f'❌ Product {url_info["product_code"]} not found in database'
        return response
    
    # Product found!
    response['status'] = 'FOUND'
    response['message'] = '✅ Product recognized!'
    
    # Check if requested color is available
    color_match = None
    if url_info['requested_color'] and db_product['colors_available']:
        # Try to find matching color
        requested_lower = url_info['requested_color'].lower()
        for color in db_product['colors_available']:
            if requested_lower in color.lower() or color.lower() in requested_lower:
                color_match = color
                break
    
    # Check if requested fit is available
    fit_match = None
    if url_info['requested_fit'] and db_product['fit_options']:
        for fit in db_product['fit_options']:
            if url_info['requested_fit'].lower() == fit.lower():
                fit_match = fit
                break
    
    response['display_data'] = {
        'product_name': db_product['product_name'],
        'category': f"{db_product['category']} > {db_product['subcategory']}",
        'price': f"${db_product['price']}" if db_product['price'] else 'Price not available',
        'garment_type': db_product['garment_type'] or 'Not classified',
        'available_colors': db_product['colors_available'] or [],
        'available_fits': db_product['fit_options'] or [],
        'available_sizes': db_product['sizes_available'] or [],
        'requested_color': url_info['requested_color'],
        'color_match': color_match,
        'requested_fit': url_info['requested_fit'],
        'fit_match': fit_match
    }
    
    return response

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
    
    print("🔍 V10 App URL Recognition Test")
    print("=" * 80)
    print(f"Testing {len(test_urls)} URLs to see what the app would display...\n")
    
    results = []
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n📱 Test #{i}")
        print(f"URL: {url[:80]}...")
        
        # Extract info from URL
        url_info = extract_product_info_from_url(url)
        print(f"  📋 Extracted: Code={url_info['product_code']}, Color={url_info['requested_color']}, Fit={url_info['requested_fit']}")
        
        # Check database
        db_product = None
        if url_info['product_code']:
            db_product = check_product_in_database(cur, url_info['product_code'])
        
        # Simulate app response
        response = simulate_app_response(url_info, db_product)
        results.append(response)
        
        print(f"  {response['message']}")
        
        if response['status'] == 'FOUND':
            data = response['display_data']
            print(f"\n  📦 Product Details:")
            print(f"     Name: {data['product_name']}")
            print(f"     Category: {data['category']}")
            print(f"     Type: {data['garment_type']}")
            print(f"     Price: {data['price']}")
            
            print(f"\n  🎨 Color Matching:")
            print(f"     Requested: {data['requested_color'] or 'None'}")
            if data['color_match']:
                print(f"     ✅ Match Found: {data['color_match']}")
            elif data['requested_color']:
                print(f"     ⚠️  No exact match (Available: {', '.join(data['available_colors'][:3])}...)")
            print(f"     Total colors: {len(data['available_colors'])}")
            
            print(f"\n  👔 Fit Matching:")
            print(f"     Requested: {data['requested_fit'] or 'None'}")
            if data['fit_match']:
                print(f"     ✅ Match Found: {data['fit_match']}")
            elif data['requested_fit']:
                print(f"     ⚠️  No exact match (Available: {', '.join(data['available_fits'])})")
            print(f"     Available fits: {', '.join(data['available_fits']) if data['available_fits'] else 'None specified'}")
            
            print(f"\n  📏 Sizes: {len(data['available_sizes'])} sizes available")
        
        print("-" * 80)
    
    # Summary
    print("\n📊 SUMMARY")
    print("=" * 80)
    found_count = sum(1 for r in results if r['status'] == 'FOUND')
    not_found_count = sum(1 for r in results if r['status'] == 'NOT_IN_DATABASE')
    invalid_count = sum(1 for r in results if r['status'] == 'INVALID_URL')
    
    print(f"✅ Products Found: {found_count}/{len(test_urls)}")
    print(f"❌ Not in Database: {not_found_count}/{len(test_urls)}")
    print(f"⚠️  Invalid URLs: {invalid_count}/{len(test_urls)}")
    
    if not_found_count > 0:
        print("\n🔴 Missing Products (need to be added to database):")
        for r in results:
            if r['status'] == 'NOT_IN_DATABASE':
                print(f"   - {r['product_code']}")
    
    # Check color/fit accuracy
    color_matches = 0
    fit_matches = 0
    for r in results:
        if r['status'] == 'FOUND' and r['display_data']:
            if r['display_data']['requested_color'] and r['display_data']['color_match']:
                color_matches += 1
            if r['display_data']['requested_fit'] and r['display_data']['fit_match']:
                fit_matches += 1
    
    print(f"\n🎯 Accuracy:")
    print(f"   Color Recognition: {color_matches}/{sum(1 for r in results if r['status'] == 'FOUND' and r['display_data'] and r['display_data']['requested_color'])} requested colors matched")
    print(f"   Fit Recognition: {fit_matches}/{sum(1 for r in results if r['status'] == 'FOUND' and r['display_data'] and r['display_data']['requested_fit'])} requested fits matched")
    
    conn.close()

if __name__ == "__main__":
    main()




