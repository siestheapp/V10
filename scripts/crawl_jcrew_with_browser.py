#!/usr/bin/env python3
"""
Browse J.Crew linen shirts page using Selenium to extract actual product URLs
Acts like a human browsing the site
"""

import time
import json
import sys
import os

# Try to import selenium, provide installation instructions if not available
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
except ImportError:
    print("❌ Selenium not installed!")
    print("\nTo install, run:")
    print("pip install selenium")
    print("\nYou also need Chrome browser and ChromeDriver installed.")
    print("On Mac with Homebrew: brew install chromedriver")
    sys.exit(1)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def setup_driver():
    """Setup Chrome driver with options to avoid detection"""
    chrome_options = Options()
    
    # Run in headless mode (no GUI) - comment out to see the browser
    # chrome_options.add_argument("--headless")
    
    # Avoid detection
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Set window size
    chrome_options.add_argument("--window-size=1920,1080")
    
    # User agent
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        # Remove webdriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    except Exception as e:
        print(f"❌ Error setting up Chrome driver: {e}")
        print("\nMake sure Chrome and ChromeDriver are installed:")
        print("brew install --cask google-chrome")
        print("brew install chromedriver")
        sys.exit(1)

def extract_product_urls(driver, url):
    """Navigate to page and extract product URLs"""
    
    print(f"🌐 Opening J.Crew linen shirts page...")
    driver.get(url)
    
    # Wait for page to load
    time.sleep(3)
    
    # Accept cookies if popup appears
    try:
        cookie_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Accept')]")
        cookie_button.click()
        print("🍪 Accepted cookies")
        time.sleep(1)
    except:
        pass
    
    # Scroll to load all products (lazy loading)
    print("📜 Scrolling to load all products...")
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        # Scroll down
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        # Check if new content loaded
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    
    print("🔍 Extracting product links...")
    
    product_urls = set()
    
    # Method 1: Find product tiles/cards and extract links
    try:
        # Common selectors for product tiles
        selectors = [
            "a[href*='/p/mens/']",
            "a[href*='/p/'][href*='shirt']",
            ".product-tile a",
            ".product-card a",
            "[data-testid='product-tile'] a",
            "article a[href*='/p/']"
        ]
        
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    href = element.get_attribute('href')
                    if href and '/p/' in href:
                        # Clean URL
                        clean_url = href.split('?')[0]
                        product_urls.add(clean_url)
            except:
                continue
    except Exception as e:
        print(f"⚠️ Error extracting links: {e}")
    
    # Method 2: Extract from JavaScript data
    try:
        # Look for product data in page JavaScript
        scripts = driver.find_elements(By.TAG_NAME, 'script')
        for script in scripts:
            content = script.get_attribute('innerHTML')
            if content and 'product' in content.lower():
                # Look for product URLs in JSON
                import re
                urls = re.findall(r'"url"\s*:\s*"([^"]*\/p\/[^"]*)"', content)
                for url in urls:
                    if url.startswith('/'):
                        url = f"https://www.jcrew.com{url}"
                    product_urls.add(url.split('?')[0])
    except:
        pass
    
    # Method 3: Get product names and codes
    product_info = []
    try:
        # Find product names and extract codes
        name_selectors = [
            ".product-name",
            ".product-tile__name",
            "[data-testid='product-name']",
            "h3.product-title",
            "a[href*='/p/'] h3",
            "a[href*='/p/'] span"
        ]
        
        for selector in name_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    text = element.text.strip()
                    if text and 'linen' in text.lower():
                        # Try to get the parent link
                        parent = element.find_element(By.XPATH, "./ancestor::a[@href]")
                        href = parent.get_attribute('href')
                        if href:
                            product_urls.add(href.split('?')[0])
                            product_info.append({
                                'name': text,
                                'url': href.split('?')[0]
                            })
            except:
                continue
    except:
        pass
    
    return list(product_urls), product_info

def process_with_fetcher(urls):
    """Process URLs with the JCrewProductFetcher"""
    from src.ios_app.Backend.jcrew_fetcher import JCrewProductFetcher
    
    fetcher = JCrewProductFetcher()
    results = []
    
    print(f"\n🔄 Processing {len(urls)} products with fetcher...")
    
    for i, url in enumerate(urls[:10], 1):  # Process first 10 for testing
        print(f"\n[{i}/10] {url.split('/')[-1]}...")
        
        try:
            product_data = fetcher.fetch_product(url)
            if product_data:
                colors = product_data.get('colors_available', [])
                print(f"   ✅ {product_data.get('product_name', 'Unknown')}")
                print(f"   Colors: {len(colors) if isinstance(colors, list) else 0}")
                
                results.append({
                    'url': url,
                    'code': product_data.get('product_code'),
                    'name': product_data.get('product_name'),
                    'colors': colors
                })
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:50]}")
        
        time.sleep(1)  # Be polite
    
    return results

def main():
    print("=" * 60)
    print("J.CREW BROWSER AUTOMATION CRAWLER")
    print("=" * 60)
    
    # Setup browser
    driver = setup_driver()
    
    try:
        # Navigate to linen shirts page
        url = "https://www.jcrew.com/plp/mens/categories/clothing/shirts?sub-categories=men-shirts-linen"
        urls, product_info = extract_product_urls(driver, url)
        
        print(f"\n✅ Found {len(urls)} product URLs")
        
        if urls:
            print("\nFirst 10 URLs found:")
            for url in urls[:10]:
                print(f"  - {url}")
            
            # Save URLs
            with open('jcrew_linen_urls_browser.txt', 'w') as f:
                for url in urls:
                    f.write(f"{url}\n")
            print(f"\n💾 Saved all URLs to jcrew_linen_urls_browser.txt")
            
            # Save product info if found
            if product_info:
                with open('jcrew_linen_products_browser.json', 'w') as f:
                    json.dump(product_info, f, indent=2)
                print(f"💾 Saved product info to jcrew_linen_products_browser.json")
            
            # Process with fetcher
            results = process_with_fetcher(urls)
            
            if results:
                with open('jcrew_linen_with_colors.json', 'w') as f:
                    json.dump(results, f, indent=2)
                print(f"\n💾 Saved {len(results)} products with color data to jcrew_linen_with_colors.json")
        
    finally:
        print("\n🔚 Closing browser...")
        driver.quit()

if __name__ == "__main__":
    main()

