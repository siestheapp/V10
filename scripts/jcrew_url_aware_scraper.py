#!/usr/bin/env python3
"""
J.Crew URL-aware scraper that understands their product hierarchy:
- Base product code (from URL) = product family
- Item code (from page) = specific SKU/variant
"""

import sys
import os
import json
import re
from urllib.parse import urlparse, parse_qs
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_config import DB_CONFIG
from scripts.jcrew_json_scraper import JCrewJSONScraper

def extract_url_info(url):
    """Extract product info from J.Crew URL"""
    
    # Extract base product code from URL path
    # Example: .../BX291?fit=Slim -> base_code = BX291
    path_match = re.search(r'/([A-Z0-9]+)(?:\?|$)', url)
    base_code = path_match.group(1) if path_match else None
    
    # Extract URL parameters
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    
    fit = params.get('fit', [None])[0]
    color_code = params.get('colorProductCode', [None])[0]
    
    return {
        'base_product_code': base_code,
        'url_fit': fit,
        'url_color_code': color_code,
        'full_url': url
    }

def scrape_jcrew_product(url):
    """Scrape J.Crew product with URL awareness"""
    
    print(f"🕷️ Scraping J.Crew Product (URL-Aware)")
    print("=" * 70)
    print(f"URL: {url}")
    
    # Extract URL info
    url_info = extract_url_info(url)
    print(f"\n📊 URL Analysis:")
    print(f"   Base Code: {url_info['base_product_code']}")
    print(f"   Fit: {url_info['url_fit']}")
    print(f"   Color Code: {url_info['url_color_code']}")
    
    # Set up Chrome for scraping
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
    
    driver = None
    try:
        # Download page
        print(f"\n1️⃣ Downloading page...")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        time.sleep(3)
        
        html_content = driver.page_source
        print("   ✓ Page downloaded")
        
        # Extract product data
        print(f"\n2️⃣ Extracting product data...")
        scraper = JCrewJSONScraper()
        product_data = scraper.extract_structured_data(html_content)
        
        if not product_data:
            print("   ❌ Failed to extract product data")
            return None
        
        # Combine URL info with scraped data
        enhanced_data = {
            **product_data,
            'base_product_code': url_info['base_product_code'],
            'url_fit': url_info['url_fit'],
            'url_color_code': url_info['url_color_code'],
            'scraped_item_code': product_data.get('product_code'),  # The item code from page
            'source_url': url
        }
        
        print(f"   ✓ Product: {enhanced_data.get('name', 'Unknown')}")
        print(f"   Base Code: {enhanced_data['base_product_code']} (from URL)")
        print(f"   Item Code: {enhanced_data['scraped_item_code']} (from page)")
        print(f"   Fit: {enhanced_data['url_fit']} (from URL)")
        
        return enhanced_data
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return None
    finally:
        if driver:
            driver.quit()

def store_jcrew_product(product_data):
    """Store J.Crew product with proper hierarchy"""
    
    import psycopg2
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    try:
        base_code = product_data['base_product_code']
        item_code = product_data['scraped_item_code']
        fit = product_data['url_fit']
        
        print(f"\n3️⃣ Storing product in database...")
        
        # Check if base product exists
        cur.execute("""
            SELECT id FROM product_master 
            WHERE brand_id = 4 AND product_code = %s
        """, (base_code,))
        
        master = cur.fetchone()
        
        if master:
            master_id = master[0]
            print(f"   ✓ Found existing master: {base_code} (ID: {master_id})")
        else:
            # Create master product with base code
            cur.execute("""
                INSERT INTO product_master (
                    brand_id, product_code, base_name, materials, pricing_data,
                    created_at, updated_at, last_scraped
                ) VALUES (
                    %s, %s, %s, %s::jsonb, %s::jsonb, %s, %s, %s
                ) RETURNING id
            """, (
                4,  # J.Crew
                base_code,  # Use base code as master
                product_data.get('name'),
                json.dumps(product_data.get('materials', {})),
                json.dumps({'price': product_data.get('price')}),
                datetime.now(), datetime.now(), datetime.now()
            ))
            
            master_id = cur.fetchone()[0]
            print(f"   ✨ Created master: {base_code} (ID: {master_id})")
        
        # Check if this specific variant exists
        cur.execute("""
            SELECT id FROM product_variants
            WHERE product_master_id = %s 
            AND color_name = %s 
            AND fit_option = %s
        """, (master_id, item_code, fit))
        
        if cur.fetchone():
            print(f"   ⚠️ Variant already exists: {item_code}/{fit}")
        else:
            # Add the specific variant
            cur.execute("""
                INSERT INTO product_variants (
                    product_master_id, color_name, fit_option, variant_code,
                    current_price, variant_url, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                master_id,
                item_code,  # J.Crew item code as color_name
                fit,        # Fit from URL
                item_code,  # Also store as variant_code
                product_data.get('price'),
                product_data.get('source_url'),
                datetime.now(), datetime.now()
            ))
            
            variant_id = cur.fetchone()[0]
            print(f"   ✨ Added variant: {item_code} ({fit}) - ID: {variant_id}")
        
        conn.commit()
        return {'master_id': master_id, 'success': True}
        
    except Exception as e:
        conn.rollback()
        print(f"   ❌ Database error: {str(e)}")
        return {'success': False, 'error': str(e)}
    finally:
        conn.close()

def main():
    """Test with the BX291 URLs"""
    
    test_urls = [
        "https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/business-casual-shirts/slim-bowery-performance-stretch-dress-shirt-with-spread-collar/BX291?display=standard&fit=Slim&colorProductCode=BX291",
        "https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/business-casual-shirts/slim-bowery-performance-stretch-dress-shirt-with-spread-collar/BX291?display=standard&fit=Classic&colorProductCode=BX291",
        "https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/business-casual-shirts/slim-bowery-performance-stretch-dress-shirt-with-spread-collar/BX291?display=standard&fit=Tall&colorProductCode=BX291"
    ]
    
    print("🧪 Testing URL-Aware J.Crew Scraper")
    print("=" * 70)
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n{'='*20} TEST {i} {'='*20}")
        
        product_data = scrape_jcrew_product(url)
        if product_data:
            result = store_jcrew_product(product_data)
            print(f"Result: {result}")
        
        print(f"{'='*50}")

if __name__ == "__main__":
    # For now, just test the URL parsing
    test_url = "https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/business-casual-shirts/slim-bowery-performance-stretch-dress-shirt-with-spread-collar/BX291?display=standard&fit=Slim&colorProductCode=BX291"
    
    url_info = extract_url_info(test_url)
    print("🧪 URL Parsing Test")
    print("=" * 50)
    print(f"URL: {test_url}")
    print(f"Parsed: {json.dumps(url_info, indent=2)}")

