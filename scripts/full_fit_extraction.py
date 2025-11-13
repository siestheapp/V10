#!/usr/bin/env python3
"""
Full fit option extraction for all J.Crew products
"""

import sys
import time
import re
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime

sys.path.append('/Users/seandavey/projects/V10')
import psycopg2
from db_config import DB_CONFIG

class FullFitExtractor:
    def __init__(self, headless=True):
        """Initialize Selenium driver"""
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Valid J.Crew fit options
        self.valid_fits = ['Classic', 'Slim', 'Tall', 'Relaxed', 'Slim Untucked', 'Untucked', 'Regular', 'Petite']
    
    def clean_url(self, url):
        """Remove fit parameters from URL to get all options"""
        if not url:
            return url
            
        # Remove query parameters that might limit fits
        base_url = url.split('?')[0]
        
        # Remove /classic/, /slim/, etc from path
        for fit in ['classic', 'slim', 'tall', 'relaxed']:
            base_url = base_url.replace(f'/{fit}/', '/').replace(f'/{fit}', '')
        
        return base_url
    
    def extract_fit_options(self, product_url):
        """Extract fit options for a product"""
        try:
            # Clean the URL first
            clean_url = self.clean_url(product_url)
            self.driver.get(clean_url)
            time.sleep(3)  # Let page load
            
            fit_options = []
            
            # Method 1: Look in JavaScript data
            try:
                script = """
                var scripts = document.getElementsByTagName('script');
                for (var i = 0; i < scripts.length; i++) {
                    if (scripts[i].innerHTML.includes('productData') || 
                        scripts[i].innerHTML.includes('variations') ||
                        scripts[i].innerHTML.includes('fitType')) {
                        return scripts[i].innerHTML;
                    }
                }
                return '';
                """
                
                js_content = self.driver.execute_script(script)
                if js_content:
                    for fit in self.valid_fits:
                        # Look for fit in various formats
                        patterns = [
                            f'"{fit}"',
                            f"'{fit}'",
                            f'fit={fit}',
                            f'fitType":"{fit}"',
                            f'fit":"{fit}"'
                        ]
                        for pattern in patterns:
                            if pattern in js_content and fit not in fit_options:
                                fit_options.append(fit)
                                break
                
            except Exception as e:
                pass
            
            # Method 2: Look for fit variation buttons
            if not fit_options:
                try:
                    fit_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                        "button[aria-label*='fit'], "
                        "button[data-variation-name='fit'], "
                        "div[data-variation-type='fit'] button")
                    
                    for button in fit_buttons:
                        aria_label = button.get_attribute('aria-label') or ''
                        button_text = button.text.strip()
                        
                        for fit in self.valid_fits:
                            if fit in aria_label or fit in button_text:
                                if fit not in fit_options:
                                    fit_options.append(fit)
                                    break
                    
                except Exception:
                    pass
            
            # Method 3: Look for fit links
            if not fit_options:
                try:
                    all_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='fit=']")
                    
                    for link in all_links:
                        href = link.get_attribute('href')
                        if href and 'fit=' in href:
                            match = re.search(r'fit=([^&]+)', href)
                            if match:
                                fit = match.group(1).replace('%20', ' ')
                                if fit in self.valid_fits and fit not in fit_options:
                                    fit_options.append(fit)
                    
                except Exception:
                    pass
            
            return fit_options if fit_options else None
            
        except Exception as e:
            print(f"    Error: {e}")
            return None
    
    def close(self):
        """Close the driver"""
        self.driver.quit()

def main():
    print("🚀 FULL FIT EXTRACTION FOR J.CREW PRODUCTS")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # Get all products that need fit extraction
    cur.execute("""
        SELECT product_code, product_name, product_url
        FROM jcrew_product_cache 
        WHERE (fit_options IS NULL OR array_length(fit_options, 1) = 0 OR array_length(fit_options, 1) = 1)
        AND product_url IS NOT NULL
        ORDER BY product_code
    """)
    
    products = cur.fetchall()
    total_products = len(products)
    print(f"\n📊 Found {total_products} products needing fit extraction")
    
    if total_products == 0:
        print("No products need extraction!")
        return
    
    extractor = FullFitExtractor(headless=True)
    successful = 0
    failed = 0
    no_fits = 0
    
    print("\nStarting extraction (this will take a while)...")
    print("-" * 60)
    
    try:
        for i, (code, name, url) in enumerate(products, 1):
            print(f"\n[{i}/{total_products}] {code}: {name[:40]}")
            print(f"  URL: {extractor.clean_url(url)}")
            
            # Extract fit options
            fit_options = extractor.extract_fit_options(url)
            
            if fit_options:
                # Update database
                cur.execute("""
                    UPDATE jcrew_product_cache 
                    SET fit_options = %s,
                        updated_at = NOW()
                    WHERE product_code = %s
                """, (fit_options, code))
                
                print(f"  ✅ Found {len(fit_options)} fits: {', '.join(fit_options)}")
                successful += 1
            elif fit_options is None:
                print(f"  ❌ Extraction failed")
                failed += 1
            else:
                print(f"  ⚪ No fit variations found")
                no_fits += 1
            
            # Rate limiting - random delay between 2-4 seconds
            delay = random.uniform(2, 4)
            if i < total_products:
                print(f"  Waiting {delay:.1f}s before next...")
                time.sleep(delay)
            
            # Commit every 10 products
            if i % 10 == 0:
                conn.commit()
                print(f"\n💾 Progress saved: {i}/{total_products}")
    
    finally:
        extractor.close()
        conn.commit()  # Final commit
    
    # Print summary
    print("\n" + "="*60)
    print("EXTRACTION COMPLETE")
    print("="*60)
    print(f"✅ Successful: {successful}")
    print(f"⚪ No fits found: {no_fits}")
    print(f"❌ Failed: {failed}")
    print(f"Total processed: {total_products}")
    
    # Get final statistics
    cur.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(*) FILTER (WHERE array_length(fit_options, 1) > 0) as has_fits,
            AVG(array_length(fit_options, 1)) as avg_fits
        FROM jcrew_product_cache
    """)
    
    total, has_fits, avg_fits = cur.fetchone()
    print(f"\n📊 DATABASE STATUS:")
    print(f"  Total products: {total}")
    print(f"  Products with fits: {has_fits} ({has_fits/total*100:.1f}%)")
    print(f"  Average fits per product: {avg_fits:.1f}")
    
    # Select random products for spot checking
    print("\n" + "="*60)
    print("🔍 RANDOM PRODUCTS FOR SPOT CHECKING")
    print("="*60)
    
    cur.execute("""
        SELECT product_code, product_name, product_url, fit_options
        FROM jcrew_product_cache 
        WHERE fit_options IS NOT NULL 
        AND array_length(fit_options, 1) > 0
        AND product_url IS NOT NULL
        ORDER BY RANDOM()
        LIMIT 5
    """)
    
    spot_check = cur.fetchall()
    print("\nPlease verify these products:")
    print("-" * 60)
    
    for code, name, url, fits in spot_check:
        print(f"\n📦 {code}: {name[:50]}")
        print(f"   URL: {url}")
        print(f"   DB Fits: {', '.join(fits) if fits else 'None'}")
        print(f"   (Open URL and check if fits match)")
    
    cur.close()
    conn.close()
    
    print("\n" + "="*60)
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()

