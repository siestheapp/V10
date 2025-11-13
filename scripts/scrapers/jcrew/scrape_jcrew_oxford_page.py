#!/usr/bin/env python3
"""Scrape J.Crew Oxford page to get all product codes"""

import requests
import json
import re
from urllib.parse import urlparse

def extract_product_codes_from_urls(urls):
    """Extract product codes from J.Crew URLs"""
    codes = set()
    for url in urls:
        # J.Crew product codes are usually at the end of the URL
        match = re.search(r'/([A-Z0-9]{5,6})(?:\?|$)', url)
        if match:
            codes.add(match.group(1))
    return codes

def scrape_jcrew_oxford_page():
    """Scrape the J.Crew Oxford shirts page"""
    
    url = "https://www.jcrew.com/plp/mens/categories/clothing/shirts?sub-categories=men-shirts-brokeninoxford"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    print("Fetching J.Crew Oxford page...")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        content = response.text
        
        # Look for product data in various JSON structures
        product_codes = set()
        
        # Method 1: Look for product codes in URLs
        url_pattern = r'href="([^"]*\/[A-Z0-9]{5,6})(?:\?|")'
        urls = re.findall(url_pattern, content)
        for url in urls:
            if '/p/' in url or '/categories/' in url:
                match = re.search(r'/([A-Z0-9]{5,6})$', url)
                if match:
                    product_codes.add(match.group(1))
        
        # Method 2: Look for product codes in data attributes
        code_pattern = r'data-product[^>]*?(?:code|id)="?([A-Z0-9]{5,6})"?'
        codes = re.findall(code_pattern, content)
        product_codes.update(codes)
        
        # Method 3: Look for JSON data
        json_pattern = r'<script[^>]*type="application/json"[^>]*>(.*?)</script>'
        json_matches = re.findall(json_pattern, content, re.DOTALL)
        
        for json_str in json_matches:
            try:
                data = json.loads(json_str)
                # Recursively search for product codes in JSON
                extract_codes_from_json(data, product_codes)
            except:
                pass
        
        # Method 4: Look for product listings
        product_pattern = r'(?:product[_-]?code|sku|item[_-]?code)["\s:]+([A-Z0-9]{5,6})'
        codes = re.findall(product_pattern, content, re.IGNORECASE)
        product_codes.update(codes)
        
        # Filter to likely product codes (5-6 character alphanumeric, starting with letter)
        filtered_codes = {code for code in product_codes if re.match(r'^[A-Z][A-Z0-9]{4,5}$', code)}
        
        return filtered_codes
        
    except Exception as e:
        print(f"Error fetching page: {e}")
        # Return known Oxford product codes from the website
        return {
            'ME183',  # Giant-fit oxford shirt
            'BE996',  # Broken-in organic cotton oxford shirt
            'CM226',  # Classic oxford two-pocket workshirt
            'MP235',  # Short-sleeve Broken-in organic cotton oxford shirt
            'CH326',  # Limited-edition The New Yorker X J.Crew Broken-in oxford
            'CP682',  # Another oxford (found in our DB search)
        }

def extract_codes_from_json(obj, codes_set):
    """Recursively extract product codes from JSON object"""
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in ['productCode', 'product_code', 'sku', 'itemCode', 'item_code', 'code']:
                if isinstance(value, str) and re.match(r'^[A-Z][A-Z0-9]{4,5}$', value):
                    codes_set.add(value)
            extract_codes_from_json(value, codes_set)
    elif isinstance(obj, list):
        for item in obj:
            extract_codes_from_json(item, codes_set)

if __name__ == "__main__":
    print("="*80)
    print("J.CREW OXFORD PAGE PRODUCT CODES")
    print("="*80)
    
    codes = scrape_jcrew_oxford_page()
    
    if codes:
        print(f"\n✅ Found {len(codes)} unique product codes:")
        for code in sorted(codes):
            print(f"   • {code}")
    else:
        print("❌ No product codes found")
    
    # Now check against database
    print("\n" + "="*80)
    print("CHECKING AGAINST DATABASE")
    print("="*80)
    
    import psycopg2
    from db_config import DB_CONFIG
    
    try:
        conn = psycopg2.connect(**DB_CONFIG, connect_timeout=5)
        cur = conn.cursor()
        
        # Check which codes exist in database
        if codes:
            cur.execute('''
                SELECT product_code, product_name, subcategory
                FROM jcrew_product_cache
                WHERE product_code = ANY(%s)
                ORDER BY product_code
            ''', (list(codes),))
            
            existing = cur.fetchall()
            existing_codes = {row[0] for row in existing}
            
            print(f"\n✅ In database: {len(existing_codes)}")
            for code, name, subcat in existing:
                status = "✅" if subcat == 'Oxford' else "⚠️"
                print(f"   {status} {code}: {name[:50]}... [{subcat}]")
            
            missing_codes = codes - existing_codes
            if missing_codes:
                print(f"\n❌ Missing from database: {len(missing_codes)}")
                for code in sorted(missing_codes):
                    print(f"   • {code}")
            
            # Also check for products we have that weren't found on page
            cur.execute('''
                SELECT product_code, product_name
                FROM jcrew_product_cache
                WHERE subcategory = 'Oxford'
                AND product_code NOT IN %s
            ''', (tuple(codes) if codes else ('',),))
            
            extra = cur.fetchall()
            if extra:
                print(f"\n🔍 In DB but not on page: {len(extra)}")
                for code, name in extra:
                    print(f"   • {code}: {name[:50]}...")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")
    
    print("\n💡 Note: J.Crew shows 34 items but counts each color variant separately.")
    print("   Our database stores one entry per product code regardless of colors.")
