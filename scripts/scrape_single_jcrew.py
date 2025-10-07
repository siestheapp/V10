#!/usr/bin/env python3
"""
Scrape a single J.Crew product and add it using the smart deduplicator
"""

import sys
import os
import json
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
from scripts.smart_product_deduplicator import SmartProductDeduplicator

def scrape_and_add_product(url):
    """Scrape a single J.Crew product and add it using the deduplicator"""
    
    print("🕷️ Scraping Single J.Crew Product")
    print("=" * 70)
    print(f"URL: {url}")
    
    # Set up Chrome options for Selenium
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
    
    driver = None
    try:
        # Step 1: Download the page with Selenium
        print("\n1️⃣ Downloading page with Selenium...")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        
        # Wait for content to load
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        time.sleep(3)  # Additional wait for dynamic content
        
        html_content = driver.page_source
        print("   ✓ Page downloaded successfully")
        
        # Step 2: Extract product data
        print("\n2️⃣ Extracting product data...")
        scraper = JCrewJSONScraper()
        product_data = scraper.extract_structured_data(html_content)
        
        if not product_data:
            print("   ❌ Failed to extract product data")
            return None
        
        print(f"   ✓ Extracted: {product_data.get('name', 'Unknown')}")
        print(f"   Code: {product_data.get('product_code', 'Unknown')}")
        print(f"   Price: ${product_data.get('price', 'Unknown')}")
        
        # Step 3: Use smart deduplicator
        print("\n3️⃣ Running through smart deduplicator...")
        deduper = SmartProductDeduplicator(DB_CONFIG)
        
        # Add URL to product data for better analysis
        product_data['url'] = url
        
        decision = deduper.process_product(product_data, brand_id=4)
        
        action_emoji = {
            'skip': '⏭️',
            'add_variant': '🔀',
            'create_master': '✨',
            'update_existing': '🔄'
        }.get(decision['action'], '❓')
        
        print(f"   {action_emoji} Decision: {decision['action'].upper()}")
        print(f"   📊 Confidence: {decision['confidence']:.2%}")
        print(f"   💡 Reason: {decision['reason']}")
        
        # Step 4: Execute the decision
        print("\n4️⃣ Executing decision...")
        
        if decision['action'] == 'skip':
            print("   ⏭️ Product already exists, skipping")
            return {'action': 'skipped', 'reason': decision['reason']}
        
        elif decision['action'] == 'create_master':
            result = create_new_product(product_data)
            print(f"   ✨ Created new product: {result}")
            return {'action': 'created', 'product_id': result}
        
        elif decision['action'] == 'add_variant':
            result = add_as_variant(product_data, decision.get('master_id'))
            print(f"   🔀 Added as variant: {result}")
            return {'action': 'variant_added', 'variant_id': result}
        
        else:
            print(f"   ❓ Unknown action: {decision['action']}")
            return {'action': 'unknown', 'decision': decision}
    
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return None
    
    finally:
        if driver:
            driver.quit()


def create_new_product(product_data):
    """Create a new product in the database"""
    import psycopg2
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    try:
        # Insert into product_master
        cur.execute("""
            INSERT INTO product_master (
                brand_id,
                product_code,
                base_name,
                materials,
                pricing_data,
                created_at,
                updated_at,
                last_scraped
            ) VALUES (
                %s, %s, %s, %s::jsonb, %s::jsonb, %s, %s, %s
            ) RETURNING id
        """, (
            4,  # J.Crew brand_id
            product_data.get('product_code'),
            product_data.get('name'),
            json.dumps(product_data.get('materials', {})),
            json.dumps({'price': product_data.get('price')}),
            datetime.now(),
            datetime.now(),
            datetime.now()
        ))
        
        product_id = cur.fetchone()[0]
        
        # Add variants if available
        colors = product_data.get('colors', [])
        fits = product_data.get('fits', ['Classic'])  # Default fit
        
        for color in colors or [product_data.get('product_code')]:  # Use product code if no colors
            for fit in fits:
                cur.execute("""
                    INSERT INTO product_variants (
                        product_master_id,
                        color_name,
                        fit_option,
                        created_at,
                        updated_at
                    ) VALUES (%s, %s, %s, %s, %s)
                """, (
                    product_id,
                    color,
                    fit,
                    datetime.now(),
                    datetime.now()
                ))
        
        conn.commit()
        return product_id
    
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def add_as_variant(product_data, master_id):
    """Add product as a variant of existing master"""
    import psycopg2
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    try:
        # Add as variant
        cur.execute("""
            INSERT INTO product_variants (
                product_master_id,
                color_name,
                fit_option,
                created_at,
                updated_at
            ) VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (
            master_id,
            product_data.get('product_code'),  # Use product code as color variant
            'Slim',  # From URL analysis
            datetime.now(),
            datetime.now()
        ))
        
        variant_id = cur.fetchone()[0]
        conn.commit()
        return variant_id
    
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


if __name__ == "__main__":
    url = "https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/business-casual-shirts/slim-bowery-performance-stretch-dress-shirt-with-spread-collar/BX291?display=standard&fit=Slim&colorProductCode=BX291"
    
    result = scrape_and_add_product(url)
    
    print("\n" + "=" * 70)
    if result:
        print("✅ Operation completed successfully!")
        print(f"Result: {result}")
    else:
        print("❌ Operation failed")
    
    # Verify the result
    print("\n🔍 Verifying result...")
    import psycopg2
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT pm.id, pm.product_code, pm.base_name,
               COUNT(pv.id) as variant_count
        FROM product_master pm
        LEFT JOIN product_variants pv ON pm.id = pv.product_master_id
        WHERE pm.brand_id = 4 
        AND pm.product_code = 'BX291'
        GROUP BY pm.id, pm.product_code, pm.base_name
    """)
    
    verification = cur.fetchone()
    if verification:
        id, code, name, variants = verification
        print(f"   ✓ Found: {code} - {name[:50]}")
        print(f"   Variants: {variants}")
    else:
        print("   ⚠️ Product not found in database")
    
    conn.close()

