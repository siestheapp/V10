#!/usr/bin/env python3
"""
BETTER fit option extraction with more specific selectors for J.Crew
"""

import sys
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

sys.path.append('/Users/seandavey/projects/V10')
import psycopg2
from db_config import DB_CONFIG

class BetterFitExtractor:
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
    
    def extract_fit_options_for_product(self, product_url):
        """Extract ACTUAL fit options for a specific product"""
        try:
            print(f"  Loading: {product_url}")
            self.driver.get(product_url)
            time.sleep(4)  # Let page fully load
            
            fit_options = []
            valid_fits = ['Classic', 'Slim', 'Tall', 'Relaxed', 'Slim Untucked', 'Untucked', 'Regular']
            
            # Method 1: Look for fit variation buttons specifically
            # J.Crew uses a variation selector for fits
            try:
                # Wait for product variations to load
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
                )
                
                # Look for buttons that are specifically fit selectors
                # These usually have aria-label like "Select Classic fit" or similar
                fit_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                    "button[aria-label*='Select'][aria-label*='fit'], "
                    "button[data-variation-name='fit'], "
                    "div[data-variation-type='fit'] button, "
                    "div.product-variation--fit button")
                
                print(f"    Found {len(fit_buttons)} potential fit buttons")
                
                for button in fit_buttons:
                    aria_label = button.get_attribute('aria-label') or ''
                    button_text = button.text.strip()
                    
                    # Extract fit name from aria-label or text
                    for fit in valid_fits:
                        if fit in aria_label or fit in button_text:
                            if fit not in fit_options:
                                fit_options.append(fit)
                                print(f"    ✓ Found fit: {fit}")
                                break
                
            except TimeoutException:
                print("    Timeout waiting for page")
            except Exception as e:
                print(f"    Error with method 1: {e}")
            
            # Method 2: Look for fit links in the URL structure
            if not fit_options:
                try:
                    # Find all links on the page
                    all_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='fit=']")
                    
                    for link in all_links:
                        href = link.get_attribute('href')
                        if href and 'fit=' in href:
                            # Extract fit parameter
                            match = re.search(r'fit=([^&]+)', href)
                            if match:
                                fit = match.group(1).replace('%20', ' ')
                                # Only add if it's a valid fit type
                                if fit in valid_fits and fit not in fit_options:
                                    fit_options.append(fit)
                                    print(f"    ✓ Found fit in URL: {fit}")
                    
                except Exception as e:
                    print(f"    Error with method 2: {e}")
            
            # Method 3: Check for fit radio buttons or select options
            if not fit_options:
                try:
                    # Look for radio buttons for fit selection
                    fit_inputs = self.driver.find_elements(By.CSS_SELECTOR, 
                        "input[type='radio'][name*='fit'], "
                        "input[type='radio'][value*='Classic'], "
                        "input[type='radio'][value*='Slim']")
                    
                    for input_elem in fit_inputs:
                        value = input_elem.get_attribute('value')
                        if value in valid_fits and value not in fit_options:
                            fit_options.append(value)
                            print(f"    ✓ Found fit in radio: {value}")
                    
                    # Also check for select dropdowns
                    fit_selects = self.driver.find_elements(By.CSS_SELECTOR, "select[name*='fit'] option")
                    for option in fit_selects:
                        option_text = option.text.strip()
                        if option_text in valid_fits and option_text not in fit_options:
                            fit_options.append(option_text)
                            print(f"    ✓ Found fit in select: {option_text}")
                            
                except Exception as e:
                    print(f"    Error with method 3: {e}")
            
            # Method 4: Look in the page's JavaScript data
            if not fit_options:
                try:
                    # Execute JavaScript to find product data
                    script = """
                    var scripts = document.getElementsByTagName('script');
                    for (var i = 0; i < scripts.length; i++) {
                        if (scripts[i].innerHTML.includes('productData') || 
                            scripts[i].innerHTML.includes('variations')) {
                            return scripts[i].innerHTML;
                        }
                    }
                    return '';
                    """
                    
                    js_content = self.driver.execute_script(script)
                    if js_content:
                        # Look for fit variations in JSON
                        for fit in valid_fits:
                            if f'"{fit}"' in js_content or f"'{fit}'" in js_content:
                                if fit not in fit_options:
                                    fit_options.append(fit)
                                    print(f"    ✓ Found fit in JS: {fit}")
                    
                except Exception as e:
                    print(f"    Error with method 4: {e}")
            
            # Final validation - only return if we found valid fits
            if fit_options:
                print(f"    ✅ Total valid fits found: {fit_options}")
                return fit_options
            else:
                print(f"    ⚠️ No valid fit options found")
                return None
            
        except Exception as e:
            print(f"    ❌ Error loading page: {e}")
            return None
    
    def close(self):
        """Close the driver"""
        self.driver.quit()

def main():
    """
    Properly extract fit options for J.Crew products
    """
    print("🎯 BETTER FIT EXTRACTION")
    print("="*60)
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # Test with specific products we know should have fit options
    test_products = [
        ('BE996', 'https://www.jcrew.com/p/mens/categories/clothing/shirts/broken-in-oxford/broken-in-organic-cotton-oxford-shirt/BE996'),
        ('BX291', 'https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/bowery-performance-stretch-dress-shirt-with-spread-collar/BX291'),
        ('AZ829', 'https://www.jcrew.com/p/mens/categories/clothing/shirts/classic/broken-in-organic-cotton-oxford-shirt/AZ829'),
    ]
    
    print(f"Testing {len(test_products)} known products...")
    
    extractor = BetterFitExtractor(headless=True)
    updates = []
    
    try:
        for code, url in test_products:
            print(f"\n📦 Product {code}:")
            
            # Extract actual fit options
            fit_options = extractor.extract_fit_options_for_product(url)
            
            if fit_options:
                updates.append((code, fit_options))
            else:
                print(f"    No fits to update")
    
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
            print(f"  Updated {code}: {fits}")
        
        conn.commit()
        print("✅ Database updated with actual fit options")
    
    cur.close()
    conn.close()
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()

