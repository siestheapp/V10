#!/usr/bin/env python3
"""
Enhanced J.Crew Crawler with Variant Support
Handles compound product codes for variants (ME053-CC100, ME053-CC101, etc.)
"""

import re
import time
import psycopg2
import logging
from typing import Dict, List, Optional, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options

# Import db config
import sys
sys.path.append('/Users/seandavey/projects/V10')
from db_config import DB_CONFIG

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

class JCrewVariantCrawler:
    """Crawler that properly handles J.Crew product variants"""
    
    # Updated category URLs
    CATEGORY_URLS = [
        'https://www.jcrew.com/plp/mens/categories/clothing/shirts',
        'https://www.jcrew.com/plp/mens/categories/clothing/shirts/secret-wash',
        'https://www.jcrew.com/plp/mens/categories/clothing/shirts/broken-in-oxford',
        'https://www.jcrew.com/plp/mens/categories/clothing/shirts/linen',
        'https://www.jcrew.com/plp/mens/categories/clothing/shirts/chambray-and-denim-shirts',
        'https://www.jcrew.com/plp/mens/categories/clothing/dress-shirts',
        'https://www.jcrew.com/plp/mens/categories/clothing/t-shirts-and-polos',
        'https://www.jcrew.com/plp/mens/categories/clothing/polos',
        'https://www.jcrew.com/plp/mens/categories/clothing/sweaters',
        # Add the cotton-cashmere subcategory
        'https://www.jcrew.com/plp/mens/categories/clothing/shirts?sub-categories=mens-shirts-cotton-cashmere'
    ]
    
    def __init__(self, headless: bool = True):
        """Initialize the crawler with Selenium WebDriver"""
        self.driver = self._setup_driver(headless)
        self.discovered_products = {}  # Track discovered product codes
        
    def _setup_driver(self, headless: bool = True) -> webdriver.Chrome:
        """Setup Chrome driver with anti-detection measures"""
        options = Options()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    
    def extract_product_codes(self, url: str) -> Tuple[str, str, Optional[str]]:
        """
        Extract compound product code, base code, and variant code from URL
        
        Args:
            url: Product URL
            
        Returns:
            Tuple of (compound_code, base_code, variant_code)
            e.g., ('ME053-CC100', 'ME053', 'CC100') or ('BE996', 'BE996', None)
        """
        # Extract base product code
        base_code = None
        patterns = [
            r'/([A-Z0-9]{2,8})(?:\?|$)',        # Most common: /CODE?params
            r'/([A-Z0-9]{2,8})$',               # End of URL: /CODE
            r'/p/.*/([A-Z0-9]{2,8})(?:\?|$)',  # /p/ paths
            r'/m/.*/([A-Z0-9]{2,8})(?:\?|$)',  # /m/ paths
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                base_code = match.group(1)
                break
        
        if not base_code:
            return None, None, None
        
        # Extract variant code (colorProductCode)
        variant_code = None
        variant_match = re.search(r'colorProductCode=([A-Z0-9]+)', url)
        if variant_match:
            variant_code = variant_match.group(1)
        
        # Create compound code
        if variant_code:
            compound_code = f"{base_code}-{variant_code}"
        else:
            compound_code = base_code
        
        return compound_code, base_code, variant_code
    
    def discover_products_from_category(self, category_url: str) -> List[Dict]:
        """
        Discover all products from a category page, including variants
        """
        products = []
        
        try:
            logger.info(f"📂 Browsing category: {category_url}")
            self.driver.get(category_url)
            
            # Wait for products to load
            wait = WebDriverWait(self.driver, 15)
            try:
                wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href*="/p/"], a[href*="/m/"], [data-testid*="product"], .product-tile'))
                )
            except TimeoutException:
                logger.warning(f"   No products found on page after waiting")
            
            time.sleep(5)  # Let dynamic content fully load
            
            # Scroll to load more products
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_attempts = 0
            max_scrolls = 5
            
            while scroll_attempts < max_scrolls:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                scroll_attempts += 1
            
            # Extract product links
            product_links = []
            
            # Strategy 1: Direct product links
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
            
            seen_compounds = set()  # Track compound codes to avoid duplicates
            
            for link in product_links:
                href = link.get_attribute('href')
                if not href or ('/p/' not in href and '/m/' not in href):
                    continue
                
                # Extract product codes (compound, base, variant)
                compound_code, base_code, variant_code = self.extract_product_codes(href)
                
                if compound_code and compound_code not in seen_compounds:
                    seen_compounds.add(compound_code)
                    
                    # Get product name
                    product_name = link.get_attribute('aria-label') or link.text
                    if not product_name:
                        try:
                            parent = link.find_element(By.XPATH, '..')
                            product_name = parent.text.split('\n')[0]
                        except:
                            product_name = compound_code
                    
                    product = {
                        'url': href,  # Keep full URL with parameters
                        'compound_code': compound_code,
                        'base_code': base_code,
                        'variant_code': variant_code,
                        'name': product_name.strip()[:100] if product_name else compound_code
                    }
                    
                    # Avoid duplicates based on compound code
                    if compound_code not in self.discovered_products:
                        products.append(product)
                        self.discovered_products[compound_code] = product
            
            logger.info(f"   Found {len(products)} unique products (including variants)")
            
        except Exception as e:
            logger.error(f"Error discovering products from {category_url}: {e}")
        
        return products
    
    def extract_product_details(self, product_url: str, compound_code: str, base_code: str, variant_code: Optional[str]) -> Dict:
        """
        Extract detailed information from a product page
        """
        try:
            logger.info(f"🔍 Extracting details for {compound_code}")
            self.driver.get(product_url)
            
            # Wait for page to load
            wait = WebDriverWait(self.driver, 10)
            time.sleep(2)
            
            product_data = {
                'product_code': compound_code,  # The compound code
                'base_product_code': base_code,  # The base style
                'variant_code': variant_code,    # The variant (if any)
                'product_url': product_url.split('?')[0],  # Clean URL
            }
            
            # Extract product name
            try:
                title_element = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'h1, [data-testid="pdp-product-title"]'))
                )
                product_data['product_name'] = title_element.text
            except:
                product_data['product_name'] = compound_code
            
            # Extract price
            try:
                price_element = self.driver.find_element(By.CSS_SELECTOR, '[class*="price"], [data-testid*="price"]')
                price_text = price_element.text
                price_match = re.search(r'\$?([\d,]+\.?\d*)', price_text)
                if price_match:
                    product_data['price'] = float(price_match.group(1).replace(',', ''))
            except:
                product_data['price'] = None
            
            # Extract fit options
            product_data['fit_options'] = self._extract_fit_options()
            
            return product_data
            
        except Exception as e:
            logger.error(f"Error extracting details for {compound_code}: {e}")
            return {
                'product_code': compound_code,
                'base_product_code': base_code,
                'variant_code': variant_code,
                'product_url': product_url.split('?')[0]
            }
    
    def _extract_fit_options(self) -> Optional[List[str]]:
        """Extract fit options from the current product page"""
        try:
            # Look for fit list
            fit_list = self.driver.find_element(By.CSS_SELECTOR, 'ul[aria-label="Fit List"]')
            
            # Find all fit buttons within the list
            fit_buttons = fit_list.find_elements(By.CSS_SELECTOR, 'button[id*="fit-button"], button[aria-label]')
            
            fit_options = []
            for button in fit_buttons:
                # Try to get fit name from aria-label first
                fit_name = button.get_attribute('aria-label')
                if fit_name and 'fit' in fit_name.lower():
                    # Clean the fit name
                    fit_name = fit_name.replace(' fit', '').replace('Fit', '').strip()
                    if fit_name and fit_name not in fit_options:
                        fit_options.append(fit_name)
                    continue
                
                # Fallback to button ID
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
        """Save or update product in database with variant support"""
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cur = conn.cursor()
        
        try:
            # Check if this specific variant exists
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
                        base_product_code = %s,
                        variant_code = %s,
                        price = %s,
                        fit_options = %s,
                        updated_at = NOW()
                    WHERE product_code = %s
                """, (
                    product_data.get('product_name'),
                    product_data.get('product_url'),
                    product_data.get('base_product_code'),
                    product_data.get('variant_code'),
                    product_data.get('price'),
                    product_data.get('fit_options'),
                    product_data['product_code']
                ))
                logger.info(f"   💾 Updated {product_data['product_code']} in database")
            else:
                # Insert new product
                cur.execute("""
                    INSERT INTO jcrew_product_cache (
                        product_code, product_name, product_url, 
                        base_product_code, variant_code,
                        price, fit_options, 
                        created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                """, (
                    product_data['product_code'],
                    product_data.get('product_name'),
                    product_data.get('product_url'),
                    product_data.get('base_product_code'),
                    product_data.get('variant_code'),
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
        """Main crawl function with variant support"""
        if categories is None:
            categories = self.CATEGORY_URLS
        
        total_products = 0
        
        for category_url in categories:
            # Discover products from category page
            products = self.discover_products_from_category(category_url)
            
            # Process each discovered product
            for product in products:
                # Extract detailed information
                product_details = self.extract_product_details(
                    product['url'], 
                    product['compound_code'],
                    product['base_code'],
                    product['variant_code']
                )
                
                if product_details:
                    # Save to database
                    self.save_to_database(product_details)
                    total_products += 1
                
                # Small delay between products
                time.sleep(1)
        
        logger.info(f"\n✅ Crawl complete! Processed {total_products} products (including variants)")
    
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()


if __name__ == "__main__":
    # Test with cotton-cashmere subcategory
    crawler = JCrewVariantCrawler(headless=False)
    
    try:
        # Crawl just the cotton-cashmere category
        crawler.crawl([
            'https://www.jcrew.com/plp/mens/categories/clothing/shirts?sub-categories=mens-shirts-cotton-cashmere'
        ])
    finally:
        crawler.cleanup()

