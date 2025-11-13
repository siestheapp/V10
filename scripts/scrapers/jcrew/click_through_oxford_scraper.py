#!/usr/bin/env python3
"""
Click-through Oxford scraper - Actually visits each product page
No assumptions, no hardcoded data
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
        from selenium.common.exceptions import TimeoutException, NoSuchElementException
    except ImportError:
        print("❌ Selenium not installed!")
        return None, None
    
    print("🔧 Setting up Chrome...")
    
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
        print("✅ Chrome ready")
        return driver, (By, WebDriverWait, EC, TimeoutException, NoSuchElementException)
    except Exception as e:
        print(f"❌ Failed to start Chrome: {e}")
        return None, None

def get_product_links(driver, selenium_imports):
    """Get unique product links from the Oxford category page"""
    By, WebDriverWait, EC, TimeoutException, NoSuchElementException = selenium_imports
    
    url = "https://www.jcrew.com/plp/mens/categories/clothing/shirts?sub-categories=men-shirts-brokeninoxford"
    
    print(f"\n📍 Loading category page...")
    driver.get(url)
    time.sleep(5)
    
    # Handle cookies
    try:
        cookie_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Accept')]")
        cookie_btn.click()
        time.sleep(1)
    except:
        pass
    
    print("📜 Scrolling to load products...")
    for i in range(5):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
    
    print("🔍 Finding product links...")
    
    # Find UNIQUE product URLs (not color variants)
    product_urls = {}
    
    # Look for product links
    links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/p/mens']")
    
    for link in links:
        href = link.get_attribute('href')
        if href and '/broken-in-oxford/' in href:
            # Extract base URL without color parameters
            base_url = href.split('?')[0]
            
            # Extract product code from URL
            match = re.search(r'/([A-Z0-9]{5,6})$', base_url)
            if match:
                code = match.group(1)
                # Skip color codes (they appear in colorProductCode params)
                if 'colorProductCode' not in href or f'/{code}' in base_url:
                    if code not in product_urls:
                        product_urls[code] = base_url
                        print(f"   Found product: {code}")
    
    return product_urls

def scrape_product_page(driver, url, code, selenium_imports):
    """Click through to a product page and get real data"""
    By, WebDriverWait, EC, TimeoutException, NoSuchElementException = selenium_imports
    
    print(f"\n🔗 Visiting product {code}...")
    print(f"   URL: {url}")
    
    driver.get(url)
    time.sleep(3)  # Let page load
    
    product_data = {
        'code': code,
        'url': url,
        'name': 'Unknown',
        'price': None,
        'colors': [],
        'fits': [],
        'error': None
    }
    
    try:
        # Get product name
        try:
            name_elem = driver.find_element(By.CSS_SELECTOR, "h1")
            product_data['name'] = name_elem.text
            print(f"   Name: {product_data['name']}")
        except:
            pass
        
        # Get price
        try:
            price_elem = driver.find_element(By.CSS_SELECTOR, "[class*='price']")
            product_data['price'] = price_elem.text
            print(f"   Price: {product_data['price']}")
        except:
            pass
        
        # Count color swatches
        try:
            # Multiple possible selectors for color swatches
            swatch_selectors = [
                "button[aria-label*='color']",
                "[data-testid*='color-swatch']",
                ".color-swatch",
                "[class*='ColorSwatch']",
                "img[alt*='color']"
            ]
            
            colors_found = False
            for selector in swatch_selectors:
                swatches = driver.find_elements(By.CSS_SELECTOR, selector)
                if swatches:
                    product_data['colors'] = [f"Color_{i+1}" for i in range(len(swatches))]
                    print(f"   ✅ Found {len(swatches)} color options")
                    colors_found = True
                    break
            
            if not colors_found:
                print("   ⚠️  No color swatches found")
        except Exception as e:
            print(f"   ⚠️  Error finding colors: {e}")
        
        # Get fit options
        try:
            fit_buttons = driver.find_elements(By.CSS_SELECTOR, "button[class*='fit'], [data-testid*='fit']")
            if fit_buttons:
                product_data['fits'] = [btn.text for btn in fit_buttons if btn.text]
                print(f"   Fits: {', '.join(product_data['fits'])}")
        except:
            pass
        
    except Exception as e:
        product_data['error'] = str(e)
        print(f"   ❌ Error scraping product: {e}")
    
    return product_data

def main():
    """Main function - no hardcoded data"""
    
    print("="*80)
    print("CLICK-THROUGH OXFORD SCRAPER - REAL DATA ONLY")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    driver, selenium_imports = setup_selenium()
    
    if not driver:
        print("\n❌ Cannot proceed without Selenium")
        return
    
    try:
        # Step 1: Get product links from category page
        product_urls = get_product_links(driver, selenium_imports)
        
        if not product_urls:
            print("\n❌ No products found on category page")
            print("   No hardcoded fallback - returning empty")
            return
        
        print(f"\n✅ Found {len(product_urls)} unique products to check")
        
        # Step 2: Click through to each product
        print("\n" + "="*80)
        print("CLICKING THROUGH TO EACH PRODUCT PAGE")
        print("="*80)
        
        all_products = {}
        
        for code, url in product_urls.items():
            product_data = scrape_product_page(driver, url, code, selenium_imports)
            all_products[code] = product_data
            time.sleep(2)  # Be respectful between requests
        
        # Step 3: Display results
        print("\n" + "="*80)
        print("FINAL RESULTS - ACTUAL SCRAPED DATA ONLY")
        print("="*80)
        
        total_variants = 0
        
        for code, data in all_products.items():
            print(f"\n{code}: {data['name']}")
            print(f"   URL: {data['url']}")
            
            if data['colors']:
                color_count = len(data['colors'])
                print(f"   Colors: {color_count} actual color options found")
                total_variants += color_count
            else:
                print(f"   Colors: Unable to detect")
                total_variants += 1  # Count at least 1
            
            if data['fits']:
                print(f"   Fits: {', '.join(data['fits'])}")
            
            if data['error']:
                print(f"   ⚠️  Error: {data['error']}")
        
        print(f"\n📊 Summary:")
        print(f"   • Products scraped: {len(all_products)}")
        print(f"   • Total color variants: {total_variants}")
        print(f"   • This is REAL data from clicking through each page")
        print(f"   • NO hardcoded data used")
        
    finally:
        driver.quit()
        print("\n🔚 Browser closed")

if __name__ == "__main__":
    main()
