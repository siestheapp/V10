#!/usr/bin/env python3
"""
Extract ALL J.Crew linen shirt variations (each color shown as separate item)
Then fetch complete color data for each unique product
"""

import time
import json
import re
import sys
import os
from collections import defaultdict

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
except ImportError:
    print("❌ Selenium not installed! Run: pip install selenium")
    sys.exit(1)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ios_app.Backend.jcrew_fetcher import JCrewProductFetcher

def setup_driver(headless=True):
    """Setup Chrome driver"""
    chrome_options = Options()
    
    if headless:
        chrome_options.add_argument("--headless")
    
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def extract_all_color_urls(driver):
    """Extract ALL product URLs including color variations from the listing page"""
    
    url = "https://www.jcrew.com/plp/mens/categories/clothing/shirts?sub-categories=men-shirts-linen"
    print(f"🌐 Loading J.Crew linen shirts page...")
    driver.get(url)
    
    # Wait for page load
    time.sleep(4)
    
    # Handle cookie banner
    try:
        cookie_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Accept')]")
        cookie_btn.click()
        time.sleep(1)
    except:
        pass
    
    print("📜 Scrolling to load all 21 items...")
    
    # Scroll multiple times to ensure all items load
    for i in range(8):
        driver.execute_script(f"window.scrollTo(0, {i * 500});")
        time.sleep(0.5)
    
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    
    # Go back to top and scroll down again to trigger any lazy loading
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(1)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    
    print("🔍 Extracting all product URLs (including color variations)...")
    
    # Extract ALL links, including color variations
    all_urls = []
    product_by_code = defaultdict(list)
    
    # Get all product links
    links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/p/'], a[href*='/m/mens/']")
    
    for link in links:
        href = link.get_attribute('href')
        if href and ('/p/' in href or '/m/mens/categories/clothing/shirts' in href):
            # Clean the URL but keep color parameters
            if '?' in href:
                base_url = href.split('?')[0]
                # Parse color from URL parameters
                if 'color_name=' in href:
                    color_match = re.search(r'color_name=([^&]+)', href)
                    color_name = color_match.group(1) if color_match else ''
                else:
                    color_name = ''
            else:
                base_url = href
                color_name = ''
            
            # Extract product code
            code_match = re.search(r'/([A-Z0-9]{4,6})(?:\?|$)', base_url)
            if code_match:
                code = code_match.group(1)
                product_by_code[code].append({
                    'url': href,
                    'base_url': base_url,
                    'color_name': color_name
                })
                all_urls.append(href)
    
    print(f"\n📊 Found {len(all_urls)} total URLs")
    print(f"📦 Unique product codes: {len(product_by_code)}")
    
    # Display breakdown
    for code, variations in product_by_code.items():
        print(f"   {code}: {len(variations)} color variations")
    
    return all_urls, product_by_code

def process_unique_products(product_by_code):
    """Process each unique product to get all color data"""
    
    fetcher = JCrewProductFetcher()
    all_products = []
    
    print("\n" + "=" * 60)
    print("PROCESSING UNIQUE PRODUCTS")
    print("=" * 60)
    
    for code, variations in product_by_code.items():
        print(f"\n📦 Product {code} ({len(variations)} variations found on listing)")
        
        # Use the first URL to fetch the product (fetcher will get all colors)
        base_url = variations[0]['base_url']
        
        try:
            product_data = fetcher.fetch_product(base_url)
            
            if product_data:
                colors = product_data.get('colors_available', [])
                
                print(f"   ✅ {product_data.get('product_name', 'Unknown')}")
                print(f"   Total colors available: {len(colors) if isinstance(colors, list) else 0}")
                
                # Show color details
                if isinstance(colors, list) and len(colors) > 0:
                    for i, color in enumerate(colors[:5], 1):
                        if isinstance(color, dict):
                            name = color.get('name', 'N/A')
                            hex_val = color.get('hex', 'N/A')
                            print(f"      {i}. {name:<25} Hex: {hex_val}")
                        else:
                            print(f"      {i}. {color}")
                    
                    if len(colors) > 5:
                        print(f"      ... and {len(colors) - 5} more colors")
                
                # Store product data
                all_products.append({
                    'code': code,
                    'url': base_url,
                    'name': product_data.get('product_name', ''),
                    'colors': colors,
                    'material': product_data.get('material', ''),
                    'price': product_data.get('price', ''),
                    'sizes': product_data.get('sizes_available', []),
                    'fit_options': product_data.get('fit_options', []),
                    'variations_on_listing': len(variations)
                })
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:100]}")
        
        time.sleep(1.5)  # Be polite
    
    return all_products

def main():
    print("=" * 60)
    print("J.CREW LINEN SHIRTS - COMPLETE COLOR EXTRACTION")
    print("Understanding that each color is shown as a separate item")
    print("=" * 60)
    
    # Step 1: Get all URLs from listing page
    driver = setup_driver(headless=True)
    
    try:
        all_urls, product_by_code = extract_all_color_urls(driver)
        
        # Save all URLs found
        with open('jcrew_all_21_urls.json', 'w') as f:
            json.dump({
                'total_urls': len(all_urls),
                'unique_products': len(product_by_code),
                'urls': all_urls,
                'by_product': {code: [v['url'] for v in variations] 
                             for code, variations in product_by_code.items()}
            }, f, indent=2)
        
        print(f"\n💾 Saved all {len(all_urls)} URLs to jcrew_all_21_urls.json")
        
    finally:
        driver.quit()
        print("🔚 Browser closed")
    
    # Step 2: Process unique products to get all color data
    if product_by_code:
        all_products = process_unique_products(product_by_code)
        
        # Save final results
        if all_products:
            with open('jcrew_linen_all_21_complete.json', 'w') as f:
                json.dump(all_products, f, indent=2)
            
            print("\n" + "=" * 60)
            print("FINAL RESULTS")
            print("=" * 60)
            print(f"💾 Saved {len(all_products)} products to jcrew_linen_all_21_complete.json")
            
            # Calculate statistics
            total_colors = sum(len(p['colors']) if isinstance(p['colors'], list) else 0 for p in all_products)
            total_variations = sum(p['variations_on_listing'] for p in all_products)
            
            print(f"\n📊 SUMMARY:")
            print(f"   Unique products: {len(all_products)}")
            print(f"   Total items on listing page: {total_variations}")
            print(f"   Total colors across all products: {total_colors}")
            if len(all_products) > 0:
                print(f"   Average colors per product: {total_colors/len(all_products):.1f}")
            
            # Show products with most colors
            print(f"\n🌈 PRODUCTS AND THEIR COLORS:")
            sorted_products = sorted(all_products, 
                                    key=lambda p: len(p['colors']) if isinstance(p['colors'], list) else 0, 
                                    reverse=True)
            
            for product in sorted_products:
                if isinstance(product['colors'], list):
                    print(f"\n   {product['name']}")
                    print(f"   Code: {product['code']}")
                    print(f"   Colors available: {len(product['colors'])}")
                    print(f"   Shown on listing: {product['variations_on_listing']} items")
                    
                    # List first few colors
                    for color in product['colors'][:8]:
                        if isinstance(color, dict):
                            name = color.get('name', 'N/A')
                            hex_val = color.get('hex', 'N/A')
                            has_image = '✓' if color.get('imageUrl') else '✗'
                            print(f"      • {name:<25} Hex: {hex_val:<8} Image: {has_image}")
                        else:
                            print(f"      • {color}")
                    
                    if len(product['colors']) > 8:
                        print(f"      ... and {len(product['colors']) - 8} more colors")

if __name__ == "__main__":
    main()
