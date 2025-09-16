#!/usr/bin/env python3
"""
Check J.Crew Broken-in Oxford products in database vs website
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

def check_database_oxford():
    """Check what Broken-in Oxford products we have in database"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    print("=" * 80)
    print("J.CREW BROKEN-IN OXFORD PRODUCTS - DATABASE CHECK")
    print("=" * 80)
    
    # Check for products with "Oxford" in name or subcategory
    cur.execute("""
        SELECT product_code, product_name, fit_options, colors_available, subcategory
        FROM jcrew_product_cache
        WHERE LOWER(product_name) LIKE '%oxford%'
           OR LOWER(subcategory) LIKE '%oxford%'
           OR LOWER(product_name) LIKE '%broken-in%'
           OR LOWER(product_name) LIKE '%broken in%'
        ORDER BY product_code
    """)
    
    db_products = cur.fetchall()
    
    print(f"\n📊 Found {len(db_products)} Oxford/Broken-in products in database:\n")
    
    product_codes = []
    for code, name, fits, colors, subcat in db_products[:10]:  # Show first 10
        product_codes.append(code)
        print(f"{code}: {name[:50] if name else 'No name'}...")
        if fits:
            print(f"   Fits: {len(fits)} options")
        if colors:
            print(f"   Colors: {len(colors)} available")
        print()
    
    if len(db_products) > 10:
        print(f"... and {len(db_products) - 10} more products")
    
    cur.close()
    conn.close()
    
    return product_codes

def scrape_oxford_listing(headless=True):
    """Scrape the Broken-in Oxford listing page"""
    
    # Setup driver
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument('--headless')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)')
    
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    print("\n" + "=" * 80)
    print("SCRAPING J.CREW BROKEN-IN OXFORD LISTING")
    print("=" * 80)
    
    url = 'https://www.jcrew.com/plp/mens/categories/clothing/shirts?sub-categories=men-shirts-brokeninoxford'
    print(f"URL: {url}\n")
    
    driver.get(url)
    time.sleep(3)
    
    # Wait for products
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[class*="product"], article'))
        )
    except TimeoutException:
        print("⚠️ Timeout waiting for products")
    
    # Scroll to load all products
    print("📜 Scrolling to load products...")
    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_count = 0
    max_scrolls = 5  # Limit scrolling
    
    while scroll_count < max_scrolls:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        scroll_count += 1
    
    # Extract product codes
    print("\n🔍 Extracting product information...")
    
    products_found = {}
    product_elements = driver.find_elements(By.CSS_SELECTOR, '[class*="product-tile"], [class*="product-card"], article')
    
    for element in product_elements:
        try:
            # Get href
            link = element.find_element(By.TAG_NAME, 'a')
            href = link.get_attribute('href')
            
            if not href:
                continue
            
            # Extract product code
            patterns = [
                r'/([A-Z]{2}\d{3,4})(?:\?|$)',
                r'/p/.*/([A-Z]{2}\d{3,4})(?:\?|$)',
            ]
            
            code = None
            for pattern in patterns:
                match = re.search(pattern, href)
                if match:
                    code = match.group(1)
                    break
            
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
            
            # Check if it's actually an Oxford product
            if name and ('oxford' in name.lower() or 'broken-in' in name.lower() or 'broken in' in name.lower()):
                products_found[code] = {
                    'product_code': code,
                    'product_name': name,
                    'product_url': href
                }
                print(f"   Found: {code} - {name[:40]}...")
            
        except Exception as e:
            continue
    
    driver.quit()
    
    print(f"\n✅ Found {len(products_found)} Oxford products on page")
    return list(products_found.values())

def compare_data(db_codes, scraped_products):
    """Compare database with scraped data"""
    print("\n" + "=" * 80)
    print("COMPARISON ANALYSIS")
    print("=" * 80)
    
    scraped_codes = {p['product_code'] for p in scraped_products}
    db_codes_set = set(db_codes)
    
    # Find differences
    in_db_not_scraped = db_codes_set - scraped_codes
    in_scraped_not_db = scraped_codes - db_codes_set
    in_both = db_codes_set & scraped_codes
    
    print(f"\n📊 Summary:")
    print(f"   Products in database: {len(db_codes_set)}")
    print(f"   Products on website: {len(scraped_codes)}")
    print(f"   In both: {len(in_both)}")
    print(f"   Only in DB: {len(in_db_not_scraped)}")
    print(f"   Only on website: {len(in_scraped_not_db)}")
    
    if in_scraped_not_db:
        print(f"\n🆕 New products to add ({len(in_scraped_not_db)}):")
        for code in list(in_scraped_not_db)[:10]:
            product = next(p for p in scraped_products if p['product_code'] == code)
            print(f"   {code}: {product['product_name'][:50]}...")
        if len(in_scraped_not_db) > 10:
            print(f"   ... and {len(in_scraped_not_db) - 10} more")
    
    if in_db_not_scraped:
        print(f"\n⚠️ In DB but not on current page ({len(in_db_not_scraped)}):")
        for code in list(in_db_not_scraped)[:5]:
            print(f"   {code}")
        if len(in_db_not_scraped) > 5:
            print(f"   ... and {len(in_db_not_scraped) - 5} more")
        print("   (May be out of stock or discontinued)")
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'oxford_check_{timestamp}.json'
    
    with open(filename, 'w') as f:
        json.dump({
            'timestamp': timestamp,
            'summary': {
                'db_count': len(db_codes_set),
                'scraped_count': len(scraped_codes),
                'in_both': len(in_both),
                'only_db': len(in_db_not_scraped),
                'only_scraped': len(in_scraped_not_db)
            },
            'new_products': [p for p in scraped_products if p['product_code'] in in_scraped_not_db],
            'all_scraped': scraped_products
        }, f, indent=2)
    
    print(f"\n📁 Results saved to: {filename}")
    
    return {
        'new': len(in_scraped_not_db),
        'missing': len(in_db_not_scraped),
        'matched': len(in_both)
    }

def main():
    """Main execution"""
    
    # Check database
    db_codes = check_database_oxford()
    
    # Scrape website
    scraped_products = scrape_oxford_listing(headless=True)
    
    # Compare
    results = compare_data(db_codes, scraped_products)
    
    print("\n" + "=" * 80)
    print("BROKEN-IN OXFORD CHECK COMPLETE")
    print("=" * 80)
    
    if results['new'] > 0:
        print(f"\n⚠️ Found {results['new']} new Oxford products not in database")
        print("   Consider running full scraper to add these products")
    else:
        print("\n✅ All Oxford products on page are in database")
    
    if results['missing'] > 0:
        print(f"\n📝 Note: {results['missing']} products in DB not on current page")
        print("   These may be seasonal or discontinued items")

if __name__ == "__main__":
    main()
