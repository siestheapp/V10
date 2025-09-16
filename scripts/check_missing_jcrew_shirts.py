#!/usr/bin/env python3
"""
J.Crew Casual Shirts Missing Products Checker

This script:
1. Scrapes all products from J.Crew Men's Casual Shirts page
2. Handles J.Crew's anti-scraper protection using Selenium
3. Groups products by base product code (ignoring color variants)
4. Checks which products are missing from the database
5. Generates a detailed report of missing products

Based on the existing J.Crew scraping infrastructure in the V10 project.
"""

import re
import json
import sys
import time
import psycopg2
from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging

# Add project root to path
sys.path.append('/Users/seandavey/projects/V10')
from db_config import DB_CONFIG

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

class JCrewShirtsChecker:
    """Check for missing J.Crew casual shirts in the database"""
    
    def __init__(self):
        self.base_url = 'https://www.jcrew.com'
        self.shirts_url = 'https://www.jcrew.com/plp/mens/categories/clothing/shirts'
        self.driver = None
        self.scraped_products = []
        self.db_products = set()
        self.missing_products = []
        
    def setup_driver(self, headless=False):
        """Initialize Selenium driver with anti-detection measures"""
        logger.info("Setting up Chrome driver with anti-detection measures...")
        
        options = Options()
        
        # Anti-detection measures
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Stealth mode user agent
        options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Performance optimizations
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        
        if headless:
            options.add_argument('--headless')
            logger.info("Running in headless mode")
        
        try:
            self.driver = webdriver.Chrome(options=options)
            
            # Execute stealth scripts to avoid detection
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                '''
            })
            
            logger.info("✅ Chrome driver initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Chrome driver: {e}")
            return False
    
    def close_driver(self):
        """Close the Selenium driver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            logger.info("Chrome driver closed")
    
    def scroll_to_load_all_products(self):
        """Scroll down the page to load all products (lazy loading)"""
        logger.info("Scrolling to load all products...")
        
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        max_scrolls = 10
        
        while scroll_attempts < max_scrolls:
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Wait for new content to load
            time.sleep(2)
            
            # Check if new content has loaded
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                # Try clicking "Load More" button if exists
                try:
                    load_more = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Load More') or contains(text(), 'View More')]")
                    load_more.click()
                    time.sleep(2)
                except:
                    break
            
            last_height = new_height
            scroll_attempts += 1
            logger.info(f"  Scroll {scroll_attempts}/{max_scrolls} - Page height: {new_height}px")
    
    def extract_products_from_page(self):
        """Extract all product information from the loaded page"""
        logger.info("Extracting products from page...")
        
        products = {}
        
        try:
            # Wait for products to be visible
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/p/']"))
            )
            
            # Method 1: Find all product links on the page
            all_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/p/']")
            logger.info(f"  Found {len(all_links)} total links")
            
            for link in all_links:
                try:
                    href = link.get_attribute('href')
                    if href and '/p/' in href:
                        # Multiple patterns to extract product codes
                        # Pattern 1: /p/.../PRODUCTCODE or /p/.../PRODUCTCODE?param=value
                        code_match = re.search(r'/([A-Z]{2}\d{3,4})(?:\?|$)', href)
                        if not code_match:
                            # Pattern 2: /p/mens/.../something/PRODUCTCODE
                            code_match = re.search(r'/p/[^/]+/[^/]+/[^/]+/[^/]+/([A-Z0-9]{4,6})(?:\?|$)', href)
                        if not code_match:
                            # Pattern 3: Any alphanumeric code at the end
                            code_match = re.search(r'/([A-Z0-9]{4,6})(?:\?|$)', href)
                        
                        if code_match:
                            product_code = code_match.group(1)
                            
                            # Get parent element for product details
                            parent = link
                            for _ in range(3):  # Go up max 3 levels
                                try:
                                    parent = parent.find_element(By.XPATH, '..')
                                    if parent.tag_name in ['article', 'div', 'li']:
                                        break
                                except:
                                    break
                            
                            # Get product name
                            product_name = ""
                            try:
                                name_elem = parent.find_element(By.CSS_SELECTOR, "h3, h4, .product-name, .product-title, [data-testid*='product-name']")
                                product_name = name_elem.text.strip()
                            except:
                                # Try getting from link text
                                try:
                                    product_name = link.text.strip()
                                except:
                                    pass
                            
                            # Get price
                            price_text = ""
                            try:
                                price_elem = parent.find_element(By.CSS_SELECTOR, ".product-price, [data-testid*='price'], .price")
                                price_text = price_elem.text.strip()
                            except:
                                pass
                            
                            # Store product (using code as key to deduplicate)
                            if product_code not in products:
                                products[product_code] = {
                                    'code': product_code,
                                    'name': product_name,
                                    'url': href.split('?')[0],  # Remove query params
                                    'price': price_text,
                                    'colors': []
                                }
                        
                except Exception as e:
                    continue
            
            # Method 2: Extract from JavaScript data
            try:
                # Look for product data in window objects or scripts
                product_data = self.driver.execute_script("""
                    // Try to find product data in various window objects
                    if (window.__INITIAL_STATE__ && window.__INITIAL_STATE__.products) {
                        return window.__INITIAL_STATE__.products;
                    }
                    if (window.digitalData && window.digitalData.products) {
                        return window.digitalData.products;
                    }
                    // Try to extract from Next.js data
                    if (window.__NEXT_DATA__ && window.__NEXT_DATA__.props) {
                        return window.__NEXT_DATA__.props;
                    }
                    return null;
                """)
                
                if product_data:
                    logger.info("  Found product data in JavaScript")
                    self._extract_from_js_data(product_data, products)
                    
            except Exception as e:
                logger.debug(f"Could not extract JS data: {e}")
            
            # Method 3: Extract from page source with regex
            try:
                page_source = self.driver.page_source
                
                # Look for product codes in various patterns
                patterns = [
                    r'/([A-Z]{2}\d{3,4})(?:\?|")',  # BE123, CM456 patterns
                    r'"productCode"\s*:\s*"([A-Z0-9]{4,6})"',  # JSON productCode
                    r'"sku"\s*:\s*"([A-Z0-9]{4,6})"',  # SKU codes
                    r'/p/[^/]+/[^/]+/[^/]+/[^/]+/([A-Z0-9]{4,6})(?:\?|")',  # Full path pattern
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, page_source, re.IGNORECASE)
                    for code in matches:
                        if code not in products and len(code) >= 4:
                            products[code] = {
                                'code': code,
                                'name': '',
                                'url': f'https://www.jcrew.com/p/mens/categories/clothing/shirts/{code}',
                                'price': '',
                                'colors': []
                            }
                            logger.debug(f"    Found code from regex: {code}")
                
                logger.info(f"  Found {len(products)} products from page source patterns")
                
            except Exception as e:
                logger.debug(f"Could not extract from page source: {e}")
            
        except TimeoutException:
            logger.error("Timeout waiting for products to load")
        except Exception as e:
            logger.error(f"Error extracting products: {e}")
        
        # Convert to list
        self.scraped_products = list(products.values())
        logger.info(f"✅ Extracted {len(self.scraped_products)} unique products")
        
        return self.scraped_products
    
    def _extract_from_js_data(self, data, products):
        """Extract products from JavaScript data object"""
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, dict) and 'productCode' in value:
                    code = value['productCode']
                    if code not in products:
                        products[code] = {
                            'code': code,
                            'name': value.get('name', ''),
                            'url': f"{self.base_url}/p/mens/categories/clothing/shirts/{code}",
                            'price': value.get('price', ''),
                            'colors': value.get('colors', [])
                        }
                elif isinstance(value, (dict, list)):
                    self._extract_from_js_data(value, products)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    self._extract_from_js_data(item, products)
    
    def get_database_products(self):
        """Get all J.Crew product codes from the database"""
        logger.info("Checking database for existing J.Crew products...")
        
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor()
            
            product_codes = set()
            
            # Check jcrew_product_cache table
            logger.info("  Checking jcrew_product_cache table...")
            try:
                cur.execute("""
                    SELECT DISTINCT product_code 
                    FROM jcrew_product_cache 
                    WHERE product_code IS NOT NULL
                """)
                cache_codes = cur.fetchall()
                for (code,) in cache_codes:
                    if code:
                        product_codes.add(code.upper())
                logger.info(f"    Found {len(cache_codes)} products in cache")
            except psycopg2.Error as e:
                logger.warning(f"    Could not access jcrew_product_cache: {e}")
            
            # Check product_master table
            logger.info("  Checking product_master table...")
            try:
                cur.execute("""
                    SELECT DISTINCT pm.product_code 
                    FROM product_master pm 
                    JOIN brands b ON pm.brand_id = b.id 
                    WHERE b.id = 4  -- J.Crew brand ID
                    AND pm.product_code IS NOT NULL
                """)
                master_codes = cur.fetchall()
                for (code,) in master_codes:
                    if code:
                        product_codes.add(code.upper())
                logger.info(f"    Found {len(master_codes)} J.Crew products in product_master")
            except psycopg2.Error as e:
                logger.warning(f"    Could not access product_master: {e}")
            
            # Check garments table
            logger.info("  Checking garments table...")
            try:
                cur.execute("""
                    SELECT DISTINCT product_code 
                    FROM garments 
                    WHERE brand_id = 4  -- J.Crew brand ID
                    AND product_code IS NOT NULL
                """)
                garment_codes = cur.fetchall()
                for (code,) in garment_codes:
                    if code:
                        product_codes.add(code.upper())
                logger.info(f"    Found {len(garment_codes)} J.Crew products in garments")
            except psycopg2.Error as e:
                logger.warning(f"    Could not access garments table: {e}")
            
            cur.close()
            conn.close()
            
            self.db_products = product_codes
            logger.info(f"✅ Total unique J.Crew products in database: {len(product_codes)}")
            
            return product_codes
            
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            return set()
    
    def analyze_missing_products(self):
        """Analyze which products are missing from the database"""
        logger.info("Analyzing missing products...")
        
        scraped_codes = {p['code'].upper() for p in self.scraped_products}
        missing_codes = scraped_codes - self.db_products
        existing_codes = scraped_codes & self.db_products
        
        # Categorize missing products by type
        categories = defaultdict(list)
        
        for product in self.scraped_products:
            code = product['code'].upper()
            if code in missing_codes:
                name_lower = product['name'].lower()
                
                # Categorize by product type
                if 'oxford' in name_lower:
                    category = 'Oxford Shirts'
                elif 'secret wash' in name_lower:
                    category = 'Secret Wash'
                elif 'corduroy' in name_lower:
                    category = 'Corduroy'
                elif 'linen' in name_lower:
                    category = 'Linen'
                elif 'flannel' in name_lower:
                    category = 'Flannel'
                elif 'performance' in name_lower or 'bowery' in name_lower:
                    category = 'Performance'
                elif 'casual' in name_lower or 'shirt' in name_lower:
                    category = 'Casual Shirts'
                else:
                    category = 'Other'
                
                categories[category].append(product)
        
        self.missing_products = {
            'total_scraped': len(self.scraped_products),
            'total_in_db': len(existing_codes),
            'total_missing': len(missing_codes),
            'missing_codes': sorted(missing_codes),
            'existing_codes': sorted(existing_codes),
            'categories': dict(categories),
            'missing_products_list': [p for p in self.scraped_products if p['code'].upper() in missing_codes]
        }
        
        return self.missing_products
    
    def generate_report(self):
        """Generate a detailed report of missing products"""
        analysis = self.missing_products
        
        print("\n" + "="*80)
        print("J.CREW CASUAL SHIRTS - MISSING PRODUCTS REPORT")
        print("="*80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total products on website:       {analysis['total_scraped']}")
        print(f"   Products already in database:    {analysis['total_in_db']}")
        print(f"   Products MISSING from database:  {analysis['total_missing']}")
        
        if analysis['total_scraped'] > 0:
            coverage = (analysis['total_in_db'] / analysis['total_scraped'] * 100)
            print(f"   Database coverage:               {coverage:.1f}%")
        
        print(f"\n🔍 MISSING PRODUCTS BY CATEGORY:")
        for category, products in analysis['categories'].items():
            print(f"   {category:20} {len(products):3} products")
        
        print(f"\n❌ MISSING PRODUCT DETAILS:")
        for category, products in analysis['categories'].items():
            if products:
                print(f"\n   {category}:")
                for product in products[:3]:  # Show first 3 per category
                    print(f"     • {product['code']} - {product['name']}")
                    print(f"       URL: {product['url']}")
                if len(products) > 3:
                    print(f"     ... and {len(products) - 3} more")
        
        print(f"\n📋 ALL MISSING PRODUCT CODES:")
        codes = analysis['missing_codes']
        for i in range(0, len(codes), 10):
            line_codes = codes[i:i+10]
            print(f"   {' '.join(line_codes)}")
        
        print("\n" + "="*80)
        
        # Save to JSON file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"jcrew_missing_shirts_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: {output_file}")
        print(f"   This file contains all missing products with full details")
        
        return output_file
    
    def run(self, headless=False):
        """Main execution method"""
        logger.info("Starting J.Crew Casual Shirts Missing Products Check")
        logger.info("="*60)
        
        try:
            # Setup driver
            if not self.setup_driver(headless=headless):
                return False
            
            # Load the page
            logger.info(f"Loading page: {self.shirts_url}")
            self.driver.get(self.shirts_url)
            time.sleep(3)  # Initial load time
            
            # Scroll to load all products
            self.scroll_to_load_all_products()
            
            # Extract products
            self.extract_products_from_page()
            
            if not self.scraped_products:
                logger.error("No products found on the page")
                return False
            
            # Get database products
            self.get_database_products()
            
            # Analyze missing products
            self.analyze_missing_products()
            
            # Generate report
            output_file = self.generate_report()
            
            logger.info(f"✅ Analysis complete! Missing products: {self.missing_products['total_missing']}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error during execution: {e}")
            return False
            
        finally:
            self.close_driver()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Check for missing J.Crew casual shirts')
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    parser.add_argument('--test', action='store_true', help='Test database connection only')
    
    args = parser.parse_args()
    
    if args.test:
        # Test database connection
        print("Testing database connection...")
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM jcrew_product_cache")
            count = cur.fetchone()[0]
            cur.close()
            conn.close()
            print(f"✅ Database connection successful. Found {count} products in cache.")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
        return
    
    # Run the checker
    checker = JCrewShirtsChecker()
    success = checker.run(headless=args.headless)
    
    if success:
        print("\n✅ Check completed successfully!")
    else:
        print("\n❌ Check failed. Please check the logs above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
