#!/usr/bin/env python3
"""
Find remaining dress shirt product codes by deep analysis of the page
"""

import re
import sys
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime

# Add project root to path
sys.path.append('/Users/seandavey/projects/V10')
import psycopg2
from db_config import DB_CONFIG

def setup_driver():
    """Setup Chrome driver with anti-detection"""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
    
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def extract_from_product_grid(driver):
    """Extract product codes from the product grid"""
    products = {}
    
    # Look for product grid items
    selectors = [
        'article[data-testid*="product"]',
        'div[class*="product-tile"]',
        'div[class*="product-card"]',
        'li[class*="product"]',
        'a[class*="product-link"]'
    ]
    
    for selector in selectors:
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        print(f"  Found {len(elements)} elements with selector: {selector}")
        
        for elem in elements:
            try:
                # Look for links within the element
                links = elem.find_elements(By.TAG_NAME, 'a')
                for link in links:
                    href = link.get_attribute('href')
                    if href and '/p/' in href:
                        # Extract product code
                        matches = re.findall(r'/([A-Z]{2}\d{3,4})(?:\?|/|$)', href)
                        for code in matches:
                            if code not in products:
                                # Try to get product name
                                name = ""
                                for name_sel in ['h3', 'h4', '.product-name', '[class*="product-title"]']:
                                    try:
                                        name_elem = elem.find_element(By.CSS_SELECTOR, name_sel)
                                        name = name_elem.text.strip()
                                        if name:
                                            break
                                    except:
                                        continue
                                
                                products[code] = {
                                    'code': code,
                                    'name': name or f"Dress Shirt {code}",
                                    'url': href.split('?')[0]
                                }
            except:
                continue
    
    return products

def main():
    print("="*60)
    print("FINDING REMAINING DRESS SHIRTS")
    print("="*60)
    
    driver = setup_driver()
    
    try:
        # Load the dress shirts page
        url = 'https://www.jcrew.com/plp/mens/categories/clothing/dress-shirts'
        print(f"Loading: {url}")
        driver.get(url)
        time.sleep(5)
        
        # Scroll to load all products
        print("Scrolling to load all products...")
        for _ in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
        
        # Extract from product grid
        print("Extracting from product grid...")
        products = extract_from_product_grid(driver)
        
        # Also extract from any Quick Shop buttons/links
        quick_shop_links = driver.find_elements(By.CSS_SELECTOR, '[data-testid*="quick-shop"], button[class*="quick-shop"]')
        print(f"Found {len(quick_shop_links)} Quick Shop elements")
        
        # Look for data attributes with product codes
        all_elements = driver.find_elements(By.XPATH, '//*[@*[contains(., \"BM\") or contains(., \"CA\") or contains(., \"CD\") or contains(., \"CP\") or contains(., \"BG\") or contains(., \"BW\")]]')
        print(f"Found {len(all_elements)} elements with potential product codes")
        
        for elem in all_elements[:100]:  # Check first 100 to avoid too many
            for attr in elem.get_property('attributes'):
                try:
                    attr_name = attr.get('name', '')
                    attr_value = attr.get('value', '')
                    
                    # Look for product codes in attribute values
                    matches = re.findall(r'\b([A-Z]{2}\d{3,4})\b', attr_value)
                    for code in matches:
                        if code not in products and not code.startswith(('WT', 'WX', 'WZ', 'YD', 'FF')):
                            products[code] = {
                                'code': code,
                                'name': f"Dress Shirt {code}",
                                'url': f"https://www.jcrew.com/p/{code}"
                            }
                except:
                    continue
        
        # Filter valid product codes
        valid_pattern = re.compile(r'^[A-Z]{2}\d{3,4}$')
        valid_products = {
            code: info for code, info in products.items() 
            if valid_pattern.match(code) and not code.startswith(('WT', 'WX', 'WZ', 'YD', 'FF'))
        }
        
        print(f"\n✅ Found {len(valid_products)} potential dress shirt codes")
        
        # Check database
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        cur.execute("SELECT DISTINCT UPPER(product_code) FROM jcrew_product_cache WHERE product_code IS NOT NULL")
        existing = {row[0] for row in cur.fetchall()}
        
        cur.close()
        conn.close()
        
        # Find missing
        missing = set(valid_products.keys()) - existing
        
        if missing:
            print(f"\n📋 ADDITIONAL MISSING CODES ({len(missing)}):")
            sorted_missing = sorted(missing)
            for code in sorted_missing:
                print(f"  {code} - {valid_products[code]['name'][:50]}")
            
            # Save for fetching
            with open(f"additional_dress_shirts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", 'w') as f:
                for code in sorted_missing:
                    f.write(f"{code}\n")
        else:
            print("\n✅ No additional missing dress shirts found")
            
    finally:
        driver.quit()

if __name__ == "__main__":
    main()

