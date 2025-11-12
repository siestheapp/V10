#!/usr/bin/env python3
"""
Fresh Selenium-based Oxford scraper
No hardcoded data, full transparency
"""

import time
import re
import json
import psycopg2
from datetime import datetime
from db_config import DB_CONFIG

def setup_selenium():
    """Setup Selenium with Chrome"""
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import TimeoutException, NoSuchElementException
    except ImportError:
        print("❌ Selenium not installed!")
        print("   Run: pip install selenium")
        return None, None
    
    print("🔧 Setting up Chrome with anti-detection...")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        # Hide webdriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        print("✅ Chrome driver ready")
        return driver, (By, WebDriverWait, EC, TimeoutException, NoSuchElementException)
    except Exception as e:
        print(f"❌ Failed to start Chrome: {e}")
        return None, None

def scrape_oxford_page(driver, selenium_imports):
    """Scrape the J.Crew Oxford page"""
    By, WebDriverWait, EC, TimeoutException, NoSuchElementException = selenium_imports
    
    url = "https://www.jcrew.com/plp/mens/categories/clothing/shirts?sub-categories=men-shirts-brokeninoxford"
    
    print(f"\n📍 Navigating to: {url}")
    driver.get(url)
    
    print("⏳ Waiting for page to load...")
    time.sleep(5)  # Initial wait
    
    # Handle cookie banner if present
    try:
        cookie_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Accept')]")
        cookie_btn.click()
        print("🍪 Accepted cookies")
        time.sleep(1)
    except:
        pass
    
    print("📜 Scrolling to load all products...")
    
    # Scroll progressively to trigger lazy loading
    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_attempts = 0
    
    while scroll_attempts < 10:
        # Scroll down
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        # Check if more content loaded
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        scroll_attempts += 1
        print(f"   Scroll {scroll_attempts}: Page height = {new_height}px")
    
    print("\n🔍 Extracting product information...")
    
    products = {}
    
    # Method 1: Find all product links
    product_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/broken-in-oxford/']")
    print(f"   Found {len(product_links)} Oxford product links")
    
    for link in product_links:
        href = link.get_attribute('href')
        if href and '/p/' in href:
            # Extract product code from URL
            match = re.search(r'/([A-Z0-9]{5,6})(?:\?|$)', href)
            if match:
                code = match.group(1)
                # Try to get product name from link text or nearby element
                try:
                    # Try parent element for product name
                    parent = link.find_element(By.XPATH, "..")
                    name = parent.text.split('\n')[0] if parent.text else "Unknown"
                except:
                    name = link.text or "Unknown"
                
                if code not in products:
                    products[code] = {
                        'code': code,
                        'name': name,
                        'url': href.split('?')[0],  # Clean URL
                        'variants': []
                    }
                
                # Track color variants if in URL
                if 'color_name=' in href:
                    color = href.split('color_name=')[1].split('&')[0]
                    products[code]['variants'].append(color)
    
    # Method 2: Look for product tiles/cards
    selectors = [
        "[data-testid*='product']",
        ".product-tile",
        ".product-card",
        "article[class*='product']"
    ]
    
    for selector in selectors:
        try:
            tiles = driver.find_elements(By.CSS_SELECTOR, selector)
            if tiles:
                print(f"   Found {len(tiles)} elements with selector: {selector}")
                for tile in tiles[:5]:  # Sample first 5
                    try:
                        text = tile.text
                        if text:
                            lines = text.split('\n')
                            if lines:
                                print(f"      Sample: {lines[0][:50]}...")
                    except:
                        pass
                break
        except:
            continue
    
    # Method 3: Check page source for product data
    page_source = driver.page_source
    
    # Look for product codes in the source
    code_pattern = r'(?:product[Cc]ode|sku|item[Cc]ode)[":\s]+["\']*([A-Z][A-Z0-9]{4,5})["\']'
    found_codes = re.findall(code_pattern, page_source)
    
    for code in set(found_codes):
        if code not in products and code not in ['CLASS', 'STYLE', 'FALSE', 'TRUE']:  # Filter out non-product codes
            products[code] = {
                'code': code,
                'name': 'Found in page source',
                'url': None,
                'variants': []
            }
    
    return products

def compare_with_database(products):
    """Compare scraped products with database"""
    
    print("\n" + "="*80)
    print("COMPARING WITH DATABASE")
    print("="*80)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG, connect_timeout=5)
        cur = conn.cursor()
        
        # Get Oxford products from database
        cur.execute('''
            SELECT product_code, product_name, subcategory, product_url
            FROM jcrew_product_cache
            WHERE subcategory = 'Oxford'
            OR LOWER(product_url) LIKE '%oxford%'
            ORDER BY product_code
        ''')
        
        db_products = {row[0]: {'name': row[1], 'subcategory': row[2], 'url': row[3]} 
                      for row in cur.fetchall()}
        
        scraped_codes = set(products.keys())
        db_codes = set(db_products.keys())
        
        print(f"\n📊 Summary:")
        print(f"   • Scraped from website: {len(scraped_codes)} products")
        print(f"   • In database: {len(db_codes)} products")
        print(f"   • In both: {len(scraped_codes & db_codes)} products")
        print(f"   • Only on website: {len(scraped_codes - db_codes)} products")
        print(f"   • Only in database: {len(db_codes - scraped_codes)} products")
        
        if scraped_codes - db_codes:
            print(f"\n❌ Missing from database (found on website):")
            for code in sorted(scraped_codes - db_codes):
                print(f"   • {code}: {products[code]['name'][:50]}...")
        
        if db_codes - scraped_codes:
            print(f"\n⚠️  In database but not found on website:")
            for code in sorted(db_codes - scraped_codes):
                print(f"   • {code}: {db_products[code]['name'][:50]}...")
        
        if scraped_codes & db_codes:
            print(f"\n✅ Confirmed in both:")
            for code in sorted(scraped_codes & db_codes):
                db_subcat = db_products[code]['subcategory']
                status = "✅" if db_subcat == 'Oxford' else f"⚠️ [{db_subcat}]"
                print(f"   {status} {code}: {products[code]['name'][:50]}...")
        
        # Count total variants
        total_variants = sum(max(1, len(p['variants'])) for p in products.values())
        print(f"\n📈 Variant Analysis:")
        print(f"   • Unique products: {len(products)}")
        print(f"   • Total variants (including colors): ~{total_variants}")
        print(f"   • This explains why J.Crew shows more items than unique products")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")

def main():
    """Main function"""
    
    print("="*80)
    print("FRESH SELENIUM OXFORD SCRAPER")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Setup Selenium
    driver, selenium_imports = setup_selenium()
    
    if not driver:
        print("\n❌ Cannot proceed without Selenium/Chrome")
        return
    
    try:
        # Scrape the page
        products = scrape_oxford_page(driver, selenium_imports)
        
        print("\n" + "="*80)
        print("SCRAPING RESULTS")
        print("="*80)
        
        if products:
            print(f"\n✅ Successfully scraped {len(products)} unique products:")
            
            for code, info in sorted(products.items()):
                print(f"\n{code}:")
                print(f"   Name: {info['name'][:60] if info['name'] != 'Unknown' else 'Name not captured'}...")
                if info['url']:
                    print(f"   URL: ...{info['url'][-50:]}")
                if info['variants']:
                    print(f"   Colors: {len(info['variants'])} variants")
            
            # Compare with database
            compare_with_database(products)
            
        else:
            print("\n❌ No products found!")
            print("   The page structure may have changed or we're still being blocked")
        
    finally:
        driver.quit()
        print("\n🔚 Browser closed")

if __name__ == "__main__":
    main()
