#!/usr/bin/env python3
"""
J.Crew Fit Options Crawler - Accurate extraction of product fit variations
Visits each product page individually and extracts ONLY the fits available for purchase
"""

import sys
import json
import time
import logging
from datetime import datetime
from typing import List, Optional, Dict, Tuple

# Add project root to path
sys.path.append('/Users/seandavey/projects/V10')

import psycopg2
from psycopg2.extras import RealDictCursor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from db_config import DB_CONFIG

# Use the standard database config but with adjusted settings
# For admin operations, we should use a direct connection when available

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class JCrewFitCrawler:
    """
    Crawler specifically designed to extract fit options from J.Crew product pages
    """
    
    def __init__(self, headless: bool = False, timeout: int = 10):
        """
        Initialize the crawler with Selenium WebDriver
        
        Args:
            headless: Run browser in headless mode
            timeout: Default timeout for page loads and element waits
        """
        self.timeout = timeout
        self.driver = None
        self.headless = headless
        self.stats = {
            'total_products': 0,
            'products_with_fits': 0,
            'products_without_fits': 0,
            'errors': 0,
            'updated': 0
        }
        self._setup_driver()
    
    def _setup_driver(self):
        """Setup Selenium WebDriver with anti-detection measures"""
        options = webdriver.ChromeOptions()
        
        # Headless mode option
        if self.headless:
            options.add_argument('--headless=new')
        
        # Anti-detection settings
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Performance and stability
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        # User agent to look more like a real browser
        options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Page load strategy
        options.page_load_strategy = 'normal'
        
        self.driver = webdriver.Chrome(options=options)
        
        # Additional anti-detection JavaScript
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            '''
        })
    
    def extract_fit_options(self, product_url: str, product_code: str) -> Optional[List[str]]:
        """
        Extract fit options from a single product page by inspecting HTML source
        
        Args:
            product_url: URL of the product page
            product_code: Product code for logging
            
        Returns:
            List of fit options or None if no fits found
        """
        try:
            logger.info(f"Processing {product_code}: {product_url}")
            
            # Load the product page
            self.driver.get(product_url)
            
            # Wait for page to be interactive
            wait = WebDriverWait(self.driver, self.timeout)
            
            # Wait for product content to load (multiple possible indicators)
            try:
                wait.until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="pdp-product-title"]')),
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'h1[class*="product"]')),
                        EC.presence_of_element_located((By.CSS_SELECTOR, '.product-name')),
                        EC.presence_of_element_located((By.TAG_NAME, 'h1'))
                    )
                )
            except TimeoutException:
                logger.warning(f"Timeout waiting for page load: {product_code}")
                return None
            
            # Small delay to ensure dynamic content loads
            time.sleep(2)
            
            # Extract fit options by inspecting the HTML source directly
            fit_options = self._extract_fits_from_html_source()
            
            if fit_options:
                logger.info(f"✅ {product_code}: {fit_options}")
                return fit_options
            else:
                logger.info(f"⚠️ {product_code}: No fit options (single fit product)")
                return None
                
        except WebDriverException as e:
            logger.error(f"WebDriver error for {product_code}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error for {product_code}: {e}")
            return None
    
    def _extract_fits_from_html_source(self) -> List[str]:
        """
        Extract fit options by directly inspecting the HTML source for J.Crew's specific structure
        Looking for: <ul aria-label="Fit List"> containing buttons with fit options
        """
        fit_options = []
        
        try:
            # Method 1: Look for the Fit List structure (most accurate)
            # J.Crew uses <ul aria-label="Fit List"> to contain fit options
            fit_list_selectors = [
                'ul[aria-label="Fit List"]',
                'ul[aria-label*="fit" i][aria-label*="list" i]',
                'ul[role="group"][aria-label*="Fit" i]'
            ]
            
            for selector in fit_list_selectors:
                try:
                    fit_list = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if fit_list:
                        # Found the fit list, extract all buttons within it
                        buttons = fit_list.find_elements(By.CSS_SELECTOR, 'button[id*="fit-button"], button[aria-label]')
                        for button in buttons:
                            # Get fit name from aria-label or button text
                            fit_name = button.get_attribute('aria-label') or button.text
                            if fit_name:
                                # Clean the fit name (remove selected state, etc.)
                                fit_name = fit_name.strip()
                                fit_name = fit_name.replace(', selected', '').replace(' selected', '')
                                if fit_name and fit_name not in fit_options:
                                    fit_options.append(fit_name)
                        
                        if fit_options:
                            logger.info(f"   Found fits in Fit List: {fit_options}")
                            return fit_options
                except:
                    continue
            
            # Method 2: Look for buttons with specific fit-button IDs
            # Pattern: id="Classic__fit-button", id="Slim__fit-button", etc.
            fit_button_elements = self.driver.find_elements(By.CSS_SELECTOR, 'button[id$="__fit-button"]')
            if fit_button_elements:
                for button in fit_button_elements:
                    # Extract fit name from ID (e.g., "Classic__fit-button" -> "Classic")
                    button_id = button.get_attribute('id')
                    if button_id and '__fit-button' in button_id:
                        fit_name = button_id.replace('__fit-button', '')
                        if fit_name and fit_name not in fit_options:
                            fit_options.append(fit_name)
                    # Also check aria-label as backup
                    elif button.get_attribute('aria-label'):
                        fit_name = button.get_attribute('aria-label').strip()
                        if fit_name and fit_name not in fit_options:
                            fit_options.append(fit_name)
                
                if fit_options:
                    logger.info(f"   Found fits via button IDs: {fit_options}")
                    return fit_options
            
            # Method 3: Look within ProductVariations wrapper
            # Pattern: <div class="ProductVariations__wrapper..."> containing fit buttons
            variation_wrappers = self.driver.find_elements(By.CSS_SELECTOR, 'div[class*="ProductVariations__wrapper"]')
            for wrapper in variation_wrappers:
                # Check if this is the fit variation section
                wrapper_html = wrapper.get_attribute('innerHTML').lower()
                if 'fit' in wrapper_html and ('fit-guide' in wrapper_html or 'fit-button' in wrapper_html):
                    buttons = wrapper.find_elements(By.CSS_SELECTOR, 'button[aria-label]')
                    for button in buttons:
                        fit_name = button.get_attribute('aria-label') or button.text
                        if fit_name and self._is_valid_fit_name(fit_name):
                            fit_name = fit_name.strip()
                            if fit_name not in fit_options:
                                fit_options.append(fit_name)
                    
                    if fit_options:
                        logger.info(f"   Found fits in ProductVariations wrapper: {fit_options}")
                        return fit_options
            
        except Exception as e:
            logger.debug(f"Error extracting fits from HTML: {e}")
        
        return fit_options
    
    def _is_valid_fit_name(self, text: str) -> bool:
        """
        Check if text is a valid fit name (not a product name or other text)
        """
        if not text or len(text) > 30:
            return False
        
        text_lower = text.lower()
        
        # Valid fit keywords
        valid_fits = ['classic', 'slim', 'relaxed', 'tall', 'untucked', 'athletic', 'regular', 'standard']
        
        # Must contain at least one valid fit keyword
        return any(fit in text_lower for fit in valid_fits)
    
    
    def _clean_fit_options(self, fits: List[str]) -> List[str]:
        """Clean and normalize fit options"""
        cleaned = []
        seen = set()
        
        for fit in fits:
            # Remove common prefixes and states
            fit = fit.replace('Select ', '').replace('Choose ', '')
            fit = fit.replace('fit:', '').replace('Fit:', '')
            fit = fit.replace(', selected', '').replace(' selected', '')  # Remove selected state
            fit = fit.replace(', is unavailable', '').replace(' is unavailable', '')  # Remove unavailable state
            fit = fit.replace(', unavailable', '').replace(' unavailable', '')
            fit = fit.strip()
            
            # Normalize case
            if fit and fit.lower() not in seen:
                cleaned.append(fit)
                seen.add(fit.lower())
        
        return cleaned
    
    def process_all_products(self, limit: Optional[int] = None, 
                           skip_existing: bool = True) -> Dict[str, any]:
        """
        Process all products in the database
        
        Args:
            limit: Limit number of products to process
            skip_existing: Skip products that already have fit data
            
        Returns:
            Dictionary with processing statistics
        """
        # Create a new connection for each batch with autocommit
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True  # Auto-commit each statement to avoid long transactions
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            # Get products to process
            query = """
                SELECT product_code, product_name, product_url, fit_options
                FROM jcrew_product_cache
                WHERE product_url IS NOT NULL
            """
            
            if skip_existing:
                query += " AND (fit_options IS NULL OR array_length(fit_options, 1) = 0)"
            
            query += " ORDER BY product_code"
            
            if limit:
                query += f" LIMIT {limit}"
            
            cur.execute(query)
            products = cur.fetchall()
            
            total = len(products)
            logger.info(f"Found {total} products to process")
            self.stats['total_products'] = total
            
            # Process each product
            for idx, product in enumerate(products, 1):
                product_code = product['product_code']
                product_url = product['product_url']
                product_name = product['product_name']
                
                logger.info(f"\n[{idx}/{total}] Processing: {product_code} - {product_name[:50]}")
                
                try:
                    # Extract fit options
                    fit_options = self.extract_fit_options(product_url, product_code)
                    
                    # Update database (with autocommit, each update is immediate)
                    if fit_options:
                        cur.execute("""
                            UPDATE jcrew_product_cache
                            SET fit_options = %s,
                                updated_at = NOW()
                            WHERE product_code = %s
                        """, (fit_options, product_code))
                        self.stats['products_with_fits'] += 1
                        self.stats['updated'] += 1
                        logger.info(f"   Updated with fits: {fit_options}")
                    else:
                        # Mark as processed even if no fits found
                        cur.execute("""
                            UPDATE jcrew_product_cache
                            SET fit_options = NULL,
                                updated_at = NOW()
                            WHERE product_code = %s
                        """, (product_code,))
                        self.stats['products_without_fits'] += 1
                        logger.info(f"   No fits found (single fit product)")
                    
                except psycopg2.Error as db_err:
                    logger.error(f"   Database error for {product_code}: {db_err}")
                    self.stats['errors'] += 1
                    continue
                except Exception as e:
                    logger.error(f"   Error processing {product_code}: {e}")
                    self.stats['errors'] += 1
                    continue
                
                # Rate limiting
                time.sleep(2)  # Be respectful to J.Crew servers
                
                # Progress update every 10 products
                if idx % 10 == 0:
                    logger.info(f"Progress: {idx}/{total} processed")
                    self._save_progress(product_code)
            
            return self.stats
            
        except Exception as e:
            logger.error(f"Error in process_all_products: {e}")
            raise
        finally:
            cur.close()
            conn.close()
    
    def _save_progress(self, last_product_code: str):
        """Save progress to file for resuming if needed"""
        progress = {
            'timestamp': datetime.now().isoformat(),
            'last_product_code': last_product_code,
            'stats': self.stats
        }
        
        with open('jcrew_fit_crawler_progress.json', 'w') as f:
            json.dump(progress, f, indent=2)
    
    def test_specific_products(self):
        """Test with known products to verify accuracy"""
        test_products = [
            {
                'code': 'BE996',
                'url': 'https://www.jcrew.com/p/mens/categories/clothing/shirts/broken-in-oxford/broken-in-organic-cotton-oxford-shirt/BE996',
                'expected_fits': ['Classic', 'Slim', 'Slim Untucked', 'Tall', 'Relaxed']
            },
            {
                'code': 'BM493',
                'url': 'https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/ludlow/BM493',
                'expected_fits': None  # Single fit only
            }
        ]
        
        logger.info("Testing with known products...")
        
        for product in test_products:
            fits = self.extract_fit_options(product['url'], product['code'])
            
            if product['expected_fits']:
                if fits:
                    logger.info(f"✅ {product['code']}: Found {fits}")
                    logger.info(f"   Expected: {product['expected_fits']}")
                else:
                    logger.warning(f"❌ {product['code']}: Expected fits but found none")
            else:
                if fits:
                    logger.warning(f"❌ {product['code']}: Found fits but expected none: {fits}")
                else:
                    logger.info(f"✅ {product['code']}: Correctly identified as single fit")
    
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
            logger.info("Driver closed")
    
    def get_stats_summary(self) -> str:
        """Get a summary of processing statistics"""
        return f"""
        ========================================
        J.Crew Fit Crawler Statistics
        ========================================
        Total Products Processed: {self.stats['total_products']}
        Products with Fit Options: {self.stats['products_with_fits']}
        Products without Fit Options: {self.stats['products_without_fits']}
        Errors: {self.stats['errors']}
        Database Updates: {self.stats['updated']}
        ========================================
        """

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='J.Crew Fit Options Crawler')
    parser.add_argument('--test', action='store_true', help='Run test with known products')
    parser.add_argument('--limit', type=int, help='Limit number of products to process')
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    parser.add_argument('--skip-existing', action='store_true', default=True,
                       help='Skip products that already have fit data')
    parser.add_argument('--product-code', help='Process single product by code')
    
    args = parser.parse_args()
    
    # Initialize crawler
    crawler = JCrewFitCrawler(headless=args.headless)
    
    try:
        if args.test:
            # Run test mode
            crawler.test_specific_products()
        
        elif args.product_code:
            # Process single product
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            cur.execute("""
                SELECT product_code, product_url
                FROM jcrew_product_cache
                WHERE product_code = %s
            """, (args.product_code,))
            
            product = cur.fetchone()
            if product:
                fits = crawler.extract_fit_options(product['product_url'], product['product_code'])
                logger.info(f"Result: {fits}")
                
                # Update database
                cur.execute("""
                    UPDATE jcrew_product_cache
                    SET fit_options = %s, updated_at = NOW()
                    WHERE product_code = %s
                """, (fits, args.product_code))
                conn.commit()
            else:
                logger.error(f"Product {args.product_code} not found")
            
            cur.close()
            conn.close()
        
        else:
            # Process all products
            stats = crawler.process_all_products(
                limit=args.limit,
                skip_existing=args.skip_existing
            )
            print(crawler.get_stats_summary())
    
    finally:
        crawler.cleanup()

if __name__ == "__main__":
    main()
