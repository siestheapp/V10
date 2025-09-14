#!/usr/bin/env python3
"""
Extract ALL J.Crew Secret Wash shirts and cache them
58 items as shown on the page
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
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
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

def extract_secret_wash_urls(driver):
    """Extract ALL Secret Wash product URLs from the listing page"""
    
    url = "https://www.jcrew.com/plp/mens/categories/clothing/shirts?sub-categories=men-shirts-secretwash"
    print(f"🌐 Loading J.Crew Secret Wash shirts page...")
    print(f"   URL: {url}")
    driver.get(url)
    
    # Wait for page load
    time.sleep(5)
    
    # Handle cookie banner
    try:
        cookie_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Accept')]")
        cookie_btn.click()
        time.sleep(1)
    except:
        pass
    
    print("📜 Scrolling to load all 58 items...")
    
    # Scroll multiple times to ensure all items load
    last_height = 0
    scroll_attempts = 0
    max_attempts = 15
    
    while scroll_attempts < max_attempts:
        # Scroll down in increments
        for i in range(5):
            driver.execute_script(f"window.scrollTo(0, {(i+1) * 1000});")
            time.sleep(0.5)
        
        # Scroll to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        # Check if new content loaded
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            # Try clicking "Load More" button if it exists
            try:
                load_more = driver.find_element(By.XPATH, "//button[contains(text(), 'Load More')]")
                load_more.click()
                print("   Clicked 'Load More' button")
                time.sleep(3)
            except:
                break
        
        last_height = new_height
        scroll_attempts += 1
        print(f"   Scroll attempt {scroll_attempts}/{max_attempts}")
    
    print("🔍 Extracting all Secret Wash product URLs...")
    
    # Extract ALL links
    all_urls = []
    product_by_code = defaultdict(list)
    
    # Multiple selectors to catch all product links
    selectors = [
        "a[href*='/p/mens/']",
        "a[href*='/m/mens/']",
        "a.product-tile__link",
        "a[data-testid='product-link']"
    ]
    
    links = []
    for selector in selectors:
        links.extend(driver.find_elements(By.CSS_SELECTOR, selector))
    
    # De-duplicate by href
    seen_hrefs = set()
    for link in links:
        href = link.get_attribute('href')
        if href and href not in seen_hrefs:
            seen_hrefs.add(href)
            
            # Filter for shirt products
            if ('/p/mens/' in href or '/m/mens/') and '/shirts/' in href:
                # Clean the URL but keep color parameters
                if '?' in href:
                    base_url = href.split('?')[0]
                    # Parse color from URL parameters
                    color_match = re.search(r'color_name=([^&]+)', href)
                    color_name = color_match.group(1) if color_match else ''
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
    for code, variations in list(product_by_code.items())[:10]:  # Show first 10
        print(f"   {code}: {len(variations)} color variations")
    
    if len(product_by_code) > 10:
        print(f"   ... and {len(product_by_code) - 10} more products")
    
    return all_urls, product_by_code

def process_secret_wash_products(product_by_code):
    """Process each unique Secret Wash product to get all color data"""
    
    fetcher = JCrewProductFetcher()
    all_products = []
    
    print("\n" + "=" * 60)
    print("PROCESSING SECRET WASH PRODUCTS")
    print("=" * 60)
    
    total_products = len(product_by_code)
    processed = 0
    
    for code, variations in product_by_code.items():
        processed += 1
        print(f"\n📦 [{processed}/{total_products}] Product {code}")
        
        # Use the first URL to fetch the product (fetcher will get all colors)
        base_url = variations[0]['base_url']
        
        try:
            product_data = fetcher.fetch_product(base_url)
            
            if product_data:
                colors = product_data.get('colors_available', [])
                
                print(f"   ✅ {product_data.get('product_name', 'Unknown')}")
                print(f"   Total colors available: {len(colors) if isinstance(colors, list) else 0}")
                
                # Show first few color details
                if isinstance(colors, list) and len(colors) > 0:
                    for i, color in enumerate(colors[:3], 1):
                        if isinstance(color, dict):
                            name = color.get('name', 'N/A')
                            hex_val = color.get('hex', 'N/A')
                            print(f"      {i}. {name:<30} Hex: {hex_val}")
                    
                    if len(colors) > 3:
                        print(f"      ... and {len(colors) - 3} more colors")
                
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
        
        # Be polite to J.Crew's servers
        time.sleep(1.5)
        
        # Progress indicator every 10 products
        if processed % 10 == 0:
            print(f"\n{'=' * 40}")
            print(f"Progress: {processed}/{total_products} products processed")
            print(f"{'=' * 40}")
    
    return all_products

def main():
    print("=" * 60)
    print("J.CREW SECRET WASH SHIRTS - COMPLETE EXTRACTION")
    print("Premium 100% cotton poplin shirts - 58 items")
    print("=" * 60)
    
    # Step 1: Get all URLs from listing page
    driver = setup_driver(headless=True)
    
    try:
        all_urls, product_by_code = extract_secret_wash_urls(driver)
        
        # Save all URLs found
        with open('jcrew_secret_wash_urls.json', 'w') as f:
            json.dump({
                'total_urls': len(all_urls),
                'unique_products': len(product_by_code),
                'urls': all_urls,
                'by_product': {code: [v['url'] for v in variations] 
                             for code, variations in product_by_code.items()}
            }, f, indent=2)
        
        print(f"\n💾 Saved all {len(all_urls)} URLs to jcrew_secret_wash_urls.json")
        
    finally:
        driver.quit()
        print("🔚 Browser closed")
    
    # Step 2: Process unique products to get all color data
    if product_by_code:
        print(f"\n🎯 Processing {len(product_by_code)} unique Secret Wash products...")
        all_products = process_secret_wash_products(product_by_code)
        
        # Save final results
        if all_products:
            with open('jcrew_secret_wash_complete.json', 'w') as f:
                json.dump(all_products, f, indent=2)
            
            print("\n" + "=" * 60)
            print("FINAL RESULTS")
            print("=" * 60)
            print(f"💾 Saved {len(all_products)} products to jcrew_secret_wash_complete.json")
            
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
            print(f"\n🌈 TOP SECRET WASH PRODUCTS BY COLOR VARIETY:")
            sorted_products = sorted(all_products, 
                                    key=lambda p: len(p['colors']) if isinstance(p['colors'], list) else 0, 
                                    reverse=True)
            
            for i, product in enumerate(sorted_products[:5], 1):
                if isinstance(product['colors'], list):
                    print(f"\n   {i}. {product['name']}")
                    print(f"      Code: {product['code']}")
                    print(f"      Colors available: {len(product['colors'])}")
                    print(f"      Fit options: {', '.join(product['fit_options']) if product['fit_options'] else 'N/A'}")
                    
                    # List first few colors
                    for color in product['colors'][:5]:
                        if isinstance(color, dict):
                            name = color.get('name', 'N/A')
                            hex_val = color.get('hex', 'N/A')
                            has_image = '✓' if color.get('imageUrl') else '✗'
                            print(f"         • {name:<30} Hex: {hex_val:<8} Image: {has_image}")
                    
                    if len(product['colors']) > 5:
                        print(f"         ... and {len(product['colors']) - 5} more colors")
            
            print("\n✨ Ready to provide instant loading for all Secret Wash shirts!")

if __name__ == "__main__":
    main()
