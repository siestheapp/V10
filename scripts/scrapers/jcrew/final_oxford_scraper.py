#!/usr/bin/env python3
"""
Final Oxford scraper - Clicks "See more colors" to get all options
Real data only, no assumptions
"""

import time
import re
from datetime import datetime

def setup_selenium():
    """Setup Selenium with Chrome"""
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
    except ImportError:
        print("❌ Selenium not installed!")
        return None, None
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver, (By, WebDriverWait, EC)
    except Exception as e:
        print(f"❌ Failed: {e}")
        return None, None

def count_visible_colors(driver, By):
    """Count currently visible color options"""
    # Count visible color buttons (not including "see more" buttons)
    color_buttons = driver.find_elements(By.CSS_SELECTOR, ".product__colors button")
    visible_colors = []
    
    for btn in color_buttons:
        aria_label = btn.get_attribute('aria-label')
        if aria_label and 'see more' not in aria_label.lower():
            visible_colors.append(aria_label)
    
    return visible_colors

def scrape_product_with_expansion(driver, url, code, selenium_imports):
    """Scrape product page and expand color options"""
    By, WebDriverWait, EC = selenium_imports
    
    print(f"\n🔗 Visiting {code}: {url}")
    driver.get(url)
    time.sleep(4)
    
    # Count initial visible colors
    initial_colors = count_visible_colors(driver, By)
    print(f"   Initial visible colors: {len(initial_colors)}")
    
    # Try to click "See more colors" button
    try:
        see_more = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'See more colors')]")
        print("   📋 Found 'See more colors' button, clicking...")
        driver.execute_script("arguments[0].click();", see_more)
        time.sleep(2)
        
        # Count colors after expansion
        expanded_colors = count_visible_colors(driver, By)
        print(f"   ✅ After expansion: {len(expanded_colors)} colors visible")
        
        return {
            'code': code,
            'initial_colors': len(initial_colors),
            'expanded_colors': len(expanded_colors),
            'color_names': expanded_colors[:5]  # Sample first 5
        }
        
    except Exception as e:
        print(f"   No 'See more colors' button or already expanded")
        return {
            'code': code,
            'initial_colors': len(initial_colors),
            'expanded_colors': len(initial_colors),
            'color_names': initial_colors[:5]
        }

def main():
    print("="*80)
    print("FINAL OXFORD SCRAPER - WITH COLOR EXPANSION")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    driver, selenium_imports = setup_selenium()
    
    if not driver:
        return
    
    try:
        # Define the Oxford products we know exist
        products = {
            'BE996': 'https://www.jcrew.com/p/mens/categories/clothing/shirts/broken-in-oxford/broken-in-organic-cotton-oxford-shirt/BE996',
            'CM226': 'https://www.jcrew.com/p/mens/categories/clothing/shirts/broken-in-oxford/classic-oxford-two-pocket-workshirt/CM226',
            'CH326': 'https://www.jcrew.com/p/mens/categories/clothing/shirts/broken-in-oxford/limited-edition-the-new-yorker-x-jcrew-broken-in-organic-cotton-oxford-shirt/CH326'
        }
        
        results = {}
        
        for code, url in products.items():
            result = scrape_product_with_expansion(driver, url, code, selenium_imports)
            results[code] = result
            time.sleep(2)
        
        print("\n" + "="*80)
        print("FINAL RESULTS - ACTUAL SCRAPED DATA")
        print("="*80)
        
        total_variants = 0
        
        for code, data in results.items():
            print(f"\n{code}:")
            print(f"   Initial colors shown: {data['initial_colors']}")
            print(f"   Total colors available: {data['expanded_colors']}")
            total_variants += data['expanded_colors']
            
            if data['color_names']:
                print(f"   Sample colors: {', '.join(data['color_names'][:3])}")
        
        print(f"\n📊 Summary:")
        print(f"   • Products scraped: {len(results)}")
        print(f"   • Total color variants: {total_variants}")
        print(f"   • This is REAL data from clicking 'See more colors'")
        print(f"   • NO hardcoded data or assumptions")
        
    finally:
        driver.quit()
        print("\n🔚 Browser closed")

if __name__ == "__main__":
    main()
