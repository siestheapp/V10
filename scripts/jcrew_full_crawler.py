#!/usr/bin/env python3
"""
Complete J.Crew Product Discovery and Fit Extraction Crawler
Discovers products from category pages and extracts fit options
"""

import sys
import time
import logging
import json
from datetime import datetime
from typing import List, Dict, Set, Optional
import re

sys.path.append('/Users/seandavey/projects/V10')

import psycopg2
from psycopg2.extras import RealDictCursor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from db_config import DB_CONFIG

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class JCrewFullCrawler:
    """
    Complete J.Crew crawler that discovers products and extracts fit options
    """
    
    # J.Crew men's category URLs to crawl (using working /plp/ structure)
    CATEGORY_URLS = [
        # Main shirts page
        'https://www.jcrew.com/plp/mens/categories/clothing/shirts',
        
        # Specific shirt types
        'https://www.jcrew.com/plp/mens/categories/clothing/shirts/secret-wash',
        'https://www.jcrew.com/plp/mens/categories/clothing/shirts/broken-in-oxford',
        'https://www.jcrew.com/plp/mens/categories/clothing/shirts/linen',
        'https://www.jcrew.com/plp/mens/categories/clothing/shirts/chambray-and-denim-shirts',
        
        # Dress shirts
        'https://www.jcrew.com/plp/mens/categories/clothing/dress-shirts',
        
        # T-Shirts & Polos
        'https://www.jcrew.com/plp/mens/categories/clothing/t-shirts-and-polos',
        'https://www.jcrew.com/plp/mens/categories/clothing/polos',
        
        # Sweaters
        'https://www.jcrew.com/plp/mens/categories/clothing/sweaters',
    ]
    
    def __init__(self, headless: bool = True, max_products: int = None):
        """
        Initialize the crawler
        
        Args:
            headless: Run browser in headless mode
            max_products: Maximum number of products to process (None for unlimited)
        """
        self.headless = headless
        self.max_products = max_products
        self.driver = None
        self.discovered_products = {}
        self.processed_count = 0
        self._setup_driver()
    
    def _setup_driver(self):
        """Setup Selenium WebDriver"""
        options = webdriver.ChromeOptions()
        
        if self.headless:
            options.add_argument('--headless=new')
        
        # Anti-detection settings
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        
        self.driver = webdriver.Chrome(options=options)
        
        # Anti-detection JavaScript
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            '''
        })
    
    def discover_products_from_category(self, category_url: str) -> List[Dict]:
        """
        Discover all products from a category page
        
        Returns:
            List of product dictionaries with url, name, and code
        """
        products = []
        
        try:
            logger.info(f"📂 Browsing category: {category_url}")
            self.driver.get(category_url)
            
            # Wait for products to load
            wait = WebDriverWait(self.driver, 15)
            
            # Wait specifically for product elements
            try:
                wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href*="/p/"], [data-testid*="product"], .product-tile'))
                )
            except TimeoutException:
                logger.warning(f"   No products found on page after waiting")
            
            time.sleep(5)  # Let dynamic content fully load
            
            # Scroll to load more products (J.Crew uses lazy loading)
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_attempts = 0
            max_scrolls = 5
            
            while scroll_attempts < max_scrolls:
                # Scroll down
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Check if new content loaded
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                scroll_attempts += 1
            
            # Extract product links - try multiple strategies
            product_links = []
            
            # Strategy 1: Direct product links (both /p/ and /m/ patterns)
            product_links.extend(self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/p/mens/"], a[href*="/m/mens/"]'))
            
            # Strategy 2: Product cards/tiles
            product_cards = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid*="product"], .product-tile, article')
            for card in product_cards:
                links = card.find_elements(By.TAG_NAME, 'a')
                product_links.extend(links)
            
            # Strategy 3: Any link with /p/ or /m/ pattern
            if not product_links:
                product_links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/p/"], a[href*="/m/"]')
            
            logger.info(f"   Found {len(product_links)} potential product links")
            
            for link in product_links:
                href = link.get_attribute('href')
                if not href or ('/p/' not in href and '/m/' not in href):
                    continue
                
                # Extract product code from URL - be more flexible with patterns
                # Try multiple patterns for both /p/ and /m/ URLs
                patterns = [
                    r'/p/[^/]+/([A-Z0-9]+)(?:\?|$)',  # /p/category/CODE
                    r'/p/([A-Z0-9]+)(?:\?|$)',         # /p/CODE
                    r'/m/[^/]+/([A-Z0-9]+)(?:\?|$)',  # /m/category/CODE
                    r'/m/.*/([A-Z0-9]+)(?:\?|$)',     # /m/.../CODE (flexible path)
                    r'/([A-Z0-9]{2,8})(?:\?|$)'        # /CODE (more flexible length)
                ]
                
                product_code = None
                for pattern in patterns:
                    match = re.search(pattern, href)
                    if match:
                        product_code = match.group(1)
                        break
                
                if product_code:
                    
                    # Get product name from link text or aria-label
                    product_name = link.get_attribute('aria-label') or link.text
                    if not product_name:
                        # Try to find product name in parent element
                        try:
                            parent = link.find_element(By.XPATH, '..')
                            product_name = parent.text.split('\n')[0]
                        except:
                            product_name = product_code
                    
                    # Clean the URL (remove query parameters)
                    clean_url = href.split('?')[0]
                    
                    product = {
                        'url': clean_url,
                        'code': product_code,
                        'name': product_name.strip()[:100] if product_name else product_code
                    }
                    
                    # Avoid duplicates
                    if product_code not in self.discovered_products:
                        products.append(product)
                        self.discovered_products[product_code] = product
            
            logger.info(f"   Found {len(products)} products in this category")
            
        except Exception as e:
            logger.error(f"Error discovering products from {category_url}: {e}")
        
        return products
    
    def extract_product_details(self, product_url: str, product_code: str) -> Dict:
        """
        Extract detailed information from a product page including fit options
        
        Returns:
            Dictionary with all product details
        """
        try:
            logger.info(f"🔍 Extracting details for {product_code}")
            self.driver.get(product_url)
            
            # Wait for page to load
            wait = WebDriverWait(self.driver, 10)
            time.sleep(2)
            
            # Extract product name
            try:
                name_elem = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="pdp-product-title"], h1')
                product_name = name_elem.text.strip()
            except:
                product_name = product_code
            
            # Extract price
            price = None
            try:
                price_elem = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="pdp-product-price"], [class*="price"]')
                price_text = price_elem.text
                # Extract numeric price
                match = re.search(r'[\d,]+\.?\d*', price_text.replace('$', ''))
                if match:
                    price = float(match.group().replace(',', ''))
            except:
                pass
            
            # Extract fit options using our proven method
            fit_options = self._extract_fit_options()
            
            # Extract available sizes
            sizes = []
            try:
                size_buttons = self.driver.find_elements(By.CSS_SELECTOR, 'button[aria-label*="size"]')
                for button in size_buttons:
                    size_text = button.get_attribute('aria-label') or button.text
                    if size_text and 'size' in size_text.lower():
                        # Extract the actual size (S, M, L, etc.)
                        size = size_text.replace('Select size', '').strip()
                        if size and len(size) < 10:  # Reasonable size length
                            sizes.append(size)
            except:
                pass
            
            # Extract colors
            colors = []
            try:
                color_buttons = self.driver.find_elements(By.CSS_SELECTOR, 'button[aria-label*="color"]')
                for button in color_buttons:
                    color = button.get_attribute('aria-label')
                    if color and 'color' in color.lower():
                        color = color.replace('Select color', '').strip()
                        if color:
                            colors.append(color)
            except:
                pass
            
            # Extract description
            description = ""
            try:
                desc_elem = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="product-description"], [class*="description"]')
                description = desc_elem.text.strip()[:500]
            except:
                pass
            
            # Extract main image
            image_url = ""
            try:
                img_elem = self.driver.find_element(By.CSS_SELECTOR, 'img[data-testid="pdp-product-image"], img[class*="hero"], img[alt*="' + product_code + '"]')
                image_url = img_elem.get_attribute('src')
            except:
                pass
            
            return {
                'product_code': product_code,
                'product_name': product_name,
                'product_url': product_url,
                'price': price,
                'fit_options': fit_options,
                'sizes': sizes,
                'colors': colors,
                'description': description,
                'image_url': image_url,
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error extracting details for {product_code}: {e}")
            return {
                'product_code': product_code,
                'product_url': product_url,
                'error': str(e)
            }
    
    def _extract_fit_options(self) -> Optional[List[str]]:
        """
        Extract fit options from the current product page
        """
        fit_options = []
        
        try:
            # Look for the Fit List structure
            fit_list = self.driver.find_element(By.CSS_SELECTOR, 'ul[aria-label="Fit List"]')
            if fit_list:
                buttons = fit_list.find_elements(By.CSS_SELECTOR, 'button')
                for button in buttons:
                    fit_name = button.get_attribute('aria-label') or button.text
                    if fit_name:
                        # Clean the fit name
                        fit_name = fit_name.strip()
                        fit_name = fit_name.replace(', selected', '').replace(' selected', '')
                        fit_name = fit_name.replace(', is unavailable', '').replace(' unavailable', '')
                        if fit_name and fit_name not in fit_options:
                            fit_options.append(fit_name)
                
                if fit_options:
                    logger.info(f"   ✅ Found fits: {fit_options}")
                    return fit_options
        except:
            pass
        
        # Alternative: Look for fit buttons with specific IDs
        try:
            fit_buttons = self.driver.find_elements(By.CSS_SELECTOR, 'button[id$="__fit-button"]')
            for button in fit_buttons:
                button_id = button.get_attribute('id')
                if button_id and '__fit-button' in button_id:
                    fit_name = button_id.replace('__fit-button', '')
                    if fit_name and fit_name not in fit_options:
                        fit_options.append(fit_name)
            
            if fit_options:
                logger.info(f"   ✅ Found fits: {fit_options}")
                return fit_options
        except:
            pass
        
        logger.info(f"   ⚠️ No fit options (single fit product)")
        return None
    
    def save_to_database(self, product_data: Dict):
        """
        Save or update product in database
        """
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cur = conn.cursor()
        
        try:
            # Check if product exists
            cur.execute("""
                SELECT product_code FROM jcrew_product_cache 
                WHERE product_code = %s
            """, (product_data['product_code'],))
            
            exists = cur.fetchone()
            
            if exists:
                # Update existing product
                cur.execute("""
                    UPDATE jcrew_product_cache SET
                        product_name = %s,
                        product_url = %s,
                        price = %s,
                        fit_options = %s,
                        updated_at = NOW()
                    WHERE product_code = %s
                """, (
                    product_data.get('product_name'),
                    product_data.get('product_url'),
                    product_data.get('price'),
                    product_data.get('fit_options'),
                    product_data['product_code']
                ))
                logger.info(f"   💾 Updated {product_data['product_code']} in database")
            else:
                # Insert new product
                cur.execute("""
                    INSERT INTO jcrew_product_cache (
                        product_code, product_name, product_url, price,
                        fit_options, created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
                """, (
                    product_data['product_code'],
                    product_data.get('product_name'),
                    product_data.get('product_url'),
                    product_data.get('price'),
                    product_data.get('fit_options')
                ))
                logger.info(f"   💾 Saved new product {product_data['product_code']} to database")
            
        except Exception as e:
            logger.error(f"Database error: {e}")
        finally:
            cur.close()
            conn.close()
    
    def crawl(self, categories: List[str] = None):
        """
        Main crawl function that discovers and processes products
        
        Args:
            categories: List of category URLs to crawl (uses defaults if None)
        """
        if categories is None:
            categories = self.CATEGORY_URLS
        
        logger.info("="*70)
        logger.info("🚀 Starting J.Crew Full Crawler")
        logger.info(f"   Categories to crawl: {len(categories)}")
        logger.info(f"   Max products: {self.max_products or 'Unlimited'}")
        logger.info("="*70)
        
        all_products = []
        
        # Phase 1: Discover products from category pages
        logger.info("\n📋 PHASE 1: Product Discovery")
        logger.info("-"*40)
        
        for category_url in categories:
            if self.max_products and self.processed_count >= self.max_products:
                break
            
            products = self.discover_products_from_category(category_url)
            all_products.extend(products)
            
            # Rate limiting
            time.sleep(2)
            
            if self.max_products and len(all_products) >= self.max_products:
                all_products = all_products[:self.max_products]
                break
        
        logger.info(f"\n✅ Discovered {len(all_products)} unique products")
        
        # Phase 2: Extract details from each product
        logger.info("\n📋 PHASE 2: Product Detail Extraction")
        logger.info("-"*40)
        
        for idx, product in enumerate(all_products, 1):
            logger.info(f"\n[{idx}/{len(all_products)}] {product['code']}: {product['name'][:50]}")
            
            # Extract product details
            details = self.extract_product_details(product['url'], product['code'])
            
            # Save to database
            if not details.get('error'):
                self.save_to_database(details)
                self.processed_count += 1
            
            # Rate limiting
            time.sleep(2)
            
            # Progress update
            if idx % 10 == 0:
                logger.info(f"\n📊 Progress: {idx}/{len(all_products)} products processed")
        
        logger.info("\n" + "="*70)
        logger.info("✅ Crawl Complete!")
        logger.info(f"   Products discovered: {len(all_products)}")
        logger.info(f"   Products processed: {self.processed_count}")
        logger.info("="*70)
    
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
            logger.info("Driver closed")

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='J.Crew Full Product Crawler')
    parser.add_argument('--categories', nargs='+', help='Category URLs to crawl')
    parser.add_argument('--max-products', type=int, help='Maximum products to process')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    
    args = parser.parse_args()
    
    # Initialize crawler
    crawler = JCrewFullCrawler(
        headless=args.headless,
        max_products=args.max_products
    )
    
    try:
        # Run the crawl
        crawler.crawl(categories=args.categories)
    finally:
        crawler.cleanup()

if __name__ == "__main__":
    main()
