#!/usr/bin/env python3
"""
Enhanced browser automation to extract ALL J.Crew linen shirt products
Handles dynamic loading and multiple product grid layouts
"""

import time
import json
import sys
import os
import re

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.action_chains import ActionChains
except ImportError:
    print("❌ Selenium not installed! Run: pip install selenium")
    sys.exit(1)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

def extract_all_products(driver):
    """Extract ALL product URLs from the linen shirts page"""
    
    url = "https://www.jcrew.com/plp/mens/categories/clothing/shirts?sub-categories=men-shirts-linen"
    print(f"🌐 Loading J.Crew linen shirts page...")
    driver.get(url)
    
    # Wait for initial page load
    time.sleep(4)
    
    # Handle cookie banner if present
    try:
        cookie_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'OK')]")
        cookie_btn.click()
        print("🍪 Accepted cookies")
        time.sleep(1)
    except:
        pass
    
    # Close any popup overlays
    try:
        close_btn = driver.find_element(By.CSS_SELECTOR, "[aria-label='Close']")
        close_btn.click()
        time.sleep(1)
    except:
        pass
    
    print("📜 Scrolling to load all products...")
    
    # Scroll method 1: Incremental scrolling
    last_count = 0
    scroll_pause = 2
    max_scrolls = 20
    
    for i in range(max_scrolls):
        # Scroll down by viewport height
        driver.execute_script("window.scrollBy(0, window.innerHeight);")
        time.sleep(scroll_pause)
        
        # Check if new products loaded
        products = driver.find_elements(By.CSS_SELECTOR, "a[href*='/p/']")
        current_count = len(products)
        print(f"   Scroll {i+1}: Found {current_count} product links")
        
        if current_count == last_count and current_count >= 21:
            break
        last_count = current_count
    
    # Scroll to bottom to ensure everything is loaded
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    
    print("🔍 Extracting product information...")
    
    product_data = {}
    
    # Method 1: Find all links with /p/ in the URL
    all_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/p/']")
    print(f"   Found {len(all_links)} total links with /p/")
    
    for link in all_links:
        try:
            href = link.get_attribute('href')
            if not href or 'categories/clothing/shirts' not in href:
                continue
                
            # Extract product code
            match = re.search(r'/p/.*?/([A-Z0-9]{4,6})(?:\?|$)', href)
            if not match:
                match = re.search(r'/p/([A-Z0-9]{4,6})(?:\?|$)', href)
            
            if match:
                code = match.group(1)
                clean_url = href.split('?')[0]
                
                # Try to get product name
                name = ""
                try:
                    # Look for product name in the link or nearby elements
                    parent = link.find_element(By.XPATH, "..")
                    name_elem = parent.find_element(By.CSS_SELECTOR, "h3, h4, [class*='product-name'], [class*='product-title']")
                    name = name_elem.text.strip()
                except:
                    try:
                        # Alternative: get from link title or aria-label
                        name = link.get_attribute('title') or link.get_attribute('aria-label') or ""
                    except:
                        pass
                
                if code not in product_data:
                    product_data[code] = {
                        'url': clean_url,
                        'code': code,
                        'name': name
                    }
        except Exception as e:
            continue
    
    # Method 2: Look for product tiles/cards with more specific selectors
    selectors = [
        "article[class*='product']",
        "div[class*='product-tile']",
        "div[class*='product-card']",
        "div[data-testid*='product']",
        "li[class*='product']"
    ]
    
    for selector in selectors:
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        print(f"   Found {len(elements)} elements with selector: {selector}")
        
        for elem in elements:
            try:
                link = elem.find_element(By.CSS_SELECTOR, "a[href*='/p/']")
                href = link.get_attribute('href')
                
                if href:
                    match = re.search(r'/([A-Z0-9]{4,6})(?:\?|$)', href)
                    if match:
                        code = match.group(1)
                        clean_url = href.split('?')[0]
                        
                        # Get product name
                        name = ""
                        try:
                            name_elem = elem.find_element(By.CSS_SELECTOR, "h3, h4, [class*='name']")
                            name = name_elem.text.strip()
                        except:
                            pass
                        
                        if code not in product_data:
                            product_data[code] = {
                                'url': clean_url,
                                'code': code,
                                'name': name
                            }
            except:
                continue
    
    # Method 3: Execute JavaScript to get product data
    try:
        # Try to extract from React/Vue data
        js_products = driver.execute_script("""
            // Try to find product data in various places
            var products = [];
            
            // Check for __NEXT_DATA__ (Next.js)
            if (window.__NEXT_DATA__ && window.__NEXT_DATA__.props) {
                var data = window.__NEXT_DATA__.props;
                // Navigate through the data structure to find products
                // This varies by site structure
            }
            
            // Check for window.products or similar
            if (window.products) {
                products = window.products;
            }
            
            // Find all product links
            var links = document.querySelectorAll('a[href*="/p/"]');
            links.forEach(function(link) {
                var href = link.href;
                var matches = href.match(/\/([A-Z0-9]{4,6})(?:\\?|$)/);
                if (matches) {
                    products.push({
                        code: matches[1],
                        url: href.split('?')[0],
                        name: link.title || link.getAttribute('aria-label') || ''
                    });
                }
            });
            
            return products;
        """)
        
        if js_products:
            print(f"   Found {len(js_products)} products via JavaScript")
            for prod in js_products:
                if isinstance(prod, dict) and 'code' in prod:
                    code = prod['code']
                    if code not in product_data:
                        product_data[code] = prod
    except:
        pass
    
    return list(product_data.values())

def process_products_with_fetcher(products):
    """Process products with the JCrewProductFetcher to get color data"""
    from src.ios_app.Backend.jcrew_fetcher import JCrewProductFetcher
    
    fetcher = JCrewProductFetcher()
    results = []
    
    print(f"\n🔄 Processing {len(products)} unique products...")
    
    for i, product in enumerate(products, 1):
        print(f"\n[{i}/{len(products)}] {product['code']}")
        
        try:
            # Fetch full product data
            product_data = fetcher.fetch_product(product['url'])
            
            if product_data:
                colors = product_data.get('colors_available', [])
                
                # Count colors with rich data
                rich_colors = 0
                if isinstance(colors, list):
                    for color in colors:
                        if isinstance(color, dict) and color.get('hex'):
                            rich_colors += 1
                
                print(f"   ✅ {product_data.get('product_name', 'Unknown')}")
                print(f"   Colors: {len(colors) if isinstance(colors, list) else 0} ({rich_colors} with hex)")
                
                # Show first few colors
                if isinstance(colors, list) and len(colors) > 0:
                    for j, color in enumerate(colors[:3], 1):
                        if isinstance(color, dict):
                            print(f"      {j}. {color.get('name', 'N/A')}")
                
                results.append({
                    'url': product['url'],
                    'code': product_data.get('product_code', product['code']),
                    'name': product_data.get('product_name', product.get('name', '')),
                    'colors': colors,
                    'material': product_data.get('material', ''),
                    'fit_options': product_data.get('fit_options', [])
                })
            else:
                print(f"   ⚠️  No data returned")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:100]}")
        
        # Be polite to J.Crew's servers
        time.sleep(1.2)
    
    return results

def main():
    print("=" * 60)
    print("J.CREW LINEN SHIRTS - COMPLETE EXTRACTION")
    print("=" * 60)
    
    # Setup browser (set headless=False to see the browser)
    driver = setup_driver(headless=True)
    
    try:
        # Extract all products
        products = extract_all_products(driver)
        
        print(f"\n✅ Found {len(products)} unique products")
        
        if products:
            # Save raw product list
            with open('jcrew_linen_products_raw.json', 'w') as f:
                json.dump(products, f, indent=2)
            print(f"💾 Saved raw product list to jcrew_linen_products_raw.json")
            
            # Show summary
            print("\n📋 Products found:")
            for i, prod in enumerate(products[:10], 1):
                print(f"   {i}. {prod['code']}: {prod.get('name', 'No name')[:50]}")
            if len(products) > 10:
                print(f"   ... and {len(products) - 10} more")
            
            # Process with fetcher to get colors
            print("\n" + "=" * 60)
            print("FETCHING COLOR DATA")
            print("=" * 60)
            
            results = process_products_with_fetcher(products)
            
            # Save complete results
            if results:
                with open('jcrew_linen_complete.json', 'w') as f:
                    json.dump(results, f, indent=2)
                print(f"\n💾 Saved {len(results)} products with color data to jcrew_linen_complete.json")
                
                # Summary statistics
                total_colors = sum(len(r['colors']) if isinstance(r['colors'], list) else 0 for r in results)
                products_with_colors = sum(1 for r in results if isinstance(r.get('colors'), list) and len(r['colors']) > 1)
                
                print(f"\n📊 SUMMARY:")
                print(f"   Total products: {len(results)}")
                print(f"   Products with multiple colors: {products_with_colors}")
                print(f"   Total color variants: {total_colors}")
                if products_with_colors > 0:
                    print(f"   Average colors per product: {total_colors/len(results):.1f}")
        
    finally:
        print("\n🔚 Closing browser...")
        driver.quit()

if __name__ == "__main__":
    main()

