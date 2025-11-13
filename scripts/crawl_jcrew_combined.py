#!/usr/bin/env python3
"""
Combined approach: Use browser to get ALL product URLs from listing,
then use JCrewProductFetcher to get color data (it already works well)
"""

import time
import json
import sys
import os
import re

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

def get_all_product_urls(driver):
    """Get ALL product URLs from the linen shirts page"""
    
    url = "https://www.jcrew.com/plp/mens/categories/clothing/shirts?sub-categories=men-shirts-linen"
    print(f"🌐 Loading linen shirts page...")
    driver.get(url)
    
    # Initial wait
    time.sleep(4)
    
    # Handle cookie banner
    try:
        cookie_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Accept')]")
        cookie_btn.click()
        time.sleep(1)
    except:
        pass
    
    print("📜 Aggressive scrolling to ensure all 21 products load...")
    
    # Method 1: Scroll multiple times slowly
    for i in range(10):
        # Scroll down
        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(0.5)
    
    # Scroll to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    
    # Scroll back up and down to trigger any lazy loading
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(1)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    
    print("🔍 Extracting product URLs...")
    
    # Extract ALL product links
    product_data = {}
    
    # Try multiple selectors to catch all products
    selectors = [
        "a[href*='/p/mens/'][href*='shirt']",
        "a[href*='/p/'][href*='CG']",
        "a[href*='/p/'][href*='CF']",
        "a[href*='/p/'][href*='BW']",
        "article a[href*='/p/']",
        ".product-tile a[href*='/p/']",
        "[data-testid*='product'] a[href*='/p/']",
        "a[href*='categories/clothing/shirts']"
    ]
    
    for selector in selectors:
        try:
            links = driver.find_elements(By.CSS_SELECTOR, selector)
            print(f"   Selector '{selector[:30]}...' found {len(links)} links")
            
            for link in links:
                href = link.get_attribute('href')
                if href and '/p/' in href:
                    # Extract product code
                    match = re.search(r'/([A-Z0-9]{4,6})(?:\?|$)', href)
                    if match:
                        code = match.group(1)
                        clean_url = href.split('?')[0]
                        
                        if code not in product_data:
                            product_data[code] = clean_url
        except:
            continue
    
    # Also try JavaScript extraction
    try:
        js_urls = driver.execute_script("""
            var urls = new Set();
            document.querySelectorAll('a').forEach(function(link) {
                var href = link.href;
                if (href && href.includes('/p/') && href.includes('shirt')) {
                    urls.add(href.split('?')[0]);
                }
            });
            return Array.from(urls);
        """)
        
        for url in js_urls:
            match = re.search(r'/([A-Z0-9]{4,6})(?:\?|$)', url)
            if match:
                code = match.group(1)
                if code not in product_data:
                    product_data[code] = url
    except:
        pass
    
    return list(product_data.values())

def main():
    print("=" * 60)
    print("J.CREW LINEN SHIRTS - COMPLETE EXTRACTION")
    print("Combined Browser + Fetcher Approach")
    print("=" * 60)
    
    # Step 1: Use browser to get ALL product URLs
    driver = setup_driver(headless=True)
    
    try:
        product_urls = get_all_product_urls(driver)
        print(f"\n✅ Found {len(product_urls)} unique product URLs")
        
        if product_urls:
            print("\nProduct codes found:")
            for url in product_urls[:10]:
                code = url.split('/')[-1]
                print(f"   - {code}")
            if len(product_urls) > 10:
                print(f"   ... and {len(product_urls) - 10} more")
            
            # Save URLs
            with open('jcrew_linen_all_urls.txt', 'w') as f:
                for url in product_urls:
                    f.write(f"{url}\n")
            print(f"\n💾 Saved all URLs to jcrew_linen_all_urls.txt")
        
    finally:
        driver.quit()
        print("🔚 Browser closed")
    
    # Step 2: Use JCrewProductFetcher to get color data for each product
    if product_urls:
        print("\n" + "=" * 60)
        print("FETCHING COLOR DATA")
        print("=" * 60)
        
        fetcher = JCrewProductFetcher()
        all_products = []
        
        for i, url in enumerate(product_urls, 1):
            print(f"\n[{i}/{len(product_urls)}] Processing {url.split('/')[-1]}...")
            
            try:
                product_data = fetcher.fetch_product(url)
                
                if product_data:
                    colors = product_data.get('colors_available', [])
                    
                    # Convert to our format
                    processed_product = {
                        'url': url,
                        'code': product_data.get('product_code', ''),
                        'name': product_data.get('product_name', ''),
                        'colors': colors,
                        'material': product_data.get('material', ''),
                        'fit_options': product_data.get('fit_options', []),
                        'sizes': product_data.get('sizes_available', []),
                        'price': product_data.get('price', '')
                    }
                    
                    all_products.append(processed_product)
                    
                    # Display progress
                    color_count = len(colors) if isinstance(colors, list) else 0
                    print(f"   ✅ {product_data.get('product_name', 'Unknown')}")
                    print(f"   Colors: {color_count}")
                    
                    if isinstance(colors, list) and len(colors) > 0:
                        for j, color in enumerate(colors[:3], 1):
                            if isinstance(color, dict):
                                print(f"      {j}. {color.get('name', 'N/A')}")
                            else:
                                print(f"      {j}. {color}")
                    
                    # Save progress
                    if i % 5 == 0:
                        with open('jcrew_linen_complete_progress.json', 'w') as f:
                            json.dump(all_products, f, indent=2)
                        print(f"\n💾 Progress saved ({i}/{len(product_urls)})")
                    
            except Exception as e:
                print(f"   ❌ Error: {str(e)[:100]}")
            
            # Be polite
            time.sleep(1.5)
        
        # Save final results
        if all_products:
            with open('jcrew_linen_complete_final.json', 'w') as f:
                json.dump(all_products, f, indent=2)
            
            print("\n" + "=" * 60)
            print("FINAL RESULTS")
            print("=" * 60)
            print(f"💾 Saved {len(all_products)} products to jcrew_linen_complete_final.json")
            
            # Statistics
            total_colors = 0
            products_with_multiple_colors = 0
            
            for product in all_products:
                if isinstance(product['colors'], list):
                    color_count = len(product['colors'])
                    total_colors += color_count
                    if color_count > 1:
                        products_with_multiple_colors += 1
            
            print(f"\n📊 SUMMARY:")
            print(f"   Total products processed: {len(all_products)}")
            print(f"   Products with multiple colors: {products_with_multiple_colors}")
            print(f"   Total color variants: {total_colors}")
            if len(all_products) > 0:
                print(f"   Average colors per product: {total_colors/len(all_products):.1f}")
            
            # Show products with most colors
            print(f"\n🌈 PRODUCTS WITH MOST COLORS:")
            sorted_products = sorted(all_products, 
                                    key=lambda p: len(p['colors']) if isinstance(p['colors'], list) else 0, 
                                    reverse=True)
            
            for product in sorted_products[:5]:
                if isinstance(product['colors'], list) and len(product['colors']) > 1:
                    print(f"\n   {product['name']}")
                    print(f"   Code: {product['code']}")
                    print(f"   Colors ({len(product['colors'])}):")
                    for color in product['colors'][:5]:
                        if isinstance(color, dict):
                            hex_str = color.get('hex', 'No hex')
                            print(f"      - {color.get('name', 'N/A')} ({hex_str})")
                        else:
                            print(f"      - {color}")

if __name__ == "__main__":
    main()

