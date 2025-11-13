#!/usr/bin/env python3
"""
Reiss Fast JSON Scraper - Extracts product data from structured JSON instead of Selenium
Much faster than browser automation
"""

import requests
import json
import re
from typing import Dict, Optional, List
from bs4 import BeautifulSoup
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_config import DB_CONFIG

class ReissJSONScraper:
    """Fast scraper for Reiss using structured data extraction"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def extract_structured_data(self, html: str) -> Optional[Dict]:
        """
        Extract structured data from Reiss HTML
        Look for:
        1. JSON-LD structured data
        2. Next.js __NEXT_DATA__ 
        3. Window state objects
        4. Meta tags as fallback
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Method 1: Look for JSON-LD structured data
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                if '@type' in data and 'Product' in data.get('@type', ''):
                    print("✅ Found JSON-LD product data")
                    return self.parse_json_ld(data)
            except json.JSONDecodeError:
                continue
        
        # Method 2: Look for Next.js __NEXT_DATA__
        next_data_script = soup.find('script', id='__NEXT_DATA__')
        if next_data_script:
            try:
                data = json.loads(next_data_script.string)
                print("✅ Found __NEXT_DATA__")
                return self.parse_next_data(data)
            except json.JSONDecodeError:
                pass
        
        # Method 3: Look for window state objects (common patterns)
        patterns = [
            r'window\.__INITIAL_STATE__\s*=\s*({.*?});',
            r'window\.productData\s*=\s*({.*?});',
            r'window\.PRODUCT\s*=\s*({.*?});',
            r'var\s+productJson\s*=\s*({.*?});',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(1))
                    print(f"✅ Found window state object with pattern: {pattern[:30]}...")
                    return self.parse_window_state(data)
                except json.JSONDecodeError:
                    continue
        
        # Method 4: Parse from meta tags and HTML as fallback
        print("⚠️ No structured JSON found, falling back to HTML parsing")
        return self.parse_html_fallback(soup)
    
    def parse_json_ld(self, data: Dict) -> Dict:
        """Parse JSON-LD structured data"""
        result = {
            'name': data.get('name', ''),
            'description': data.get('description', ''),
            'sku': data.get('sku', ''),
            'brand': data.get('brand', {}).get('name', 'Reiss'),
            'price': None,
            'currency': 'USD',
            'sizes': [],
            'color': '',
            'images': [],
            'material': '',
            'care': ''
        }
        
        # Parse offers (price/availability)
        offers = data.get('offers', {})
        if isinstance(offers, dict):
            result['price'] = offers.get('price')
            result['currency'] = offers.get('priceCurrency', 'USD')
            result['in_stock'] = offers.get('availability') == 'https://schema.org/InStock'
        elif isinstance(offers, list) and offers:
            # AggregateOffer with multiple sizes
            result['price'] = offers[0].get('price')
            result['sizes'] = [o.get('name') for o in offers if o.get('name')]
        
        # Parse images
        images = data.get('image', [])
        if isinstance(images, str):
            result['images'] = [images]
        elif isinstance(images, list):
            result['images'] = images
        
        return result
    
    def parse_next_data(self, data: Dict) -> Dict:
        """Parse Next.js __NEXT_DATA__"""
        # Navigate through Next.js structure
        props = data.get('props', {}).get('pageProps', {})
        product = props.get('product', {}) or props.get('data', {}).get('product', {})
        
        if not product:
            # Try different paths
            product = props.get('initialData', {}).get('product', {})
        
        result = {
            'name': product.get('name', '') or product.get('title', ''),
            'description': product.get('description', ''),
            'sku': product.get('sku', '') or product.get('code', ''),
            'brand': 'Reiss',
            'price': None,
            'currency': product.get('currency', 'USD'),
            'sizes': [],
            'color': product.get('color', '') or product.get('colour', ''),
            'images': [],
            'material': product.get('composition', ''),
            'care': product.get('care', ''),
            'style_code': '',
            'product_code': ''
        }
        
        # Extract price
        price_data = product.get('price', {})
        if isinstance(price_data, dict):
            result['price'] = price_data.get('current') or price_data.get('value')
        elif isinstance(price_data, (int, float)):
            result['price'] = price_data
        
        # Extract sizes
        sizes = product.get('sizes', []) or product.get('variants', [])
        if sizes:
            result['sizes'] = []
            for size in sizes:
                if isinstance(size, dict):
                    size_label = size.get('size') or size.get('name') or size.get('label')
                    if size_label:
                        result['sizes'].append({
                            'label': size_label,
                            'in_stock': size.get('available', True) or size.get('inStock', True),
                            'sku': size.get('sku', '')
                        })
                elif isinstance(size, str):
                    result['sizes'].append({'label': size, 'in_stock': True})
        
        # Extract images
        images = product.get('images', []) or product.get('media', [])
        if images:
            result['images'] = []
            for img in images:
                if isinstance(img, dict):
                    url = img.get('url') or img.get('src') or img.get('large')
                    if url:
                        result['images'].append(url)
                elif isinstance(img, str):
                    result['images'].append(img)
        
        return result
    
    def parse_window_state(self, data: Dict) -> Dict:
        """Parse window state objects"""
        # Similar to parse_next_data but with different paths
        product = data.get('product', {})
        
        # Sometimes nested under 'state' or 'data'
        if not product:
            product = data.get('state', {}).get('product', {})
        if not product:
            product = data.get('data', {}).get('product', {})
        
        return self.parse_next_data({'props': {'pageProps': {'product': product}}})
    
    def parse_html_fallback(self, soup: BeautifulSoup) -> Dict:
        """Fallback to parsing HTML directly"""
        result = {
            'name': '',
            'description': '',
            'sku': '',
            'brand': 'Reiss',
            'price': None,
            'currency': 'USD',
            'sizes': [],
            'color': '',
            'images': [],
            'material': '',
            'care': '',
            'style_code': '',
            'product_code': ''
        }
        
        # Get product name from h1 or title
        h1 = soup.find('h1')
        if h1:
            result['name'] = h1.get_text(strip=True)
        else:
            title = soup.find('title')
            if title:
                result['name'] = title.get_text(strip=True).replace(' | REISS', '')
        
        # Get price
        price_elem = soup.find(['span', 'div'], class_=re.compile(r'price', re.I))
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            price_match = re.search(r'[\d,]+\.?\d*', price_text)
            if price_match:
                result['price'] = float(price_match.group().replace(',', ''))
        
        # Get product code from URL or page
        code_elem = soup.find(text=re.compile(r'Product Code:', re.I))
        if code_elem:
            code_text = code_elem.parent.get_text()
            code_match = re.search(r'[A-Z]\d{2}-?\d{3,4}', code_text)
            if code_match:
                result['sku'] = code_match.group()
        
        # Get sizes from buttons or selects
        size_buttons = soup.find_all('button', {'data-testid': re.compile(r'size', re.I)})
        if not size_buttons:
            size_buttons = soup.find_all('button', text=re.compile(r'^(XS|S|M|L|XL|XXL|\d+)$'))
        
        for btn in size_buttons:
            size_text = btn.get_text(strip=True)
            if size_text:
                result['sizes'].append({
                    'label': size_text,
                    'in_stock': 'disabled' not in btn.get('class', []) and not btn.get('disabled')
                })
        
        # Get images
        img_tags = soup.find_all('img', src=re.compile(r'reiss.*product', re.I))
        for img in img_tags[:5]:  # Limit to first 5
            src = img.get('src', '')
            if src and not 'icon' in src.lower():
                result['images'].append(src)
        
        return result
    
    def scrape_product(self, url: str) -> Optional[Dict]:
        """
        Main entry point - scrape a Reiss product URL
        Returns structured product data
        """
        print(f"\n🔍 Scraping Reiss product: {url}")
        
        # Extract product codes from URL
        url_parts = self.parse_url(url)
        print(f"   Style code: {url_parts['style_code']}")
        print(f"   Product code: {url_parts['product_code']}")
        
        try:
            # Fetch HTML
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            html = response.text
            print(f"   ✅ Fetched HTML ({len(html)} bytes)")
            
            # Extract structured data
            product_data = self.extract_structured_data(html)
            
            if product_data:
                # Enhance with URL data
                product_data['url'] = url
                product_data['style_code'] = url_parts['style_code']
                product_data['product_code'] = url_parts['product_code']
                
                # Clean up data
                if not product_data.get('sku'):
                    product_data['sku'] = url_parts['product_code']
                
                # Extract color from name if not found
                if not product_data.get('color') and ' in ' in product_data.get('name', ''):
                    parts = product_data['name'].rsplit(' in ', 1)
                    if len(parts) == 2:
                        product_data['color'] = parts[1]
                
                print(f"   ✅ Extracted product: {product_data.get('name', 'Unknown')}")
                print(f"   💰 Price: ${product_data.get('price', 'N/A')}")
                print(f"   📏 Sizes found: {len(product_data.get('sizes', []))}")
                print(f"   🖼️ Images found: {len(product_data.get('images', []))}")
                
                return product_data
            else:
                print("   ❌ Failed to extract product data")
                return None
                
        except requests.RequestException as e:
            print(f"   ❌ Request failed: {e}")
            return None
    
    def parse_url(self, url: str) -> Dict:
        """Extract style and product codes from Reiss URL"""
        # Pattern: /style/{style_code}/{product_code}
        match = re.search(r'/style/([^/]+)/([^/?#]+)', url)
        if match:
            return {
                'style_code': match.group(1),  # e.g., st378878
                'product_code': match.group(2).upper()  # e.g., D43750
            }
        return {'style_code': '', 'product_code': ''}
    
    def scrape_multiple(self, urls: List[str]) -> List[Dict]:
        """Scrape multiple Reiss products"""
        results = []
        for url in urls:
            data = self.scrape_product(url)
            if data:
                results.append(data)
        return results


def main():
    """Test the scraper with Reiss products"""
    scraper = ReissJSONScraper()
    
    # Test URLs - the Greenwich shirts we already have
    test_urls = [
        "https://www.reiss.com/us/en/style/st378878/d43750",  # White
        "https://www.reiss.com/us/en/style/st378878/d40078",  # Soft Blue
        "https://www.reiss.com/us/en/style/st378878/t53709",  # Navy
    ]
    
    print("=" * 80)
    print("REISS FAST JSON SCRAPER TEST")
    print("=" * 80)
    
    all_results = []
    for url in test_urls:
        result = scraper.scrape_product(url)
        if result:
            all_results.append(result)
            
            # Save to JSON file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reiss_products_{timestamp}.json"
            with open(filename, 'w') as f:
                json.dump(all_results, f, indent=2)
            print(f"\n💾 Saved to {filename}")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Successfully scraped: {len(all_results)}/{len(test_urls)} products")
    
    for result in all_results:
        print(f"\n📦 {result.get('name', 'Unknown')}")
        print(f"   SKU: {result.get('sku')}")
        print(f"   Color: {result.get('color')}")
        print(f"   Price: ${result.get('price')}")
        print(f"   Sizes: {', '.join([s['label'] if isinstance(s, dict) else s for s in result.get('sizes', [])])}")


if __name__ == "__main__":
    main()
