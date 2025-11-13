#!/usr/bin/env python3
"""
Comprehensive scraper for J.Crew Broken-in Oxford shirts
Captures all color variants and individual product URLs
"""

import time
import json
import sys
import os
import re
from datetime import datetime

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
except ImportError:
    print("❌ Selenium not installed! Run: pip install selenium")
    sys.exit(1)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ios_app.Backend.jcrew_fetcher import JCrewProductFetcher

def setup_driver(headless=True):
    """Setup Chrome driver with anti-detection measures"""
    chrome_options = Options()
    
    if headless:
        chrome_options.add_argument("--headless")
    
    # Anti-detection measures
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    except Exception as e:
        print(f"❌ Error setting up Chrome driver: {e}")
        print("Make sure Chrome and ChromeDriver are installed:")
        print("brew install --cask google-chrome")
        print("brew install chromedriver")
        sys.exit(1)

def extract_all_product_urls(driver):
    """Extract ALL product URLs including color variants from the broken-in oxford page"""
    
    url = "https://www.jcrew.com/plp/mens/categories/clothing/shirts?sub-categories=men-shirts-brokeninoxford"
    print(f"🌐 Loading broken-in oxford shirts page...")
    print(f"URL: {url}")
    
    driver.get(url)
    
    # Wait for page to load
    time.sleep(5)
    
    # Handle cookie banner
    try:
        cookie_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Accept')]")
        cookie_btn.click()
        print("🍪 Accepted cookies")
        time.sleep(1)
    except:
        pass
    
    print("📜 Scrolling to load all products...")
    
    # More aggressive scrolling to ensure all 25 products load
    for i in range(20):
        driver.execute_script("window.scrollBy(0, 200);")
        time.sleep(0.2)
    
    # Scroll to bottom multiple times
    for i in range(5):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
    
    # Scroll back up and down to trigger lazy loading
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(1)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    
    print("🔍 Extracting ALL product URLs (including color variants)...")
    
    all_urls = set()
    
    # Method 1: Extract from all links on the page
    try:
        all_links = driver.find_elements(By.TAG_NAME, "a")
        print(f"   Found {len(all_links)} total links on page")
        
        for link in all_links:
            href = link.get_attribute('href')
            if href and '/p/mens/' in href and 'shirt' in href:
                # Clean URL but keep color parameters
                clean_url = href.split('#')[0]  # Remove fragments but keep query params
                all_urls.add(clean_url)
    except Exception as e:
        print(f"   Error extracting links: {e}")
    
    # Method 2: Extract from product tiles specifically
    try:
        product_selectors = [
            "[data-testid*='product']",
            ".product-tile",
            ".product-card", 
            ".product-item",
            "article[data-testid*='product']"
        ]
        
        for selector in product_selectors:
            try:
                tiles = driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"   Found {len(tiles)} product tiles with selector: {selector}")
                
                for tile in tiles:
                    try:
                        # Look for links within each tile
                        links = tile.find_elements(By.CSS_SELECTOR, "a[href*='/p/']")
                        for link in links:
                            href = link.get_attribute('href')
                            if href and '/p/mens/' in href:
                                clean_url = href.split('#')[0]
                                all_urls.add(clean_url)
                    except:
                        continue
            except:
                continue
    except Exception as e:
        print(f"   Error extracting from product tiles: {e}")
    
    # Method 3: JavaScript extraction to get all product URLs
    try:
        js_urls = driver.execute_script("""
            var urls = new Set();
            document.querySelectorAll('a').forEach(function(link) {
                var href = link.href;
                if (href && href.includes('/p/mens/') && href.includes('shirt')) {
                    urls.add(href.split('#')[0]);
                }
            });
            return Array.from(urls);
        """)
        
        for url in js_urls:
            all_urls.add(url)
    except Exception as e:
        print(f"   JavaScript extraction error: {e}")
    
    # Method 4: Look for specific product codes in the page source
    try:
        page_source = driver.page_source
        
        # Look for product codes in the HTML
        product_codes = re.findall(r'/([A-Z]{2}\d{3,4})(?:\?|$)', page_source)
        print(f"   Found {len(set(product_codes))} unique product codes in page source")
        
        # Try to construct URLs for these codes
        for code in set(product_codes):
            if code.startswith(('BE', 'CM', 'CH', 'MP')):
                # Try different URL patterns
                possible_urls = [
                    f"https://www.jcrew.com/p/mens/categories/clothing/shirts/broken-in-oxford/broken-in-organic-cotton-oxford-shirt/{code}",
                    f"https://www.jcrew.com/p/mens/categories/clothing/shirts/casual/broken-in-oxford-shirt/{code}",
                    f"https://www.jcrew.com/m/mens/categories/clothing/shirts/broken-in-oxford/broken-in-organic-cotton-oxford-shirt/{code}"
                ]
                
                for possible_url in possible_urls:
                    all_urls.add(possible_url)
    except Exception as e:
        print(f"   Error extracting from page source: {e}")
    
    print(f"✅ Found {len(all_urls)} total URLs")
    return list(all_urls)

def fetch_product_details(urls):
    """Use JCrewProductFetcher to get detailed product information"""
    
    print(f"\n🔄 Fetching detailed product information for {len(urls)} URLs...")
    fetcher = JCrewProductFetcher()
    all_products = []
    
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Processing {url.split('/')[-1]}...")
        
        try:
            product_data = fetcher.fetch_product(url)
            
            if product_data:
                # Process the product data
                processed_product = {
                    'url': url,
                    'code': product_data.get('product_code', ''),
                    'name': product_data.get('product_name', ''),
                    'category': product_data.get('category', 'Shirts'),
                    'subcategory': product_data.get('subcategory', 'Broken-in Oxford'),
                    'colors': product_data.get('colors_available', []),
                    'material': product_data.get('material', ''),
                    'fit_options': product_data.get('fit_options', []),
                    'sizes': product_data.get('sizes_available', []),
                    'price': product_data.get('price', ''),
                    'image_url': product_data.get('product_image', ''),
                    'description': product_data.get('description', ''),
                    'scraped_at': datetime.now().isoformat()
                }
                
                all_products.append(processed_product)
                
                # Display progress
                color_count = len(processed_product['colors']) if isinstance(processed_product['colors'], list) else 0
                print(f"   ✅ {processed_product['name']}")
                print(f"   Colors: {color_count}")
                print(f"   Price: {processed_product['price']}")
                
                if isinstance(processed_product['colors'], list) and len(processed_product['colors']) > 0:
                    print(f"   Color variants:")
                    for j, color in enumerate(processed_product['colors'][:3], 1):
                        if isinstance(color, dict):
                            print(f"      {j}. {color.get('name', 'N/A')}")
                        else:
                            print(f"      {j}. {color}")
                
                # Save progress every 10 products
                if i % 10 == 0:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    progress_file = f'jcrew_broken_in_oxford_progress_{timestamp}.json'
                    with open(progress_file, 'w') as f:
                        json.dump(all_products, f, indent=2)
                    print(f"\n💾 Progress saved to {progress_file}")
                
            else:
                print(f"   ❌ No product data returned")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:100]}")
        
        # Be polite to the server
        time.sleep(1.5)
    
    return all_products

def main():
    print("=" * 70)
    print("J.CREW BROKEN-IN OXFORD SHIRTS - COMPREHENSIVE SCRAPER")
    print("=" * 70)
    
    # Step 1: Extract ALL product URLs using browser automation
    driver = setup_driver(headless=True)
    
    try:
        all_urls = extract_all_product_urls(driver)
        print(f"\n✅ Found {len(all_urls)} total URLs")
        
        if all_urls:
            print("\nFirst 10 URLs found:")
            for url in all_urls[:10]:
                print(f"   - {url}")
            if len(all_urls) > 10:
                print(f"   ... and {len(all_urls) - 10} more")
            
            # Save URLs
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            urls_file = f'jcrew_broken_in_oxford_all_urls_{timestamp}.txt'
            with open(urls_file, 'w') as f:
                for url in all_urls:
                    f.write(f"{url}\n")
            print(f"\n💾 Saved all URLs to {urls_file}")
        
    finally:
        driver.quit()
        print("🔚 Browser closed")
    
    # Step 2: Fetch detailed product information
    if all_urls:
        print("\n" + "=" * 70)
        print("FETCHING DETAILED PRODUCT INFORMATION")
        print("=" * 70)
        
        all_products = fetch_product_details(all_urls)
        
        # Save final results
        if all_products:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            final_file = f'jcrew_broken_in_oxford_comprehensive_{timestamp}.json'
            with open(final_file, 'w') as f:
                json.dump(all_products, f, indent=2)
            
            print("\n" + "=" * 70)
            print("FINAL RESULTS")
            print("=" * 70)
            print(f"💾 Saved {len(all_products)} products to {final_file}")
            
            # Statistics
            total_colors = 0
            products_with_multiple_colors = 0
            unique_codes = set()
            
            for product in all_products:
                unique_codes.add(product['code'])
                if isinstance(product['colors'], list):
                    color_count = len(product['colors'])
                    total_colors += color_count
                    if color_count > 1:
                        products_with_multiple_colors += 1
            
            print(f"\n📊 SUMMARY:")
            print(f"   Total products processed: {len(all_products)}")
            print(f"   Unique product codes: {len(unique_codes)}")
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
                    print(f"   Price: {product['price']}")
                    print(f"   Colors ({len(product['colors'])}):")
                    for color in product['colors'][:5]:
                        if isinstance(color, dict):
                            print(f"      - {color.get('name', 'N/A')}")
                        else:
                            print(f"      - {color}")
        else:
            print("❌ No products were successfully processed")
    else:
        print("❌ No product URLs found to process")

if __name__ == "__main__":
    main()

