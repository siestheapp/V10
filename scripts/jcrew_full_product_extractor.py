#!/usr/bin/env python3
"""
Enhanced J.Crew Product Extractor using Playwright
Captures ALL unique products from J.Crew PLP pages
Handles their anti-scraper measures and lazy loading properly
"""

import re
import time
import json
import csv
from urllib.parse import urlparse, urlunparse, parse_qs
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import pandas as pd
from datetime import datetime
import logging
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

class JCrewProductExtractor:
    """Extract all unique products from J.Crew PLP pages"""
    
    def __init__(self, headless=True):
        self.headless = headless
        self.products = {}
        self.base_url = "https://www.jcrew.com"
        
        # Query params to ignore for uniqueness (color/fit variants)
        self.ignore_params = {
            "color_name", "color", "colorProductCode", "fit", 
            "display", "N", "Nrpp", "Ns", "Nf", "Nty",
            "intcmp", "mbid", "srccode", "cid"
        }
        
        # Product code patterns - J.Crew uses these formats
        self.product_code_patterns = [
            r'/([A-Z]{2}\d{3,4})(?:\?|$|")',  # BE123, CM456 patterns
            r'/([A-Z0-9]{4,6})(?:\?|$|")',    # General alphanumeric
            r'"productCode"\s*:\s*"([A-Z0-9]{4,6})"',  # JSON productCode
            r'"sku"\s*:\s*"([A-Z0-9]{4,6})"',  # SKU codes
        ]
    
    def extract_product_code(self, url):
        """Extract product code from URL"""
        for pattern in self.product_code_patterns[:2]:  # URL patterns only
            match = re.search(pattern, url)
            if match:
                return match.group(1).upper()
        
        # Fallback: last segment that looks like a code
        path = urlparse(url).path
        segments = [s for s in path.split('/') if s]
        if segments:
            last_seg = segments[-1]
            if re.match(r'^[A-Z0-9]{4,6}$', last_seg, re.IGNORECASE):
                return last_seg.upper()
        return None
    
    def canonical_url(self, url):
        """Get canonical URL without color/fit params"""
        parsed = urlparse(url)
        # Remove all query params for canonical form
        return urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", "", ""))
    
    def extract_products_from_page(self, page):
        """Extract all products from the current page state"""
        logger.info("Extracting products from page...")
        
        # Method 1: Find all product links
        product_links = page.query_selector_all("a[href*='/p/']")
        logger.info(f"  Found {len(product_links)} product links")
        
        for link in product_links:
            try:
                href = link.get_attribute("href")
                if not href or '/p/' not in href:
                    continue
                
                # Make absolute URL
                if not href.startswith('http'):
                    href = self.base_url + href if href.startswith('/') else self.base_url + '/' + href
                
                # Get canonical URL and product code
                canonical = self.canonical_url(href)
                product_code = self.extract_product_code(href)
                
                if not product_code:
                    continue
                
                # Try to get product name from various sources
                name = ""
                try:
                    # Try parent container for product info
                    parent = link.evaluate("el => el.closest('article, div[class*=\"product\"], li')")
                    if parent:
                        # Look for product name in parent
                        name_elem = page.evaluate("""
                            (el) => {
                                const nameEl = el.querySelector('h3, h4, [class*="name"], [class*="title"]');
                                return nameEl ? nameEl.textContent.trim() : '';
                            }
                        """, parent)
                        if name_elem:
                            name = name_elem
                except:
                    pass
                
                if not name:
                    # Fallback to link text or aria-label
                    name = link.get_attribute("aria-label") or link.inner_text() or ""
                
                name = " ".join(name.split())  # Clean up whitespace
                
                # Store unique product
                if product_code not in self.products:
                    self.products[product_code] = {
                        'code': product_code,
                        'name': name,
                        'url': canonical,
                        'original_url': href
                    }
                    logger.debug(f"    Added: {product_code} - {name[:50]}")
                
            except Exception as e:
                logger.debug(f"    Error processing link: {e}")
                continue
        
        # Method 2: Extract from page HTML/JavaScript
        try:
            # Look for embedded product data
            page_content = page.content()
            
            # Extract product codes from HTML
            for pattern in self.product_code_patterns:
                matches = re.findall(pattern, page_content, re.IGNORECASE)
                for code in matches:
                    if isinstance(code, str) and len(code) >= 4:
                        code = code.upper()
                        if code not in self.products and re.match(r'^[A-Z0-9]{4,6}$', code):
                            self.products[code] = {
                                'code': code,
                                'name': '',
                                'url': f'{self.base_url}/p/mens/categories/clothing/shirts/{code}',
                                'original_url': ''
                            }
                            logger.debug(f"    Added from HTML: {code}")
            
            # Try to extract from window.__INITIAL_STATE__ or similar
            try:
                product_data = page.evaluate("""
                    () => {
                        // Try various common patterns for product data
                        if (window.__INITIAL_STATE__ && window.__INITIAL_STATE__.products) {
                            return window.__INITIAL_STATE__.products;
                        }
                        if (window.digitalData && window.digitalData.products) {
                            return window.digitalData.products;
                        }
                        if (window.__NEXT_DATA__ && window.__NEXT_DATA__.props) {
                            return window.__NEXT_DATA__.props;
                        }
                        // Look for any global with products
                        for (let key in window) {
                            if (key.includes('product') && typeof window[key] === 'object') {
                                return window[key];
                            }
                        }
                        return null;
                    }
                """)
                
                if product_data:
                    logger.info("  Found embedded product data")
                    self._parse_json_products(product_data)
                    
            except:
                pass
                
        except Exception as e:
            logger.debug(f"  Error extracting from page source: {e}")
        
        logger.info(f"  Total unique products found: {len(self.products)}")
    
    def _parse_json_products(self, data, depth=0):
        """Recursively parse JSON data for products"""
        if depth > 5:  # Prevent infinite recursion
            return
        
        if isinstance(data, dict):
            # Look for product code fields
            if 'productCode' in data or 'sku' in data or 'id' in data:
                code = data.get('productCode') or data.get('sku') or data.get('id', '')
                if isinstance(code, str) and re.match(r'^[A-Z0-9]{4,6}$', code, re.IGNORECASE):
                    code = code.upper()
                    if code not in self.products:
                        self.products[code] = {
                            'code': code,
                            'name': data.get('name', '') or data.get('title', ''),
                            'url': data.get('url', f'{self.base_url}/p/mens/categories/clothing/shirts/{code}'),
                            'original_url': data.get('url', '')
                        }
            
            # Recurse through dict values
            for value in data.values():
                if isinstance(value, (dict, list)):
                    self._parse_json_products(value, depth + 1)
                    
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    self._parse_json_products(item, depth + 1)
    
    def scroll_and_load_all(self, page, max_scrolls=20):
        """Scroll to load all lazy-loaded content"""
        logger.info("Scrolling to load all products...")
        
        last_height = 0
        stable_count = 0
        
        for i in range(max_scrolls):
            # Scroll to bottom
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            
            # Wait a bit for content to load
            page.wait_for_timeout(1500)
            
            # Check for "Load More" or "Show More" buttons
            try:
                load_more_selectors = [
                    "button:has-text('Show More')",
                    "button:has-text('Load More')",
                    "button:has-text('View More')",
                    "[class*='load-more']",
                    "[class*='show-more']"
                ]
                
                for selector in load_more_selectors:
                    try:
                        button = page.query_selector(selector)
                        if button and button.is_visible():
                            logger.info(f"  Clicking load more button...")
                            button.click()
                            page.wait_for_timeout(2000)
                            break
                    except:
                        continue
                        
            except:
                pass
            
            # Check if page height changed
            new_height = page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                stable_count += 1
                if stable_count >= 3:  # Height stable for 3 scrolls
                    logger.info(f"  Page fully loaded after {i+1} scrolls")
                    break
            else:
                stable_count = 0
            
            last_height = new_height
            
            # Extract products after each scroll
            self.extract_products_from_page(page)
    
    def scrape_plp(self, url):
        """Main method to scrape a PLP page"""
        logger.info(f"Scraping: {url}")
        
        with sync_playwright() as p:
            # Launch browser with anti-detection settings
            browser = p.chromium.launch(
                headless=self.headless,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                    "--disable-web-security",
                    "--disable-features=IsolateOrigins,site-per-process"
                ]
            )
            
            # Create context with realistic settings
            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                viewport={"width": 1920, "height": 1080},
                java_script_enabled=True,
                ignore_https_errors=True,
                locale="en-US",
            )
            
            # Add anti-detection scripts
            context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
            
            page = context.new_page()
            
            try:
                # Navigate to page
                logger.info("Loading page...")
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                
                # Wait for initial content
                page.wait_for_timeout(3000)
                
                # Accept cookies if present
                try:
                    cookie_button = page.query_selector("button:has-text('Accept')")
                    if cookie_button:
                        cookie_button.click()
                        page.wait_for_timeout(1000)
                except:
                    pass
                
                # Initial extraction
                self.extract_products_from_page(page)
                
                # Scroll and load all products
                self.scroll_and_load_all(page)
                
                # Final extraction
                self.extract_products_from_page(page)
                
                logger.info(f"✅ Scraping complete. Found {len(self.products)} unique products")
                
            except Exception as e:
                logger.error(f"Error during scraping: {e}")
            
            finally:
                browser.close()
        
        return self.products
    
    def save_results(self, output_file="jcrew_products.csv"):
        """Save results to CSV"""
        if not self.products:
            logger.warning("No products to save")
            return
        
        # Convert to DataFrame
        df = pd.DataFrame.from_dict(self.products, orient='index')
        
        # Sort by product code
        df = df.sort_values('code')
        
        # Save to CSV
        df.to_csv(output_file, index=False)
        logger.info(f"💾 Saved {len(df)} products to {output_file}")
        
        # Also save detailed JSON
        json_file = output_file.replace('.csv', '.json')
        with open(json_file, 'w') as f:
            json.dump(self.products, f, indent=2)
        logger.info(f"💾 Saved detailed JSON to {json_file}")
        
        return df


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract all J.Crew products from PLP')
    parser.add_argument('--url', default='https://www.jcrew.com/plp/mens/categories/clothing/shirts',
                        help='PLP URL to scrape')
    parser.add_argument('--output', default='jcrew_products_full.csv',
                        help='Output CSV file')
    parser.add_argument('--visible', action='store_true',
                        help='Run browser in visible mode')
    
    args = parser.parse_args()
    
    # Create extractor
    extractor = JCrewProductExtractor(headless=not args.visible)
    
    # Scrape the page
    products = extractor.scrape_plp(args.url)
    
    # Save results
    if products:
        df = extractor.save_results(args.output)
        
        # Print summary
        print("\n" + "="*60)
        print("EXTRACTION SUMMARY")
        print("="*60)
        print(f"Total unique products found: {len(products)}")
        print(f"\nSample products:")
        for code, info in list(products.items())[:5]:
            print(f"  {code}: {info['name'][:50]}")
        print("\nFiles created:")
        print(f"  - {args.output}")
        print(f"  - {args.output.replace('.csv', '.json')}")
    else:
        print("❌ No products found. The page may have changed or there was an error.")


if __name__ == "__main__":
    main()

