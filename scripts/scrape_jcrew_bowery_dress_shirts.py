#!/usr/bin/env python3
"""
Scraper for J.Crew Bowery dress shirts (Business Casual Shirts subcategory)
URL: https://www.jcrew.com/plp/mens/categories/clothing/dress-shirts?sub-categories=men-dress-shirts-businesscasualshirts
"""

import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def scrape_bowery_shirts():
    """Scrape J.Crew Bowery dress shirts"""
    
    url = "https://www.jcrew.com/plp/mens/categories/clothing/dress-shirts?sub-categories=men-dress-shirts-businesscasualshirts"
    
    print(f"🔍 Scraping Bowery dress shirts from J.Crew...")
    print(f"URL: {url}")
    
    # Setup Chrome options
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
    
    driver = webdriver.Chrome(options=options)
    products = []
    
    try:
        driver.get(url)
        time.sleep(3)  # Initial page load
        
        # Scroll to load all products
        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        max_scrolls = 10
        
        while scroll_attempts < max_scrolls:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                # Try one more scroll to be sure
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
            
            last_height = new_height
            scroll_attempts += 1
        
        print(f"✅ Page loaded after {scroll_attempts} scrolls")
        
        # Find all product tiles
        product_elements = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="product-tile"]')
        print(f"📦 Found {len(product_elements)} product tiles")
        
        for element in product_elements:
            try:
                # Get product link
                link_elem = element.find_element(By.CSS_SELECTOR, 'a[data-testid="product-tile-link"]')
                product_url = link_elem.get_attribute('href')
                
                # Extract product code from URL
                if '/p/' in product_url:
                    product_code = product_url.split('/p/')[-1].split('/')[0].upper()
                else:
                    product_code = product_url.split('/')[-1].split('?')[0].upper()
                
                # Get product name
                name_elem = element.find_element(By.CSS_SELECTOR, 'h3[data-testid="product-tile-name"]')
                product_name = name_elem.text.strip()
                
                # Get price
                try:
                    price_elem = element.find_element(By.CSS_SELECTOR, '[data-testid="product-tile-price"]')
                    price_text = price_elem.text.strip()
                    # Extract numeric price
                    import re
                    price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                    price = float(price_match.group()) if price_match else None
                except:
                    price = None
                
                # Get colors (if visible)
                colors = []
                try:
                    color_elements = element.find_elements(By.CSS_SELECTOR, '[data-testid="product-tile-swatch"]')
                    for color_elem in color_elements:
                        color_name = color_elem.get_attribute('aria-label')
                        if color_name:
                            colors.append(color_name.replace('Color: ', '').strip())
                except:
                    pass
                
                product = {
                    'product_code': product_code,
                    'product_name': product_name,
                    'product_url': product_url,
                    'price': price,
                    'colors': colors if colors else ['Multiple colors available'],
                    'category': 'Dress Shirts',
                    'subcategory': 'Bowery',
                    'brand_name': 'J.Crew'
                }
                
                products.append(product)
                print(f"  ✓ {product_code}: {product_name}")
                
            except Exception as e:
                print(f"  ⚠️ Error processing product: {e}")
                continue
        
        print(f"\n✅ Successfully scraped {len(products)} Bowery products")
        
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        
    finally:
        driver.quit()
    
    # Save to JSON
    if products:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'jcrew_bowery_shirts_{timestamp}.json'
        
        with open(filename, 'w') as f:
            json.dump(products, f, indent=2)
        
        print(f"\n💾 Saved to {filename}")
        
        # Print summary
        unique_codes = set(p['product_code'] for p in products)
        print(f"\n📊 Summary:")
        print(f"  - Total products: {len(products)}")
        print(f"  - Unique product codes: {len(unique_codes)}")
        
    return products

if __name__ == "__main__":
    scrape_bowery_shirts()



