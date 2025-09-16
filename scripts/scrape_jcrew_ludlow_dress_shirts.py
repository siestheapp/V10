#!/usr/bin/env python3
"""
Scrape J.Crew Ludlow Premium Dress Shirts
"""

import time
import json
import sys
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ios_app.Backend.jcrew_fetcher import JCrewProductFetcher

def setup_driver(headless=True):
    """Setup Chrome driver with options"""
    options = Options()
    if headless:
        options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
    
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(30)
    return driver

def extract_ludlow_urls(driver):
    """Extract all product URLs from the Ludlow Premium dress shirts page"""
    
    url = "https://www.jcrew.com/plp/mens/categories/clothing/dress-shirts?sub-categories=men-dress-shirts-ludlowremiumdressshirts"
    print(f"🌐 Loading Ludlow Premium dress shirts page...")
    print(f"URL: {url}")
    
    driver.get(url)
    time.sleep(4)
    
    # Handle cookie banner if present
    try:
        cookie_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Accept')]")
        cookie_btn.click()
        print("🍪 Accepted cookies")
        time.sleep(1)
    except:
        pass
    
    print("📜 Scrolling to load all products...")
    
    # Scroll to load all products
    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_attempts = 0
    
    while scroll_attempts < 10:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        scroll_attempts += 1
    
    # Extract product URLs
    product_urls = set()
    
    # Try multiple selectors
    selectors = [
        "a[data-testid='product-tile-link']",
        "a[href*='/p/mens/']",
        ".product-tile a",
        "a.product-link"
    ]
    
    for selector in selectors:
        try:
            links = driver.find_elements(By.CSS_SELECTOR, selector)
            for link in links:
                href = link.get_attribute('href')
                if href and '/p/mens/' in href and 'ludlow' in href.lower():
                    # Clean URL - remove query parameters for base product
                    base_url = href.split('?')[0]
                    product_urls.add(base_url)
        except:
            continue
    
    # Also try to find product codes directly
    try:
        # Look for product codes in the page
        scripts = driver.find_elements(By.TAG_NAME, 'script')
        for script in scripts:
            content = script.get_attribute('innerHTML')
            if content and 'productCode' in content:
                # Extract product codes using regex
                import re
                codes = re.findall(r'"productCode"\s*:\s*"([A-Z0-9]+)"', content)
                for code in codes:
                    # Construct URL from code
                    product_url = f"https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/ludlow/{code}"
                    product_urls.add(product_url)
    except:
        pass
    
    print(f"✅ Found {len(product_urls)} unique Ludlow product URLs")
    return list(product_urls)

def scrape_ludlow_products(urls):
    """Scrape product details for each Ludlow dress shirt"""
    
    fetcher = JCrewProductFetcher()
    products = []
    
    print(f"\n📊 Processing {len(urls)} Ludlow products...")
    
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Processing {url.split('/')[-1]}...")
        
        try:
            # Fetch product data
            product_data = fetcher.fetch_product(url)
            
            if product_data:
                # Add category information
                product_data['category'] = 'Dress Shirts'
                product_data['subcategory'] = 'Ludlow Premium'
                product_data['brand_name'] = 'J.Crew'
                
                # Ensure we have the URL
                if 'url' not in product_data:
                    product_data['url'] = url
                
                products.append(product_data)
                
                print(f"   ✅ {product_data.get('name', 'Unknown')}")
                print(f"   Colors: {len(product_data.get('colors', []))}")
                print(f"   Price: ${product_data.get('price', 'N/A')}")
                
                # Show color variants
                colors = product_data.get('colors', [])
                if isinstance(colors, list) and colors:
                    print(f"   Color variants:")
                    for j, color in enumerate(colors[:5], 1):
                        if isinstance(color, dict):
                            print(f"      {j}. {color.get('name', 'Unknown')}")
                        else:
                            print(f"      {j}. {color}")
                    if len(colors) > 5:
                        print(f"      ... and {len(colors) - 5} more")
            else:
                print(f"   ⚠️ Failed to fetch product data")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            continue
        
        # Rate limiting
        time.sleep(1)
    
    return products

def save_results(products):
    """Save scraped products to JSON file"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"jcrew_ludlow_dress_shirts_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(products, f, indent=2, default=str)
    
    print(f"\n💾 Saved {len(products)} products to {filename}")
    return filename

def main():
    """Main function"""
    print("🚀 Starting J.Crew Ludlow Premium Dress Shirts Scraper")
    print("=" * 60)
    
    driver = setup_driver(headless=True)
    
    try:
        # Extract URLs
        urls = extract_ludlow_urls(driver)
        
        if not urls:
            print("❌ No product URLs found!")
            return
        
        # Save URLs for reference
        with open(f"jcrew_ludlow_urls_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", 'w') as f:
            for url in urls:
                f.write(url + '\n')
        
        # Scrape products
        products = scrape_ludlow_products(urls)
        
        if products:
            # Save results
            filename = save_results(products)
            
            # Summary
            print("\n" + "=" * 60)
            print("📊 SCRAPING SUMMARY")
            print("=" * 60)
            print(f"Total products scraped: {len(products)}")
            
            # Get unique product codes
            codes = set(p.get('code') for p in products if p.get('code'))
            print(f"Unique product codes: {len(codes)}")
            
            # Count total color variants
            total_colors = sum(len(p.get('colors', [])) for p in products)
            print(f"Total color variants: {total_colors}")
            
            # Price range
            prices = [p.get('price') for p in products if p.get('price')]
            if prices:
                print(f"Price range: ${min(prices)} - ${max(prices)}")
            
            print(f"\n✅ Data saved to: {filename}")
        else:
            print("❌ No products were successfully scraped")
            
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        driver.quit()
        print("\n🏁 Scraping complete!")

if __name__ == "__main__":
    main()



