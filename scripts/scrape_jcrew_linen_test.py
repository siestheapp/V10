#!/usr/bin/env python3
"""
Test scrape of J.Crew Men's Linen Shirts category
Compares with database and uses safe import process
"""

import sys
import time
import json
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

sys.path.append('/Users/seandavey/projects/V10')
import psycopg2
from db_config import DB_CONFIG

class JCrewLinenScraper:
    def __init__(self, headless=True):
        self.setup_driver(headless)
        self.products_found = {}
        
    def setup_driver(self, headless):
        """Setup Selenium driver with anti-detection"""
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    def extract_product_code(self, element):
        """Extract product code from various sources"""
        # Try href first
        try:
            href = element.find_element(By.TAG_NAME, 'a').get_attribute('href')
            if href:
                # Look for product code patterns
                patterns = [
                    r'/([A-Z]{2}\d{3,4})(?:\?|$)',
                    r'/p/.*/([A-Z]{2}\d{3,4})(?:\?|$)',
                ]
                for pattern in patterns:
                    match = re.search(pattern, href)
                    if match:
                        return match.group(1), href
        except:
            pass
        return None, None
    
    def scrape_linen_products(self, url):
        """Scrape all linen products from the page"""
        print("=" * 80)
        print("SCRAPING J.CREW MEN'S LINEN SHIRTS")
        print("=" * 80)
        print(f"URL: {url}\n")
        
        self.driver.get(url)
        time.sleep(3)  # Let page load
        
        # Wait for products to load
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[class*="product"], article'))
            )
        except TimeoutException:
            print("⚠️ Timeout waiting for products")
        
        # Scroll to load all products
        print("📜 Scrolling to load all products...")
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        
        # Extract products
        print("\n🔍 Extracting product information...")
        product_elements = self.driver.find_elements(By.CSS_SELECTOR, '[class*="product-tile"], [class*="product-card"], article')
        
        for element in product_elements:
            try:
                # Get product code and URL
                code, product_url = self.extract_product_code(element)
                if not code:
                    continue
                
                # Get product name
                name = None
                for selector in ['h3', 'h4', '[class*="name"]', '[class*="title"]']:
                    try:
                        name_elem = element.find_element(By.CSS_SELECTOR, selector)
                        name = name_elem.text.strip()
                        if name:
                            break
                    except:
                        continue
                
                # Get price
                price = None
                try:
                    price_elem = element.find_element(By.CSS_SELECTOR, '[class*="price"]')
                    price = price_elem.text.strip()
                except:
                    pass
                
                # Get fit options (from text on listing page)
                fits = []
                try:
                    # Look for fit text in the product tile
                    text = element.text.lower()
                    if 'classic' in text:
                        fits.append('Classic')
                    if 'slim untucked' in text:
                        fits.append('Slim Untucked')
                    elif 'slim' in text:
                        fits.append('Slim')
                    if 'tall' in text:
                        fits.append('Tall')
                    if 'relaxed' in text:
                        fits.append('Relaxed')
                except:
                    pass
                
                # Get colors (look for swatches)
                colors = []
                try:
                    color_elements = element.find_elements(By.CSS_SELECTOR, '[aria-label*="Color"], img[alt*="color"], [class*="swatch"]')
                    for color_elem in color_elements[:10]:  # Limit to avoid too many
                        color_text = color_elem.get_attribute('aria-label') or color_elem.get_attribute('alt') or ''
                        if color_text and len(color_text) < 50:
                            colors.append(color_text.strip())
                except:
                    pass
                
                # Store product
                if code not in self.products_found:
                    self.products_found[code] = {
                        'product_code': code,
                        'product_name': name or f'Linen Shirt {code}',
                        'product_url': product_url,
                        'price': price,
                        'fit_options': list(set(fits)) if fits else None,
                        'colors': list(set(colors)) if colors else None,
                        'category': 'Casual Shirts',
                        'subcategory': 'Linen'
                    }
                    print(f"   Found: {code} - {name[:40] if name else 'Unknown'}...")
                
            except Exception as e:
                print(f"   Error processing element: {e}")
                continue
        
        print(f"\n✅ Found {len(self.products_found)} unique products")
        return list(self.products_found.values())
    
    def compare_with_database(self):
        """Compare scraped products with database"""
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        print("\n" + "=" * 80)
        print("COMPARING WITH DATABASE")
        print("=" * 80)
        
        # Get existing products
        product_codes = list(self.products_found.keys())
        placeholders = ','.join(['%s'] * len(product_codes))
        
        cur.execute(f"""
            SELECT product_code, product_name, fit_options, colors_available, product_url
            FROM jcrew_product_cache
            WHERE product_code IN ({placeholders})
        """, product_codes)
        
        existing = {row[0]: row for row in cur.fetchall()}
        
        # Analyze differences
        new_products = []
        needs_update = []
        up_to_date = []
        
        for code, product in self.products_found.items():
            if code not in existing:
                new_products.append(product)
            else:
                db_code, db_name, db_fits, db_colors, db_url = existing[code]
                
                # Check if update needed
                update_needed = False
                reasons = []
                
                if not db_name and product['product_name']:
                    update_needed = True
                    reasons.append('missing name')
                
                if not db_fits and product['fit_options']:
                    update_needed = True
                    reasons.append('missing fits')
                
                if not db_colors and product['colors']:
                    update_needed = True
                    reasons.append('missing colors')
                
                if update_needed:
                    product['update_reasons'] = reasons
                    needs_update.append(product)
                else:
                    up_to_date.append(product)
        
        # Report findings
        print(f"\n📊 Analysis Results:")
        print(f"   ✅ Up to date: {len(up_to_date)} products")
        print(f"   🆕 New products: {len(new_products)} products")
        print(f"   🔄 Need update: {len(needs_update)} products")
        
        if new_products:
            print(f"\n🆕 New Products to Add:")
            for p in new_products[:5]:  # Show first 5
                print(f"   - {p['product_code']}: {p['product_name'][:40]}...")
        
        if needs_update:
            print(f"\n🔄 Products Needing Update:")
            for p in needs_update[:5]:  # Show first 5
                print(f"   - {p['product_code']}: {', '.join(p['update_reasons'])}")
        
        cur.close()
        conn.close()
        
        return {
            'new': new_products,
            'update': needs_update,
            'current': up_to_date
        }
    
    def save_results(self, comparison):
        """Save results to JSON for review"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'jcrew_linen_test_{timestamp}.json'
        
        with open(filename, 'w') as f:
            json.dump({
                'timestamp': timestamp,
                'url': 'https://www.jcrew.com/plp/mens/categories/clothing/shirts?sub-categories=men-shirts-linen',
                'total_found': len(self.products_found),
                'comparison': comparison,
                'all_products': list(self.products_found.values())
            }, f, indent=2)
        
        print(f"\n📁 Results saved to: {filename}")
        return filename
    
    def cleanup(self):
        """Close the driver"""
        if self.driver:
            self.driver.quit()

def main():
    """Main execution"""
    scraper = JCrewLinenScraper(headless=True)
    
    try:
        # Scrape the linen page
        url = 'https://www.jcrew.com/plp/mens/categories/clothing/shirts?sub-categories=men-shirts-linen'
        products = scraper.scrape_linen_products(url)
        
        # Compare with database
        comparison = scraper.compare_with_database()
        
        # Save results
        filename = scraper.save_results(comparison)
        
        # Summary
        print("\n" + "=" * 80)
        print("SCRAPE COMPLETE")
        print("=" * 80)
        print(f"Total products found: {len(products)}")
        print(f"New products to add: {len(comparison['new'])}")
        print(f"Products needing update: {len(comparison['update'])}")
        print(f"Products up to date: {len(comparison['current'])}")
        
        if comparison['new'] or comparison['update']:
            print("\n📝 Next Steps:")
            print(f"1. Review the JSON file: {filename}")
            print("2. Use staging import to add/update products:")
            print("   python scripts/import_jcrew_staging.py " + filename)
        else:
            print("\n✅ Database is up to date!")
        
    finally:
        scraper.cleanup()

if __name__ == "__main__":
    main()
