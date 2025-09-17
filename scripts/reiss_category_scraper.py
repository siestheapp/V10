#!/usr/bin/env python3
"""
Reiss Category Scraper - Extracts all products from category/listing pages
Can scrape all 41 formal shirts from a category page
"""

import requests
import json
import re
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
import sys
import os
from datetime import datetime
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_config import DB_CONFIG

class ReissCategoryScraper:
    """Scraper for Reiss category/listing pages"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.base_url = "https://www.reiss.com"
    
    def scrape_category(self, category_url: str, max_pages: int = 10) -> List[Dict]:
        """
        Scrape all products from a Reiss category page
        
        Args:
            category_url: URL of the category page (e.g., formal shirts)
            max_pages: Maximum number of pages to scrape (for pagination)
            
        Returns:
            List of product data dictionaries
        """
        all_products = []
        page = 1
        
        print(f"🔍 Scraping Reiss category: {category_url}")
        
        while page <= max_pages:
            # Add pagination parameter if needed
            if page > 1:
                separator = '&' if '?' in category_url else '?'
                page_url = f"{category_url}{separator}page={page}"
            else:
                page_url = category_url
            
            print(f"\n📄 Page {page}:")
            products = self.scrape_page(page_url)
            
            if not products:
                print(f"   No more products found. Stopping.")
                break
            
            all_products.extend(products)
            print(f"   ✅ Found {len(products)} products (Total: {len(all_products)})")
            
            # Be nice to the server
            if page < max_pages:
                time.sleep(1)
            
            page += 1
        
        return all_products
    
    def scrape_page(self, url: str) -> List[Dict]:
        """Scrape a single page of products"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            html = response.text
            
            # Try to extract structured data first
            products = self.extract_structured_products(html)
            
            if not products:
                # Fallback to HTML parsing
                products = self.parse_html_products(html)
            
            return products
            
        except requests.RequestException as e:
            print(f"   ❌ Request failed: {e}")
            return []
    
    def extract_structured_products(self, html: str) -> List[Dict]:
        """Extract products from structured JSON data in the page"""
        products = []
        
        # Method 1: Look for __NEXT_DATA__
        match = re.search(r'<script id="__NEXT_DATA__"[^>]*>({.*?})</script>', html, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(1))
                # Navigate through Next.js structure
                props = data.get('props', {}).get('pageProps', {})
                
                # Try different paths where products might be
                product_list = (
                    props.get('products', []) or
                    props.get('items', []) or
                    props.get('data', {}).get('products', []) or
                    props.get('initialData', {}).get('products', [])
                )
                
                if product_list:
                    print(f"   ✅ Found {len(product_list)} products in __NEXT_DATA__")
                    for item in product_list:
                        products.append(self.parse_product_json(item))
                    return products
            except json.JSONDecodeError:
                pass
        
        # Method 2: Look for window state objects
        patterns = [
            r'window\.__PRODUCTS__\s*=\s*(\[.*?\]);',
            r'window\.productList\s*=\s*(\[.*?\]);',
            r'window\.categoryProducts\s*=\s*({.*?});',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(1))
                    if isinstance(data, list):
                        print(f"   ✅ Found {len(data)} products in window object")
                        for item in data:
                            products.append(self.parse_product_json(item))
                        return products
                except json.JSONDecodeError:
                    continue
        
        return products
    
    def parse_product_json(self, item: Dict) -> Dict:
        """Parse a product from JSON data"""
        return {
            'product_code': item.get('code') or item.get('sku') or item.get('id', ''),
            'style_code': item.get('styleNumber') or item.get('style', ''),
            'name': item.get('name') or item.get('title', ''),
            'price': item.get('price', {}).get('current') if isinstance(item.get('price'), dict) else item.get('price'),
            'url': item.get('url', ''),
            'image': item.get('image') or item.get('imageUrl', ''),
            'colors': item.get('colors', []),
            'in_stock': item.get('inStock', True)
        }
    
    def parse_html_products(self, html: str) -> List[Dict]:
        """Parse products from HTML when no JSON is available"""
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        
        # Common product card selectors for listing pages
        product_selectors = [
            'article[data-testid*="product"]',
            'div[class*="product-card"]',
            'div[class*="product-item"]',
            'div[class*="ProductCard"]',
            'article[class*="product"]',
            'a[href*="/style/"]',  # Reiss specific
        ]
        
        product_cards = []
        for selector in product_selectors:
            product_cards = soup.select(selector)
            if product_cards:
                print(f"   Found {len(product_cards)} product cards with selector: {selector}")
                break
        
        for card in product_cards:
            product = self.parse_product_card(card)
            if product and product.get('product_code'):
                products.append(product)
        
        return products
    
    def parse_product_card(self, card) -> Dict:
        """Parse a single product card from HTML"""
        product = {}
        
        # Extract link and codes
        link = card.find('a', href=True)
        if link:
            href = link['href']
            if not href.startswith('http'):
                href = self.base_url + href
            product['url'] = href
            
            # Extract product code from URL
            # Pattern: /style/{style_code}/{product_code}
            match = re.search(r'/style/([^/]+)/([^/?#]+)', href)
            if match:
                product['style_code'] = match.group(1)
                product['product_code'] = match.group(2).upper()
        
        # Extract product code from text (e.g., "(D43750)")
        code_match = re.search(r'\(([A-Z]\d{2,3}-?\d{3,4})\)', card.get_text())
        if code_match:
            product['product_code'] = code_match.group(1)
        
        # Extract name
        name_elem = card.find(['h3', 'h4', 'h5', 'span'], class_=re.compile(r'name|title', re.I))
        if not name_elem:
            name_elem = card.find('a', {'aria-label': True})
        if name_elem:
            if name_elem.get('aria-label'):
                product['name'] = name_elem['aria-label']
            else:
                product['name'] = name_elem.get_text(strip=True)
        
        # Extract price
        price_elem = card.find(['span', 'div'], class_=re.compile(r'price', re.I))
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            price_match = re.search(r'\$?([\d,]+\.?\d*)', price_text)
            if price_match:
                product['price'] = float(price_match.group(1).replace(',', ''))
        
        # Extract image
        img = card.find('img')
        if img:
            product['image'] = img.get('src', '') or img.get('data-src', '')
        
        # Extract colors (if shown as swatches)
        color_swatches = card.find_all(['button', 'div'], class_=re.compile(r'swatch|color', re.I))
        if color_swatches:
            colors = []
            for swatch in color_swatches:
                color = swatch.get('aria-label', '') or swatch.get('title', '') or swatch.get_text(strip=True)
                if color and color not in colors:
                    colors.append(color)
            product['colors'] = colors
        
        return product
    
    def save_to_json(self, products: List[Dict], filename: str = None):
        """Save products to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reiss_category_products_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(products, f, indent=2)
        
        print(f"\n💾 Saved {len(products)} products to {filename}")
        return filename


def main():
    """Test the category scraper"""
    scraper = ReissCategoryScraper()
    
    # Test with the formal shirts category
    test_url = "https://www.reiss.com/us/en/shop/gender-men-category-shirts/use-formal"
    
    print("=" * 80)
    print("REISS CATEGORY SCRAPER TEST")
    print("=" * 80)
    print(f"Target: Men's Formal Shirts (expecting ~41 products)")
    print("=" * 80)
    
    # Scrape the category
    products = scraper.scrape_category(test_url, max_pages=3)
    
    # Save results
    if products:
        filename = scraper.save_to_json(products)
        
        # Display summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total products scraped: {len(products)}")
        
        # Show first 5 products
        print("\nFirst 5 products:")
        for i, product in enumerate(products[:5], 1):
            print(f"\n{i}. {product.get('name', 'Unknown')}")
            print(f"   Code: {product.get('product_code', 'N/A')}")
            print(f"   Style: {product.get('style_code', 'N/A')}")
            print(f"   Price: ${product.get('price', 'N/A')}")
            print(f"   URL: {product.get('url', 'N/A')[:60]}...")
            if product.get('colors'):
                print(f"   Colors: {', '.join(product['colors'][:3])}")
        
        # Unique product codes
        unique_codes = set(p['product_code'] for p in products if p.get('product_code'))
        print(f"\n📊 Unique product codes found: {len(unique_codes)}")
        
        # Next steps
        print("\n🎯 Next Steps:")
        print("1. Use reiss_json_scraper.py to get full details for each product")
        print("2. Store in database using the unified structure")
        print("3. Each color variant will be a separate product_master entry")
    else:
        print("\n❌ No products found. The page structure might have changed.")


if __name__ == "__main__":
    main()
