#!/usr/bin/env python3
"""Compare fresh scrape results with database data"""

import sys
import os
import json
import time
from datetime import datetime

# Add paths
sys.path.append('/Users/seandavey/projects/V10')
sys.path.append('/Users/seandavey/projects/V10/scripts')

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class ScraperComparison:
    def __init__(self, headless=True):
        """Initialize the scraper with Selenium"""
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    def extract_fit_options(self, url, product_code):
        """Extract fit options from a product page"""
        try:
            print(f"\n   🔍 Loading {product_code}...")
            self.driver.get(url)
            time.sleep(3)  # Let page load
            
            fit_options = []
            
            # Method 1: Look for fit list structure (most reliable)
            try:
                fit_list = self.driver.find_element(By.CSS_SELECTOR, 'ul[aria-label="Fit List"]')
                buttons = fit_list.find_elements(By.CSS_SELECTOR, 'button')
                for button in buttons:
                    fit_name = button.get_attribute('aria-label') or button.text
                    if fit_name:
                        fit_name = fit_name.strip()
                        fit_name = fit_name.replace(', selected', '').replace(' selected', '')
                        fit_name = fit_name.replace(', is unavailable', '').replace(' unavailable', '')
                        if fit_name and fit_name not in fit_options:
                            fit_options.append(fit_name)
            except:
                pass
            
            # Method 2: Look for fit buttons with IDs
            if not fit_options:
                try:
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, 'button[id*="__fit-button"]')
                    for button in buttons:
                        button_id = button.get_attribute('id')
                        if '__fit-button' in button_id:
                            fit_name = button_id.split('__fit-button')[0].split('__')[-1]
                            fit_name = fit_name.replace('-', ' ').title()
                            if fit_name and fit_name not in fit_options:
                                fit_options.append(fit_name)
                except:
                    pass
            
            return fit_options if fit_options else None
            
        except Exception as e:
            print(f"   ❌ Error extracting fits: {e}")
            return None
    
    def extract_colors(self, url, product_code):
        """Extract color options from a product page"""
        try:
            # Already on the page from fit extraction
            colors = []
            
            # Look for color swatches
            try:
                color_list = self.driver.find_element(By.CSS_SELECTOR, 'ul[aria-label="Color List"], div[data-testid="color-selector"]')
                color_buttons = color_list.find_elements(By.CSS_SELECTOR, 'button, a')
                
                for button in color_buttons:
                    color_name = button.get_attribute('aria-label') or button.get_attribute('data-color') or button.get_attribute('title')
                    if color_name:
                        color_name = color_name.replace('Select ', '').replace(' color', '').strip()
                        if color_name and color_name not in colors:
                            colors.append(color_name)
            except:
                pass
            
            # Alternative: Look for color text
            if not colors:
                try:
                    color_elements = self.driver.find_elements(By.CSS_SELECTOR, '[class*="color-name"], [data-testid*="color"]')
                    for elem in color_elements[:5]:  # Limit to avoid noise
                        text = elem.text.strip()
                        if text and len(text) < 30 and text not in colors:
                            colors.append(text)
                except:
                    pass
            
            return colors if colors else None
            
        except Exception as e:
            print(f"   ❌ Error extracting colors: {e}")
            return None
    
    def compare_product(self, product_data):
        """Compare scraped data with database data"""
        code = product_data['product_code']
        url = product_data['product_url']
        db_fits = product_data['db_fits']
        db_colors = product_data['db_colors']
        
        print(f"\n{'='*80}")
        print(f"Testing: {code} - {product_data.get('product_name', 'Unknown')[:50]}...")
        print(f"URL: {url[:80]}...")
        
        # Extract fresh data
        scraped_fits = self.extract_fit_options(url, code)
        scraped_colors = self.extract_colors(url, code)
        
        # Compare fits
        print(f"\n   📐 FIT OPTIONS COMPARISON:")
        print(f"      Database:  {db_fits if db_fits else 'None'}")
        print(f"      Scraped:   {scraped_fits if scraped_fits else 'None (single fit product)'}")
        
        if db_fits and scraped_fits:
            if set(db_fits) == set(scraped_fits):
                print(f"      ✅ MATCH - Fits are consistent!")
            else:
                print(f"      ⚠️ MISMATCH - Fits differ!")
                missing_in_scrape = set(db_fits) - set(scraped_fits) if scraped_fits else set(db_fits)
                missing_in_db = set(scraped_fits) - set(db_fits) if db_fits else set(scraped_fits)
                if missing_in_scrape:
                    print(f"         Missing from scrape: {missing_in_scrape}")
                if missing_in_db:
                    print(f"         Missing from DB: {missing_in_db}")
        elif not db_fits and not scraped_fits:
            print(f"      ✅ MATCH - Both show single fit product")
        elif not db_fits and scraped_fits:
            print(f"      🔄 UPDATE NEEDED - DB missing fits that exist on site")
        elif db_fits and not scraped_fits:
            print(f"      ⚠️ INVESTIGATE - DB has fits but scraper found none")
        
        # Compare colors
        print(f"\n   🎨 COLOR OPTIONS COMPARISON:")
        print(f"      Database:  {len(db_colors) if db_colors else 0} colors")
        print(f"      Scraped:   {len(scraped_colors) if scraped_colors else 0} colors")
        
        if db_colors and scraped_colors:
            db_color_set = set([c.lower() for c in db_colors])
            scraped_color_set = set([c.lower() for c in scraped_colors])
            
            if len(db_color_set.intersection(scraped_color_set)) > 0:
                print(f"      ✅ Some overlap found")
            else:
                print(f"      ⚠️ No matching colors")
        
        if scraped_colors:
            print(f"      Scraped colors: {scraped_colors[:5]}")
        
        return {
            'product_code': code,
            'fits_match': (set(db_fits) == set(scraped_fits)) if (db_fits and scraped_fits) else (not db_fits and not scraped_fits),
            'db_fits': db_fits,
            'scraped_fits': scraped_fits,
            'db_colors': db_colors,
            'scraped_colors': scraped_colors
        }
    
    def run_comparison(self):
        """Run comparison for all test products"""
        # Load test products
        with open('test_products.json', 'r') as f:
            products = json.load(f)
        
        print("\n" + "="*80)
        print("STARTING SCRAPER COMPARISON TEST")
        print("="*80)
        
        results = []
        for product in products:
            result = self.compare_product(product)
            results.append(result)
            time.sleep(2)  # Be nice to the server
        
        # Summary
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        
        fits_match_count = sum(1 for r in results if r['fits_match'])
        print(f"\n✅ Fits Match: {fits_match_count}/{len(results)}")
        
        for result in results:
            code = result['product_code']
            if result['fits_match']:
                print(f"   ✅ {code}: Fits are consistent")
            else:
                print(f"   ⚠️ {code}: Fits differ - DB: {result['db_fits']} vs Scraped: {result['scraped_fits']}")
        
        # Save results
        with open('scraper_comparison_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📝 Detailed results saved to scraper_comparison_results.json")
        
        self.driver.quit()

if __name__ == "__main__":
    scraper = ScraperComparison(headless=True)
    scraper.run_comparison()
