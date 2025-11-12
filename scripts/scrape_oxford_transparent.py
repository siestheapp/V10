#!/usr/bin/env python3
"""
Transparent Oxford scraper - reports failures clearly and uses Selenium
Based on our successful crawl_jcrew_broken_in_oxford_comprehensive.py
"""

import sys
import time
import json
from datetime import datetime

def scrape_with_selenium():
    """Use Selenium to scrape J.Crew Oxford page - same approach as our successful scripts"""
    
    print("="*80)
    print("ATTEMPTING TO SCRAPE J.CREW OXFORD PAGE WITH SELENIUM")
    print("="*80)
    
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
    except ImportError:
        print("\n❌ SCRAPING FAILED: Selenium not installed")
        print("   Install with: pip install selenium")
        print("\n⚠️  Cannot proceed without Selenium")
        return None
    
    # Setup Chrome with anti-detection
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    try:
        print("\n🚀 Starting Chrome browser...")
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    except Exception as e:
        print(f"\n❌ SCRAPING FAILED: Cannot start Chrome driver")
        print(f"   Error: {e}")
        print("\n   Make sure Chrome and ChromeDriver are installed:")
        print("   brew install --cask google-chrome")
        print("   brew install chromedriver")
        return None
    
    url = "https://www.jcrew.com/plp/mens/categories/clothing/shirts?sub-categories=men-shirts-brokeninoxford"
    
    try:
        print(f"\n🌐 Loading: {url}")
        driver.get(url)
        
        # Wait for page load
        print("⏳ Waiting for page to load...")
        time.sleep(5)
        
        # Handle cookie banner if present
        try:
            cookie_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Accept')]")
            cookie_btn.click()
            print("🍪 Accepted cookies")
            time.sleep(1)
        except:
            pass
        
        print("📜 Scrolling to load all products...")
        
        # Scroll to trigger lazy loading
        for i in range(10):
            driver.execute_script("window.scrollBy(0, 300);")
            time.sleep(0.3)
        
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        print("🔍 Extracting product codes...")
        
        product_codes = set()
        
        # Extract all links
        all_links = driver.find_elements(By.TAG_NAME, "a")
        print(f"   Found {len(all_links)} links on page")
        
        for link in all_links:
            href = link.get_attribute('href')
            if href and '/broken-in-oxford/' in href and '/p/' in href:
                # Extract product code from URL (last part before query params)
                parts = href.split('/')
                for part in reversed(parts):
                    if part and '?' in part:
                        code = part.split('?')[0]
                    else:
                        code = part
                    # Valid J.Crew codes are 5-6 alphanumeric chars
                    if code and len(code) in [5, 6] and code[0].isalpha():
                        product_codes.add(code)
                        break
        
        driver.quit()
        
        if product_codes:
            print(f"\n✅ SUCCESS: Found {len(product_codes)} unique product codes")
            return product_codes
        else:
            print("\n❌ SCRAPING FAILED: No product codes found")
            print("   The page structure may have changed")
            return None
            
    except Exception as e:
        print(f"\n❌ SCRAPING FAILED: Error during extraction")
        print(f"   Error: {e}")
        driver.quit()
        return None

def scrape_with_requests():
    """Try basic requests (will likely fail due to J.Crew blocking)"""
    
    import requests
    
    url = "https://www.jcrew.com/plp/mens/categories/clothing/shirts?sub-categories=men-shirts-brokeninoxford"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }
    
    print("\n🔄 Trying basic HTTP request...")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 403:
            print("❌ SCRAPING FAILED: 403 Forbidden - J.Crew blocks automated requests")
            print("   Need to use Selenium with browser automation instead")
            return None
        elif response.status_code != 200:
            print(f"❌ SCRAPING FAILED: HTTP {response.status_code}")
            return None
        else:
            print("✅ Got response, but likely missing dynamic content")
            return None
            
    except Exception as e:
        print(f"❌ SCRAPING FAILED: {e}")
        return None

def main():
    """Main function with transparent error reporting"""
    
    print("J.CREW OXFORD SCRAPER - TRANSPARENT VERSION")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Try Selenium first (most likely to work)
    codes = scrape_with_selenium()
    
    if codes:
        print("\n📋 Product codes found:")
        for code in sorted(codes):
            print(f"   • {code}")
    else:
        print("\n⚠️  ATTEMPTING FALLBACK: Basic HTTP request...")
        codes = scrape_with_requests()
        
        if not codes:
            print("\n" + "="*80)
            print("SCRAPING FAILED - NO FALLBACK TO HARDCODED DATA")
            print("="*80)
            print("\n❌ Could not scrape J.Crew page due to:")
            print("   1. J.Crew blocks automated requests (403 Forbidden)")
            print("   2. Dynamic content requires browser automation")
            print("\n✅ Solution: Use Selenium with headless Chrome")
            print("   We have working scripts in scripts/crawl_jcrew_*.py")
            print("\n⚠️  NO DATA RETURNED - Not using hardcoded fallback")
            return None
    
    return codes

if __name__ == "__main__":
    main()
