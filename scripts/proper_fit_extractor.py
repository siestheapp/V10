#!/usr/bin/env python3
"""
PROPER fit option extraction - visits each product page individually
"""

import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

sys.path.append('/Users/seandavey/projects/V10')
import psycopg2
from db_config import DB_CONFIG

class ProperFitExtractor:
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
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    def extract_fit_options_for_product(self, product_url):
        """Extract ACTUAL fit options for a specific product"""
        try:
            print(f"  Loading: {product_url}")
            self.driver.get(product_url)
            time.sleep(3)  # Let page fully load
            
            fit_options = []
            
            # Method 1: Look for fit selector buttons
            try:
                # Wait for fit options to be present
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 
                        "button[aria-label*='fit'], button[data-testid*='fit'], .fit-selector button"))
                )
                
                # Find all fit buttons
                fit_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                    "button[aria-label*='Classic'], button[aria-label*='Slim'], "
                    "button[aria-label*='Tall'], button[aria-label*='Relaxed'], "
                    "button[aria-label*='Untucked']")
                
                for button in fit_buttons:
                    fit_text = button.get_attribute('aria-label') or button.text
                    if fit_text and fit_text not in fit_options:
                        # Clean the text (remove "Select" or other prefixes)
                        fit_text = fit_text.replace('Select ', '').strip()
                        if any(word in fit_text for word in ['Classic', 'Slim', 'Tall', 'Relaxed', 'Untucked']):
                            fit_options.append(fit_text)
                            print(f"    Found fit: {fit_text}")
            except:
                pass
            
            # Method 2: Check for fit links in navigation
            if not fit_options:
                fit_links = self.driver.find_elements(By.CSS_SELECTOR, 
                    "a[href*='fit=Classic'], a[href*='fit=Slim'], a[href*='fit=Tall']")
                
                for link in fit_links:
                    href = link.get_attribute('href')
                    if 'fit=' in href:
                        # Extract fit from URL
                        import re
                        match = re.search(r'fit=([^&]+)', href)
                        if match:
                            fit = match.group(1)
                            if fit not in fit_options:
                                fit_options.append(fit)
                                print(f"    Found fit in link: {fit}")
            
            # Method 3: Look in product variation selectors
            if not fit_options:
                variations = self.driver.find_elements(By.CSS_SELECTOR, 
                    "[data-variation-type='fit'] button, .product-variation--fit button")
                
                for var in variations:
                    fit_text = var.text.strip()
                    if fit_text and fit_text not in fit_options:
                        fit_options.append(fit_text)
                        print(f"    Found fit in variations: {fit_text}")
            
            return fit_options if fit_options else None
            
        except Exception as e:
            print(f"    Error: {e}")
            return None
    
    def close(self):
        """Close the driver"""
        self.driver.quit()

def main():
    """
    Properly extract fit options for J.Crew products
    """
    print("🎯 PROPER FIT EXTRACTION (Individual Product Pages)")
    print("="*60)
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # Get a sample of products to test
    # In production, you'd do ALL products, but let's test with a few
    cur.execute("""
        SELECT product_code, product_name, product_url
        FROM jcrew_product_cache 
        WHERE product_url IS NOT NULL
        ORDER BY product_code
        LIMIT 5
    """)
    
    products = cur.fetchall()
    print(f"Testing {len(products)} products...")
    
    extractor = ProperFitExtractor(headless=True)
    updates = []
    
    try:
        for code, name, url in products:
            print(f"\n📦 {code}: {name[:40]}")
            
            # Extract actual fit options
            fit_options = extractor.extract_fit_options_for_product(url)
            
            if fit_options:
                print(f"  ✅ Found {len(fit_options)} fits: {fit_options}")
                updates.append((code, fit_options))
            else:
                print(f"  ⚠️ No fits found (may not have fit variations)")
    
    finally:
        extractor.close()
    
    # Update database with ACTUAL fit options
    if updates:
        print(f"\n💾 Updating {len(updates)} products with real fit data...")
        for code, fits in updates:
            cur.execute("""
                UPDATE jcrew_product_cache 
                SET fit_options = %s,
                    updated_at = NOW()
                WHERE product_code = %s
            """, (fits, code))
        
        conn.commit()
        print("✅ Database updated with actual fit options")
    
    cur.close()
    conn.close()
    
    print("\n" + "="*60)
    print("This is how fit extraction SHOULD work:")
    print("1. Visit each product page individually")
    print("2. Extract only the fits actually available")
    print("3. Store product-specific fit options")
    print("="*60)

if __name__ == "__main__":
    main()

