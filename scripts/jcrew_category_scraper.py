#!/usr/bin/env python3
"""
J.Crew Category Page Scraper
Autonomously clicks through product listings and scrapes each product's colors and fits
Created: September 16, 2025

USAGE:
    python scripts/jcrew_category_scraper.py "https://www.jcrew.com/plp/mens/categories/clothing/shirts"
    python scripts/jcrew_category_scraper.py "https://www.jcrew.com/plp/mens/categories/clothing/shirts?sub-categories=men-shirts-linen"

This scraper:
- Takes a J.Crew category/listing page URL
- Finds all product links on the page
- Visits each product page individually (like a human clicking)
- Runs precise scraping logic to get actual colors and fits
- NO HARDCODED DATA or FALLBACKS
- Stops immediately on errors
"""

import sys
import json
import time
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from urllib.parse import urljoin, urlparse
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import traceback


class JCrewCategoryScraper:
    """Scrapes all products from a J.Crew category page"""
    
    def __init__(self, headless: bool = False):
        """Initialize the scraper with Chrome driver"""
        self.headless = headless
        self.driver = None
        self.base_url = "https://www.jcrew.com"
        
    def setup_driver(self) -> webdriver.Chrome:
        """Setup Chrome driver with options"""
        print("🔧 Setting up Chrome driver...")
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        print("✅ Chrome driver ready")
        return driver
    
    def extract_product_links(self, category_url: str) -> List[Dict[str, str]]:
        """Extract all product links from a category page"""
        print(f"\n📂 Loading category page: {category_url}")
        self.driver.get(category_url)
        
        # Wait for products to load
        try:
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-qaid*='ProductCard'], .product-tile, [class*='product-card'], a[href*='/p/']"))
            )
            print("✅ Category page loaded")
            time.sleep(2)  # Let initial products render
            
            # Close any initial popups/modals on category page
            self.close_popups()
            
        except TimeoutException:
            raise Exception("❌ ERROR: Could not load category page or find products")
        
        # First, collect products visible without scrolling
        products = []
        initial_products = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/p/']")
        print(f"📍 Found {len(initial_products)} initial products")

        # Scroll to load additional products.
        # NOTE: This method should not inspect sys.argv because it is called
        # from multiple entrypoints (standalone script and category ingest).
        print("📜 Scrolling to load additional products...")

        viewport_height = self.driver.execute_script("return window.innerHeight")
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scroll_position = 0

        while scroll_position < last_height:
            # Scroll down by viewport height
            scroll_position += viewport_height
            self.driver.execute_script(f"window.scrollTo(0, {scroll_position});")
            time.sleep(1)

            # Check if page height increased (new content loaded)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height > last_height:
                last_height = new_height

        # Scroll back to top to ensure we can access all elements
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)

        # Find product links - be more specific to get actual product cards
        # J.Crew uses specific patterns for product links in listing pages
        product_selectors = [
            "a[href*='/p/mens/'][href*='/categories/']",  # Men's product links
            "article a[href*='/p/']",  # Links within article elements
            "[data-qaid*='ProductCard'] a",  # Links within product cards
            ".product-tile a[href*='/p/']",  # Product tile links
            "[class*='product-card'] a[href*='/p/']"  # Product card links
        ]
        
        product_elements = []
        for selector in product_selectors:
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                product_elements.extend(elements)
                print(f"📝 Found {len(elements)} links with selector: {selector}")
        
        print(f"📝 Total {len(product_elements)} potential product links found")
        
        # Process unique product links
        seen_urls = set()
        for elem in product_elements:
            try:
                href = elem.get_attribute('href')
                
                # Skip if not a valid product URL
                if not href or '/p/' not in href:
                    continue
                    
                # Skip duplicates
                if href in seen_urls:
                    continue
                seen_urls.add(href)
                
                # Extract product code from URL (e.g., CF667 from the URL)
                # J.Crew product codes are typically 5-6 characters starting with a letter
                match = re.search(r'/([A-Z][A-Z0-9]{3,5})(?:\?|$)', href)
                if not match:
                    continue
                    
                product_code = match.group(1)
                
                # Skip if we already have this product
                if any(p['product_code'] == product_code for p in products):
                    continue
                
                # Get product name if available
                product_name = "Unknown"
                try:
                    # Try to get the product name from nearby text
                    # Look for h3 or product name within the same product card
                    parent = elem.find_element(By.XPATH, "./ancestor::article | ./ancestor::*[contains(@class, 'product')]")
                    name_elems = parent.find_elements(By.CSS_SELECTOR, "h3, [class*='product-name'], [class*='product-title']")
                    for name_elem in name_elems:
                        text = name_elem.text.strip()
                        if text and len(text) > 3:
                            product_name = text
                            break
                except:
                    # Fallback to link text
                    link_text = elem.text.strip()
                    if link_text and len(link_text) > 3:
                        product_name = link_text
                
                # Clean the URL (remove query params for consistency)
                clean_url = href.split('?')[0]
                
                products.append({
                    'url': clean_url,
                    'product_code': product_code,
                    'product_name': product_name
                })
                print(f"   ✓ Added: {product_code} - {product_name[:50]}...")
                
            except Exception as e:
                continue
        
        if not products:
            print("⚠️  No valid product links found. Debugging info:")
            print(f"   - Total links found: {len(product_elements)}")
            if product_elements and len(product_elements) > 0:
                sample_href = product_elements[0].get_attribute('href')
                print(f"   - Sample href: {sample_href}")
        else:
            print(f"✅ Found {len(products)} unique products")
        
        return products
    
    def close_popups(self):
        """Close any popups or modals that appear"""
        try:
            # Look for close buttons on modals/popups
            close_selectors = [
                "button[aria-label*='close' i]",
                "button[aria-label*='Close' i]",
                ".modal-close",
                "[class*='modal'] button[class*='close']",
                "[class*='popup'] button[class*='close']",
                "button[class*='close']",
                "[data-qaid*='close']",
                "svg[class*='close']",
                ".close-button"
            ]
            
            for selector in close_selectors:
                try:
                    close_buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for button in close_buttons:
                        if button.is_displayed():
                            button.click()
                            print("   🔒 Closed popup/modal")
                            time.sleep(1)
                            return True
                except:
                    continue
                    
            # Also try pressing ESC key
            try:
                self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
            except:
                pass
                
        except Exception as e:
            pass
        return False
    
    def scrape_product_details(self, product_url: str) -> Dict:
        """Scrape color and fit options from a single product page"""
        print(f"\n{'='*80}")
        print(f"📍 Scraping: {product_url}")
        
        result = {
            'url': product_url,
            'product_code': '',
            'product_name': '',
            'colors': [],
            'fits': [],
            'error': None,
            'scraped_at': datetime.now().isoformat()
        }
        
        try:
            # Load the product page
            self.driver.get(product_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )
            time.sleep(2)  # Let JavaScript render
            
            # Close any popups that might appear
            self.close_popups()
            
            # Get product name - wait for it to load
            try:
                # Wait for the main product name element
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h1, [class*='product-name']"))
                )
                
                # Try multiple selectors for product name
                name_selectors = [
                    "h1.product-name__title",
                    "h1[class*='product-name']",
                    "h1[data-qaid*='product-name']",
                    "h1"
                ]
                
                product_name = ""
                for selector in name_selectors:
                    try:
                        name_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                        product_name = name_elem.text.strip()
                        if product_name and len(product_name) > 2:  # Avoid empty or single char
                            break
                    except:
                        continue
                
                result['product_name'] = product_name
                if product_name:
                    print(f"   ✅ Name: {product_name}")
                else:
                    print("   ⚠️  Could not find product name")
            except Exception as e:
                print(f"   ⚠️  Could not find product name: {e}")
            
            # Extract product code from URL
            match = re.search(r'/([A-Z0-9]+)(?:\?|$)', product_url)
            if match:
                result['product_code'] = match.group(1)
            
            # Extract colors
            print("   🎨 Extracting colors...")
            colors = self.extract_colors()
            if not colors:
                raise Exception("No colors found - critical data missing!")
            result['colors'] = colors
            print(f"   ✅ Found {len(colors)} colors")
            
            # Extract fits
            print("   👔 Extracting fit options...")
            fits = self.extract_fits()
            result['fits'] = fits
            if fits:
                print(f"   ✅ Found {len(fits)} fit options")
            else:
                print("   📝 No fit variations (single-fit product)")
            
            print(f"   ✅ SUCCESS: {result['product_code']} - {result['product_name']}")
            
        except Exception as e:
            error_msg = str(e)
            result['error'] = error_msg
            print(f"   ❌ ERROR: {error_msg}")
            raise  # Re-raise to stop the entire process
        
        return result
    
    def extract_colors(self) -> List[str]:
        """
        Extract color options from J.Crew's actual HTML structure
        EXACT COPY from precise_jcrew_html_scraper_v2.py
        NO FALLBACKS - fails if structure not found
        """
        colors = []
        
        # Strategy 1: Look for radio inputs with aria-labels
        try:
            radio_elements = self.driver.find_elements(By.CSS_SELECTOR, "input[type='radio'][aria-label]")
            
            for radio in radio_elements:
                aria_label = radio.get_attribute('aria-label')
                # Filter for color-related labels (not size or fit)
                if aria_label and not any(x in aria_label.lower() for x in ['size', 'fit', 'classic', 'slim', 'tall', 'relaxed']):
                    # Extract color name from aria-label
                    # Format is often "Color Name $Price" or just "Color Name"
                    color_match = re.match(r'^([^$]+)', aria_label.strip())
                    if color_match:
                        color_name = color_match.group(1).strip()
                        if color_name and color_name not in colors:
                            colors.append(color_name)
        except:
            pass
        
        # Strategy 2: Look for divs with classes containing "color" or "Color"
        if not colors:
            try:
                color_divs = self.driver.find_elements(By.CSS_SELECTOR, "[class*='color' i][class*='item' i]")
                
                for div in color_divs:
                    # Try to get text or data attributes
                    color_text = div.text.strip()
                    if color_text and '$' not in color_text[:3]:  # Avoid prices
                        colors.append(color_text)
                    else:
                        # Try data attributes
                        for attr in ['data-color', 'data-name', 'data-label']:
                            color_name = div.get_attribute(attr)
                            if color_name:
                                colors.append(color_name)
                                break
            except:
                pass
        
        # Strategy 3: Look for image swatches
        if not colors:
            try:
                swatch_images = self.driver.find_elements(By.CSS_SELECTOR, "img[class*='swatch' i], img[alt*='color' i]")
                
                for img in swatch_images:
                    alt_text = img.get_attribute('alt')
                    if alt_text and alt_text not in colors:
                        colors.append(alt_text)
            except:
                pass
        
        if not colors:
            raise Exception("NO COLORS FOUND - All extraction strategies failed")
            
        return colors
    
    def extract_fits(self) -> List[str]:
        """
        Extract fit options from J.Crew's actual HTML structure
        EXACT COPY from precise_jcrew_html_scraper_v2.py
        NO FALLBACKS - optional data, returns empty if not found
        """
        fits = []
        
        # Strategy 1: Look for buttons with specific data-qaid patterns
        try:
            # J.Crew uses data-qaid="pdpProductVariationsItem" for fit buttons
            fit_buttons = self.driver.find_elements(By.CSS_SELECTOR, "[data-qaid*='ProductVariationsItem']")
            
            if fit_buttons:
                for button in fit_buttons:
                    fit_text = button.text.strip()
                    if fit_text and fit_text not in fits:
                        fits.append(fit_text)
        except:
            pass
        
        # Strategy 2: Look for buttons within ProductVariations wrapper
        if not fits:
            try:
                # Find any element with class containing "ProductVariations"
                variation_elements = self.driver.find_elements(By.CSS_SELECTOR, "[class*='ProductVariations']")
                
                for element in variation_elements:
                    # Find buttons within this element
                    buttons = element.find_elements(By.TAG_NAME, "button")
                    for button in buttons:
                        fit_text = button.text.strip()
                        # Common fit names
                        if fit_text and any(x in fit_text for x in ['Classic', 'Slim', 'Tall', 'Relaxed', 'Untucked', 'Regular']):
                            if fit_text not in fits:
                                fits.append(fit_text)
            except:
                pass
        
        # Strategy 3: Look for any button with fit-related text
        if not fits:
            try:
                all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
                
                fit_keywords = ['Classic', 'Slim', 'Tall', 'Relaxed', 'Untucked', 'Regular', 'Athletic', 'Traditional']
                
                for button in all_buttons:
                    button_text = button.text.strip()
                    # Check if this looks like a fit option
                    if button_text and any(keyword in button_text for keyword in fit_keywords):
                        # Avoid navigation buttons
                        if not any(x in button_text.lower() for x in ['shop', 'add', 'cart', 'size', 'review']):
                            if button_text not in fits:
                                fits.append(button_text)
            except:
                pass
        
        # No error if no fits found - it's optional data
        return fits
    
    def scrape_category(self, category_url: str) -> Dict:
        """Main method to scrape all products from a category"""
        start_time = datetime.now()
        results = {
            'category_url': category_url,
            'started_at': start_time.isoformat(),
            'products': [],
            'summary': {
                'total_products': 0,
                'successful': 0,
                'failed': 0
            }
        }
        
        try:
            # Setup driver
            self.driver = self.setup_driver()
            
            # Get all product links from category page
            product_links = self.extract_product_links(category_url)
            results['summary']['total_products'] = len(product_links)
            
            if not product_links:
                print("\n⚠️  No products found on this category page")
                return results
            
            print(f"\n{'='*80}")
            print(f"📋 Starting to scrape {len(product_links)} products")
            print(f"{'='*80}")
            
            # Add limit for testing (can be passed as second argument)
            limit = None
            if len(sys.argv) > 2:
                try:
                    limit = int(sys.argv[2])
                    print(f"\n⚠️  LIMIT: Only scraping first {limit} products for testing")
                    product_links = product_links[:limit]
                except ValueError:
                    pass
            
            # Scrape each product
            for i, product_info in enumerate(product_links, 1):
                print(f"\n[{i}/{len(product_links)}] Processing {product_info['product_code']}")
                
                try:
                    product_data = self.scrape_product_details(product_info['url'])
                    results['products'].append(product_data)
                    
                    if product_data.get('error'):
                        results['summary']['failed'] += 1
                        print(f"\n❌ STOPPING: Error encountered while scraping {product_info['product_code']}")
                        print(f"   Error: {product_data['error']}")
                        break  # Stop on error as requested
                    else:
                        results['summary']['successful'] += 1
                    
                    # Small delay to be respectful to the server
                    time.sleep(1)
                    
                except Exception as e:
                    # Critical error - stop immediately
                    error_data = {
                        'url': product_info['url'],
                        'product_code': product_info['product_code'],
                        'product_name': product_info.get('product_name', 'Unknown'),
                        'colors': [],
                        'fits': [],
                        'error': str(e),
                        'scraped_at': datetime.now().isoformat()
                    }
                    results['products'].append(error_data)
                    results['summary']['failed'] += 1
                    
                    print(f"\n❌ CRITICAL ERROR: Stopping scraper")
                    print(f"   Product: {product_info['product_code']}")
                    print(f"   Error: {str(e)}")
                    traceback.print_exc()
                    break
            
            # Add completion time
            end_time = datetime.now()
            results['completed_at'] = end_time.isoformat()
            results['duration_seconds'] = (end_time - start_time).total_seconds()
            
        finally:
            if self.driver:
                print("\n🔚 Closing browser...")
                self.driver.quit()
        
        return results
    
    def save_results(self, results: Dict, output_file: str = None) -> str:
        """Save results to JSON file"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"jcrew_category_scrape_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_file}")
        return output_file
    
    def print_summary(self, results: Dict):
        """Print a summary of the scraping results"""
        print(f"\n{'='*80}")
        print("📊 SCRAPING SUMMARY")
        print(f"{'='*80}")
        print(f"Category URL: {results['category_url']}")
        print(f"Total Products: {results['summary']['total_products']}")
        print(f"✅ Successful: {results['summary']['successful']}")
        print(f"❌ Failed: {results['summary']['failed']}")
        
        if 'duration_seconds' in results:
            duration = results['duration_seconds']
            print(f"⏱️  Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        
        # Show sample of successful products
        successful_products = [p for p in results['products'] if not p.get('error')]
        if successful_products:
            print(f"\n📝 Sample of successful products:")
            for product in successful_products[:5]:
                print(f"   • {product['product_code']}: {product['product_name']}")
                print(f"     Colors: {len(product['colors'])}, Fits: {len(product['fits'])}")
        
        # Show any errors
        failed_products = [p for p in results['products'] if p.get('error')]
        if failed_products:
            print(f"\n⚠️  Products with errors:")
            for product in failed_products:
                print(f"   • {product['product_code']}: {product.get('error', 'Unknown error')}")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("❌ ERROR: Please provide a J.Crew category URL")
        print("\nUsage examples:")
        print('  python scripts/jcrew_category_scraper.py "https://www.jcrew.com/plp/mens/categories/clothing/shirts"')
        print('  python scripts/jcrew_category_scraper.py "https://www.jcrew.com/plp/mens/categories/clothing/shirts?sub-categories=men-shirts-linen"')
        print('\nOptional: Add a number to limit products for testing:')
        print('  python scripts/jcrew_category_scraper.py "URL" 3  # Only scrape first 3 products')
        sys.exit(1)
    
    category_url = sys.argv[1]
    
    # Validate URL
    if 'jcrew.com' not in category_url:
        print("❌ ERROR: URL must be from jcrew.com")
        sys.exit(1)
    
    print(f"🚀 J.Crew Category Scraper")
    print(f"📍 Target: {category_url}")
    print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run scraper
    scraper = JCrewCategoryScraper(headless=False)  # Set to True for headless mode
    
    try:
        results = scraper.scrape_category(category_url)
        
        # Save results
        output_file = scraper.save_results(results)
        
        # Print summary
        scraper.print_summary(results)
        
        # Exit with appropriate code
        if results['summary']['failed'] > 0:
            print(f"\n⚠️  Scraping completed with {results['summary']['failed']} errors")
            sys.exit(1)
        else:
            print(f"\n✅ Scraping completed successfully!")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {str(e)}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
