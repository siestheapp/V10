#!/usr/bin/env python3
"""
Comprehensive J.Crew Men's Dress Shirts Extractor
Designed to extract ALL dress shirt product codes from the page
"""

import re
import sys
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime

# Add project root to path
sys.path.append('/Users/seandavey/projects/V10')
import psycopg2
from db_config import DB_CONFIG

class DressShirtExtractor:
    def __init__(self):
        """Initialize the dress shirt extractor"""
        self.driver = None
        self.products = {}
        
    def setup_driver(self):
        """Setup Chrome driver with anti-detection measures"""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        
        self.driver = webdriver.Chrome(options=options)
        
        # Remove webdriver property
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def extract_from_product_links(self):
        """Extract product codes from all product links"""
        print("🔍 Extracting from product links...")
        
        # Find all links that match J.Crew product URL patterns
        product_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/p/']")
        
        for link in product_links:
            try:
                href = link.get_attribute('href')
                if not href:
                    continue
                    
                # Multiple patterns to extract product codes
                # Pattern 1: Standard product URL ending with product code
                match = re.search(r'/([A-Z]{2}\d{3,4})(?:\?|$)', href)
                if not match:
                    # Pattern 2: Product code in middle of URL
                    match = re.search(r'/p/[^/]+/[^/]+/[^/]+/[^/]+/([A-Z]{2}\d{3,4})(?:\?|/|$)', href)
                if not match:
                    # Pattern 3: Direct /p/CODE pattern
                    match = re.search(r'/p/([A-Z]{2}\d{3,4})(?:\?|/|$)', href)
                    
                if match:
                    code = match.group(1)
                    
                    # Get product name from parent element
                    name = ""
                    try:
                        parent = link
                        for _ in range(4):
                            parent = parent.find_element(By.XPATH, '..')
                            # Look for product name in various elements
                            for selector in ['h3', 'h4', '.product-tile__name', '[data-testid*="product-name"]']:
                                try:
                                    name_elem = parent.find_element(By.CSS_SELECTOR, selector)
                                    name = name_elem.text.strip()
                                    if name:
                                        break
                                except:
                                    continue
                            if name:
                                break
                    except:
                        pass
                    
                    if not name:
                        name = link.text.strip() if link.text else f"Product {code}"
                    
                    if code not in self.products:
                        self.products[code] = {
                            'code': code,
                            'name': name,
                            'url': href.split('?')[0]
                        }
                        
            except Exception as e:
                continue
                
        print(f"  Found {len(self.products)} products from links")
        
    def extract_from_javascript(self):
        """Extract product data from embedded JavaScript"""
        print("🔍 Extracting from JavaScript data...")
        
        try:
            # Look for JSON-LD product data
            scripts = self.driver.find_elements(By.CSS_SELECTOR, 'script[type="application/ld+json"]')
            for script in scripts:
                try:
                    data = json.loads(script.get_attribute('innerHTML'))
                    
                    # Handle different JSON structures
                    if isinstance(data, list):
                        items = data
                    elif isinstance(data, dict) and '@graph' in data:
                        items = data['@graph']
                    else:
                        items = [data]
                    
                    for item in items:
                        if item.get('@type') == 'Product' or 'Product' in str(item.get('@type', [])):
                            # Extract SKU/product code
                            sku = item.get('sku', '')
                            if sku and re.match(r'^[A-Z]{2}\d{3,4}$', sku):
                                name = item.get('name', f'Product {sku}')
                                if sku not in self.products:
                                    self.products[sku] = {
                                        'code': sku,
                                        'name': name,
                                        'url': item.get('url', '')
                                    }
                except:
                    continue
                    
        except Exception as e:
            print(f"  Error extracting JavaScript data: {e}")
            
    def extract_from_data_attributes(self):
        """Extract product codes from data attributes"""
        print("🔍 Extracting from data attributes...")
        
        # Look for elements with data attributes containing product codes
        selectors = [
            '[data-product-id]',
            '[data-product-code]',
            '[data-sku]',
            '[data-item-id]',
            '[data-testid*="product"]'
        ]
        
        for selector in selectors:
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            for elem in elements:
                for attr in ['data-product-id', 'data-product-code', 'data-sku', 'data-item-id']:
                    try:
                        value = elem.get_attribute(attr)
                        if value and re.match(r'^[A-Z]{2}\d{3,4}$', value):
                            if value not in self.products:
                                # Try to get product name
                                name = ""
                                for name_sel in ['h3', 'h4', '.product-name']:
                                    try:
                                        name_elem = elem.find_element(By.CSS_SELECTOR, name_sel)
                                        name = name_elem.text.strip()
                                        if name:
                                            break
                                    except:
                                        continue
                                        
                                self.products[value] = {
                                    'code': value,
                                    'name': name or f"Product {value}",
                                    'url': ''
                                }
                    except:
                        continue
                        
    def scroll_and_load_all(self):
        """Scroll to load all products"""
        print("📜 Scrolling to load all products...")
        
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        max_scrolls = 10
        
        while scroll_attempts < max_scrolls:
            # Scroll down
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Check for "Load More" button
            try:
                load_more = self.driver.find_element(By.CSS_SELECTOR, 'button[data-testid="load-more"], button:contains("Load More"), button:contains("Show More")')
                if load_more.is_displayed() and load_more.is_enabled():
                    self.driver.execute_script("arguments[0].click();", load_more)
                    print("  Clicked Load More button")
                    time.sleep(3)
            except:
                pass
            
            # Check if more content loaded
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
                
            last_height = new_height
            scroll_attempts += 1
            
        print(f"  Scrolled {scroll_attempts} times")
        
    def extract_all_dress_shirts(self, url):
        """Main extraction method"""
        print(f"\n🌐 Loading: {url}")
        self.driver.get(url)
        time.sleep(5)  # Initial load
        
        # Scroll to load all products
        self.scroll_and_load_all()
        
        # Extract from multiple sources
        self.extract_from_product_links()
        self.extract_from_javascript()
        self.extract_from_data_attributes()
        
        # Also try regex on page source as fallback
        print("🔍 Final regex extraction from page source...")
        page_source = self.driver.page_source
        
        # Find all potential product codes in page
        code_matches = re.findall(r'\b([A-Z]{2}\d{3,4})\b', page_source)
        for code in set(code_matches):
            if code not in self.products:
                # Verify it's likely a product code by checking context
                if f'"/p/' in page_source and code in page_source:
                    self.products[code] = {
                        'code': code,
                        'name': f"Dress Shirt {code}",
                        'url': f"https://www.jcrew.com/p/{code}"
                    }
        
        return self.products
        
    def close(self):
        """Close the driver"""
        if self.driver:
            self.driver.quit()

def main():
    print("="*60)
    print("J.CREW MEN'S DRESS SHIRTS - COMPREHENSIVE EXTRACTION")
    print("="*60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize extractor
    extractor = DressShirtExtractor()
    extractor.setup_driver()
    
    try:
        # Extract all dress shirts
        dress_shirts_url = 'https://www.jcrew.com/plp/mens/categories/clothing/dress-shirts'
        products = extractor.extract_all_dress_shirts(dress_shirts_url)
        
        print(f"\n✅ Total unique products found: {len(products)}")
        
        # Filter for valid J.Crew product codes
        valid_products = {
            code: info for code, info in products.items() 
            if re.match(r'^[A-Z]{2}\d{3,4}$', code)
        }
        
        print(f"✅ Valid J.Crew product codes: {len(valid_products)}")
        
        # Get existing products from database
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT DISTINCT UPPER(product_code) 
            FROM jcrew_product_cache 
            WHERE product_code IS NOT NULL
        """)
        existing = {row[0] for row in cur.fetchall()}
        
        # Also check specifically for dress shirts
        cur.execute("""
            SELECT product_code, product_name 
            FROM jcrew_product_cache 
            WHERE LOWER(product_name) LIKE '%dress shirt%'
               OR LOWER(product_name) LIKE '%bowery%'
               OR LOWER(product_name) LIKE '%ludlow%'
               OR LOWER(product_name) LIKE '%thomas mason%'
               OR LOWER(product_name) LIKE '%portuguese cotton oxford dress%'
        """)
        dress_shirts_in_db = {row[0] for row in cur.fetchall()}
        
        cur.close()
        conn.close()
        
        # Find missing products
        missing = set(valid_products.keys()) - existing
        
        print("\n" + "="*60)
        print("ANALYSIS RESULTS")
        print("="*60)
        print(f"Dress shirts found on page:     {len(valid_products)}")
        print(f"Total products in database:     {len(existing)}")
        print(f"Dress shirts in database:       {len(dress_shirts_in_db)}")
        print(f"Missing dress shirts:           {len(missing)}")
        
        if missing:
            print(f"\n📋 MISSING DRESS SHIRT CODES ({len(missing)}):")
            sorted_missing = sorted(missing)
            
            # Print in rows of 8
            for i in range(0, len(sorted_missing), 8):
                print("  " + " ".join(sorted_missing[i:i+8]))
            
            # Save to file
            output_file = f"missing_dress_shirts_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w') as f:
                json.dump({
                    'missing_codes': sorted_missing,
                    'missing_products': {code: valid_products[code] for code in sorted_missing},
                    'total_missing': len(missing),
                    'extraction_time': datetime.now().isoformat()
                }, f, indent=2)
            
            print(f"\n💾 Saved missing products to: {output_file}")
            
            # Also save just codes for easy fetching
            codes_file = f"dress_shirt_codes_to_fetch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(codes_file, 'w') as f:
                for code in sorted_missing:
                    f.write(f"{code}\n")
            print(f"💾 Saved codes list to: {codes_file}")
            
        else:
            print("\n✅ All dress shirts are already in the database!")
            
    finally:
        extractor.close()
        
    print("\n" + "="*60)

if __name__ == "__main__":
    main()

