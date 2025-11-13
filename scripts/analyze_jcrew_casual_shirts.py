#!/usr/bin/env python3
"""
J.Crew Casual Shirts Analysis Script

Analyzes the J.Crew casual shirts listing page to:
1. Extract all 154 products from https://www.jcrew.com/plp/mens/categories/clothing/shirts
2. Identify unique products vs color variants
3. Check which products are missing from our database
4. Provide a summary of what we need to add

Based on existing J.Crew scraping infrastructure in the V10 project.
"""

import re
import json
import sys
import time
import socket
import urllib.parse
import urllib.request
from typing import Dict, List, Set, Optional, Tuple
import psycopg2
from collections import defaultdict

# Import database config
sys.path.append('/Users/seandavey/projects/V10')
from db_config import DB_CONFIG

# --- Settings (based on your jcrew_categories_from_sitemap.py) --------------
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0.0.0 Safari/537.36")

socket.setdefaulttimeout(20)
MAX_RETRIES = 3
BASE_BACKOFF = 0.5
REQUEST_TIMEOUT = 10

# --- Proxy helper (from your existing code) ---------------------------------
def via_proxy(url: str) -> str:
    """Use Jina.ai proxy to avoid Akamai blocking"""
    u = urllib.parse.urlparse(url)
    inner = f"http://{u.netloc}{u.path}"
    if u.query:
        inner += f"?{u.query}"
    return f"https://r.jina.ai/{inner}"

def fetch_text(url: str, retry=MAX_RETRIES, backoff=BASE_BACKOFF) -> str:
    """Fetch text content from URL with retries, trying multiple methods"""
    last_error = None
    
    # Method 1: Try direct request first
    print(f"   Trying direct request to {url}...")
    for i in range(retry):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as r:
                content = r.read().decode("utf-8", errors="replace")
                print(f"   ✅ Direct request successful")
                return content
        except Exception as e:
            last_error = e
            print(f"   ⚠️  Direct request attempt {i+1} failed: {e}")
            if i < retry - 1:
                time.sleep(backoff * (1.6 ** i))
    
    # Method 2: Try with Jina proxy if direct fails
    print(f"   Trying Jina.ai proxy...")
    proxied = via_proxy(url)
    for i in range(retry):
        try:
            req = urllib.request.Request(proxied, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as r:
                content = r.read().decode("utf-8", errors="replace")
                print(f"   ✅ Proxy request successful")
                return content
        except Exception as e:
            last_error = e
            print(f"   ⚠️  Proxy request attempt {i+1} failed: {e}")
            if i < retry - 1:
                time.sleep(backoff * (1.6 ** i))
    
    raise RuntimeError(f"Failed to fetch {url} with both direct and proxy methods. Last error: {last_error}")

# --- Product extraction (inspired by your crawl_jcrew_inspect_elements.py) ---
def extract_product_codes_from_html(html: str) -> List[Dict]:
    """Extract product information from J.Crew listing page HTML"""
    
    # Method 1: Extract from product links (J.Crew pattern: /p/mens/.../PRODUCTCODE)
    product_link_pattern = r'href="([^"]*\/p\/mens\/[^"]*\/([A-Z0-9]{4,6})(?:\?[^"]*)?)"'
    product_links = re.findall(product_link_pattern, html, re.IGNORECASE)
    print(f"Found {len(product_links)} product links")
    
    # Method 2: Extract from JSON data embedded in page
    json_pattern = r'"productCode"\s*:\s*"([A-Z0-9]{4,6})"[^}]*"name"\s*:\s*"([^"]*)"'
    json_products = re.findall(json_pattern, html, re.IGNORECASE)
    print(f"Found {len(json_products)} products in JSON data")
    
    # Method 3: Look for product data in script tags
    script_pattern = r'window\.__INITIAL_STATE__\s*=\s*({.*?});'
    script_matches = re.findall(script_pattern, html, re.DOTALL)
    
    script_products = []
    for script_content in script_matches:
        try:
            data = json.loads(script_content)
            # Navigate through J.Crew's data structure
            if 'products' in data:
                products_data = data['products']
                if isinstance(products_data, dict):
                    for product_id, product_info in products_data.items():
                        if isinstance(product_info, dict) and 'productCode' in product_info:
                            script_products.append({
                                'code': product_info['productCode'],
                                'name': product_info.get('name', ''),
                                'url': f"https://www.jcrew.com/p/mens/categories/clothing/shirts/{product_info['productCode']}",
                                'price': product_info.get('price', ''),
                                'colors': product_info.get('colors', [])
                            })
        except (json.JSONDecodeError, KeyError):
            continue
    
    print(f"Found {len(script_products)} products in script data")
    
    # Method 4: Structured data (LD+JSON)
    structured_data_pattern = r'<script[^>]*type="application/ld\+json"[^>]*>([^<]*)</script>'
    structured_scripts = re.findall(structured_data_pattern, html, re.IGNORECASE)
    
    structured_products = []
    for script_content in structured_scripts:
        try:
            data = json.loads(script_content)
            if isinstance(data, dict) and '@graph' in data:
                for item in data['@graph']:
                    if item.get('@type') == 'Product':
                        url = item.get('url', '')
                        code_match = re.search(r'/([A-Z0-9]{4,6})(?:\?|$)', url)
                        if code_match:
                            structured_products.append({
                                'code': code_match.group(1),
                                'name': item.get('name', ''),
                                'url': url,
                                'price': item.get('offers', {}).get('price', '') if isinstance(item.get('offers'), dict) else '',
                                'image': item.get('image', ''),
                                'colors': []
                            })
        except json.JSONDecodeError:
            continue
    
    print(f"Found {len(structured_products)} products in structured data")
    
    # Combine all methods and deduplicate by product code
    all_products = {}
    
    # Add from product links
    for url, code in product_links:
        if not url.startswith('http'):
            url = f"https://www.jcrew.com{url}"
        all_products[code] = {
            'code': code,
            'url': url.split('?')[0],  # Remove query parameters
            'name': '',
            'price': '',
            'image': '',
            'colors': []
        }
    
    # Add from JSON data
    for code, name in json_products:
        if code in all_products:
            all_products[code]['name'] = name
        else:
            all_products[code] = {
                'code': code,
                'url': f"https://www.jcrew.com/p/mens/categories/clothing/shirts/{code}",
                'name': name,
                'price': '',
                'image': '',
                'colors': []
            }
    
    # Add from script data
    for product in script_products:
        code = product['code']
        if code in all_products:
            all_products[code].update(product)
        else:
            all_products[code] = product
    
    # Add from structured data
    for product in structured_products:
        code = product['code']
        if code in all_products:
            all_products[code].update(product)
        else:
            all_products[code] = product
            all_products[code]['colors'] = []
    
    return list(all_products.values())

def extract_color_variants(html: str, products: List[Dict]) -> List[Dict]:
    """Try to identify color variants for each product"""
    # Look for color data in the HTML
    color_pattern = r'"colorName"\s*:\s*"([^"]*)"[^}]*"productCode"\s*:\s*"([A-Z0-9]{4,6})"'
    color_matches = re.findall(color_pattern, html, re.IGNORECASE)
    
    # Also look for color swatches
    swatch_pattern = r'"colors"\s*:\s*\[([^\]]*)\]'
    swatch_matches = re.findall(swatch_pattern, html, re.IGNORECASE)
    
    # Group colors by product code
    product_colors = defaultdict(list)
    for color_name, product_code in color_matches:
        product_colors[product_code].append(color_name)
    
    # Update products with color information
    for product in products:
        code = product['code']
        if code in product_colors:
            product['colors'] = list(set(product_colors[code]))  # Remove duplicates
    
    return products

def get_database_products() -> Set[str]:
    """Get all J.Crew product codes currently in our database"""
    print("💾 Checking database for existing J.Crew products...")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        product_codes = set()
        
        # Check jcrew_product_cache table
        print("  📋 Checking jcrew_product_cache table...")
        try:
            cur.execute("SELECT DISTINCT product_code FROM jcrew_product_cache WHERE product_code IS NOT NULL")
            cache_codes = cur.fetchall()
            for (code,) in cache_codes:
                if code:
                    product_codes.add(code.upper())
            print(f"     ✅ Found {len(cache_codes)} products in jcrew_product_cache")
        except psycopg2.Error as e:
            print(f"     ⚠️  jcrew_product_cache table not accessible: {e}")
        
        # Check product_master table for J.Crew products
        print("  📋 Checking product_master table...")
        try:
            cur.execute("""
                SELECT DISTINCT pm.product_code 
                FROM product_master pm 
                JOIN brands b ON pm.brand_id = b.id 
                WHERE LOWER(b.name) LIKE '%j.crew%' OR LOWER(b.name) LIKE '%jcrew%'
            """)
            master_codes = cur.fetchall()
            for (code,) in master_codes:
                if code:
                    product_codes.add(code.upper())
            print(f"     ✅ Found {len(master_codes)} J.Crew products in product_master")
        except psycopg2.Error as e:
            print(f"     ⚠️  product_master table not accessible: {e}")
        
        # Check garments table for J.Crew products
        print("  📋 Checking garments table...")
        try:
            cur.execute("""
                SELECT DISTINCT g.product_code 
                FROM garments g 
                JOIN brands b ON g.brand_id = b.id 
                WHERE (LOWER(b.name) LIKE '%j.crew%' OR LOWER(b.name) LIKE '%jcrew%')
                AND g.product_code IS NOT NULL
            """)
            garment_codes = cur.fetchall()
            for (code,) in garment_codes:
                if code:
                    product_codes.add(code.upper())
            print(f"     ✅ Found {len(garment_codes)} J.Crew products in garments")
        except psycopg2.Error as e:
            print(f"     ⚠️  garments table not accessible: {e}")
        
        cur.close()
        conn.close()
        
        total_unique = len(product_codes)
        print(f"  🎯 Total unique J.Crew product codes in database: {total_unique}")
        
        return product_codes
        
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return set()

def analyze_products(scraped_products: List[Dict], db_products: Set[str]) -> Dict:
    """Analyze scraped products vs database products"""
    scraped_codes = {p['code'].upper() for p in scraped_products}
    
    # Find missing products
    missing_codes = scraped_codes - db_products
    existing_codes = scraped_codes & db_products
    
    # Categorize products by type (based on name patterns)
    categories = {
        'Oxford Shirts': [],
        'Secret Wash': [],
        'Corduroy Shirts': [],
        'Linen Shirts': [],
        'Flannel Shirts': [],
        'Performance Shirts': [],
        'Casual Shirts': [],
        'Other': []
    }
    
    for product in scraped_products:
        name = product['name'].lower()
        code = product['code'].upper()
        is_missing = code in missing_codes
        
        product_info = {
            'code': code,
            'name': product['name'],
            'url': product['url'],
            'colors': len(product['colors']),
            'missing': is_missing
        }
        
        if 'oxford' in name:
            categories['Oxford Shirts'].append(product_info)
        elif 'secret wash' in name:
            categories['Secret Wash'].append(product_info)
        elif 'corduroy' in name:
            categories['Corduroy Shirts'].append(product_info)
        elif 'linen' in name:
            categories['Linen Shirts'].append(product_info)
        elif 'flannel' in name:
            categories['Flannel Shirts'].append(product_info)
        elif 'performance' in name or 'bowery' in name:
            categories['Performance Shirts'].append(product_info)
        elif any(word in name for word in ['shirt', 'button', 'collar']):
            categories['Casual Shirts'].append(product_info)
        else:
            categories['Other'].append(product_info)
    
    return {
        'total_scraped': len(scraped_products),
        'total_in_db': len(existing_codes),
        'total_missing': len(missing_codes),
        'missing_codes': sorted(missing_codes),
        'existing_codes': sorted(existing_codes),
        'categories': categories
    }

def print_analysis_report(analysis: Dict):
    """Print a comprehensive analysis report"""
    print("\n" + "="*80)
    print("J.CREW CASUAL SHIRTS ANALYSIS REPORT")
    print("="*80)
    
    print(f"\n📊 SUMMARY:")
    print(f"   Total products found on website: {analysis['total_scraped']}")
    print(f"   Products already in database:    {analysis['total_in_db']}")
    print(f"   Products missing from database:  {analysis['total_missing']}")
    if analysis['total_scraped'] > 0:
        print(f"   Coverage: {(analysis['total_in_db']/analysis['total_scraped']*100):.1f}%")
    
    print(f"\n🔍 BY CATEGORY:")
    for category, products in analysis['categories'].items():
        if not products:
            continue
        missing_count = sum(1 for p in products if p['missing'])
        total_count = len(products)
        print(f"   {category:15} {total_count:3d} total, {missing_count:3d} missing")
    
    print(f"\n❌ MISSING PRODUCTS ({analysis['total_missing']} total):")
    if analysis['total_missing'] > 0:
        for category, products in analysis['categories'].items():
            missing_products = [p for p in products if p['missing']]
            if missing_products:
                print(f"\n   {category}:")
                for product in missing_products[:5]:  # Show first 5
                    colors_text = f" ({product['colors']} colors)" if product['colors'] > 0 else ""
                    print(f"     {product['code']} - {product['name'][:60]}...{colors_text}")
                if len(missing_products) > 5:
                    print(f"     ... and {len(missing_products) - 5} more")
    
    print(f"\n✅ ALREADY IN DATABASE ({analysis['total_in_db']} total):")
    if analysis['total_in_db'] > 0:
        existing_by_category = {}
        for category, products in analysis['categories'].items():
            existing_products = [p for p in products if not p['missing']]
            if existing_products:
                existing_by_category[category] = len(existing_products)
        
        for category, count in existing_by_category.items():
            print(f"   {category:15} {count:3d} products")
    
    print(f"\n📋 MISSING PRODUCT CODES:")
    if analysis['missing_codes']:
        codes_per_line = 10
        codes = analysis['missing_codes']
        for i in range(0, len(codes), codes_per_line):
            line_codes = codes[i:i+codes_per_line]
            print(f"   {' '.join(line_codes)}")
    
    print(f"\n🔗 SAMPLE URLS TO INVESTIGATE:")
    sample_missing = []
    for category, products in analysis['categories'].items():
        missing_products = [p for p in products if p['missing']]
        if missing_products:
            sample_missing.extend(missing_products[:2])  # 2 per category
    
    for product in sample_missing[:10]:  # Show first 10
        print(f"   {product['url']}")
    
    print("\n" + "="*80)

def main():
    """Main analysis function"""
    print("🔍 Analyzing J.Crew Casual Shirts...")
    print("=" * 60)
    
    # Test database connection first
    print("🔌 Testing database connection...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("Please check your database configuration and try again.")
        sys.exit(1)
    
    # Fetch the casual shirts listing page
    print("\n🌐 Fetching J.Crew casual shirts page...")
    print("URL: https://www.jcrew.com/plp/mens/categories/clothing/shirts")
    print("Using Jina.ai proxy to avoid blocking...")
    
    try:
        html = fetch_text("https://www.jcrew.com/plp/mens/categories/clothing/shirts")
        print(f"✅ Fetched {len(html):,} characters of HTML")
        
        # Quick sanity check
        if len(html) < 10000:
            print("⚠️  Warning: HTML seems unusually short, may be blocked or error page")
        if "j.crew" not in html.lower():
            print("⚠️  Warning: HTML doesn't contain 'j.crew', may be wrong page")
            
    except Exception as e:
        print(f"❌ Failed to fetch page: {e}")
        print("This could be due to:")
        print("  - Network connectivity issues")
        print("  - J.Crew blocking the request")
        print("  - Jina.ai proxy issues")
        sys.exit(1)
    
    # Extract products from HTML
    print("\n🔍 Extracting products from HTML...")
    products = extract_product_codes_from_html(html)
    
    if not products:
        print("❌ No products found. The page structure may have changed.")
        sys.exit(1)
    
    print(f"✅ Found {len(products)} unique products")
    
    # Try to extract color variants
    print("\n🎨 Analyzing color variants...")
    products = extract_color_variants(html, products)
    
    total_colors = sum(len(p['colors']) for p in products)
    print(f"✅ Found {total_colors} color variants across all products")
    
    # Get products from database
    print("\n💾 Checking database for existing products...")
    db_products = get_database_products()
    print(f"✅ Found {len(db_products)} J.Crew products in database")
    
    # Analyze the differences
    print("\n📊 Analyzing differences...")
    analysis = analyze_products(products, db_products)
    
    # Print the report
    print_analysis_report(analysis)
    
    # Save detailed results to JSON
    output_file = f"jcrew_casual_shirts_analysis_{int(time.time())}.json"
    with open(output_file, 'w') as f:
        # Make analysis JSON serializable
        json_analysis = analysis.copy()
        json_analysis['scraped_products'] = products
        json.dump(json_analysis, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {output_file}")

def test_mode():
    """Quick test mode to verify script functionality"""
    print("🧪 Running in TEST MODE")
    print("=" * 40)
    
    # Test database connection
    print("🔌 Testing database connection...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return
    
    # Test network connectivity with a simple request
    print("\n🌐 Testing network connectivity...")
    try:
        test_html = fetch_text("https://httpbin.org/get")
        print("✅ Network request successful")
        print(f"   Response length: {len(test_html)} characters")
    except Exception as e:
        print(f"❌ Network request failed: {e}")
        return
    
    # Test database queries
    print("\n💾 Testing database queries...")
    db_products = get_database_products()
    
    print(f"\n✅ Test completed successfully!")
    print(f"   Found {len(db_products)} J.Crew products in database")
    print("\nTo run full analysis, use: python scripts/analyze_jcrew_casual_shirts.py --full")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_mode()
    elif len(sys.argv) > 1 and sys.argv[1] == "--full":
        main()
    else:
        print("🔍 J.Crew Casual Shirts Analysis Script")
        print("=" * 50)
        print("Usage:")
        print("  --test    Run quick connectivity test")
        print("  --full    Run full analysis (may take 30-60 seconds)")
        print("\nRecommended: Start with --test to verify everything works")
        print("Example: python scripts/analyze_jcrew_casual_shirts.py --test")
