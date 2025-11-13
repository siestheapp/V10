#!/usr/bin/env python3
"""
Reiss Bulk Scraper - Simple approach:
1. Extract all product URLs from category page
2. Use existing JSON scraper for each product
"""

import requests
import re
from typing import List, Set
from bs4 import BeautifulSoup
import time
import json
from datetime import datetime
import sys
import os

# Import our existing JSON scraper
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from reiss_json_scraper import ReissJSONScraper

class ReissBulkScraper:
    """Extract links from category page, then scrape each product"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"macOS"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
        }
        self.base_url = "https://www.reiss.com"
        self.product_scraper = ReissJSONScraper()
        
        # Create a session with better handling
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def extract_product_links(self, category_url: str) -> List[str]:
        """
        Extract all product URLs from a category page
        
        Args:
            category_url: URL of category page (e.g., formal shirts)
            
        Returns:
            List of product URLs
        """
        print(f"🔍 Extracting product links from: {category_url}")
        
        try:
            response = self.session.get(category_url, timeout=10)
            response.raise_for_status()
            html = response.text
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find all links that match Reiss product URL pattern
            # Pattern: /style/{style_code}/{product_code}
            product_links = set()
            
            # Method 1: Find all <a> tags with href matching pattern
            for link in soup.find_all('a', href=True):
                href = link['href']
                if '/style/' in href:
                    # Make absolute URL if relative
                    if not href.startswith('http'):
                        href = self.base_url + href
                    
                    # Clean up URL (remove fragments)
                    href = href.split('#')[0]
                    
                    # Validate it's a product URL
                    if re.search(r'/style/[^/]+/[^/]+$', href):
                        product_links.add(href)
            
            # Method 2: Also check for links in data attributes
            for elem in soup.find_all(attrs={'data-href': True}):
                href = elem['data-href']
                if '/style/' in href:
                    if not href.startswith('http'):
                        href = self.base_url + href
                    href = href.split('#')[0]
                    if re.search(r'/style/[^/]+/[^/]+$', href):
                        product_links.add(href)
            
            print(f"   ✅ Found {len(product_links)} unique product links")
            return sorted(list(product_links))
            
        except requests.RequestException as e:
            print(f"   ❌ Failed to fetch category page: {e}")
            return []
    
    def scrape_all_products(self, category_url: str, delay: float = 1.0) -> List[dict]:
        """
        Scrape all products from a category
        
        Args:
            category_url: URL of category page
            delay: Seconds to wait between product scrapes (be nice to server)
            
        Returns:
            List of product data dictionaries
        """
        # Step 1: Get all product links
        product_urls = self.extract_product_links(category_url)
        
        if not product_urls:
            print("❌ No product links found")
            return []
        
        print(f"\n📦 Scraping {len(product_urls)} products...")
        print("=" * 60)
        
        # Step 2: Scrape each product
        all_products = []
        failed_urls = []
        
        for i, url in enumerate(product_urls, 1):
            print(f"\n[{i}/{len(product_urls)}] Scraping: {url.split('/')[-1]}")
            
            try:
                # Use our existing JSON scraper
                product_data = self.product_scraper.scrape_product(url)
                
                if product_data:
                    all_products.append(product_data)
                    print(f"   ✅ Success: {product_data.get('name', 'Unknown')[:50]}")
                else:
                    failed_urls.append(url)
                    print(f"   ⚠️ Failed to extract data")
                    
            except Exception as e:
                failed_urls.append(url)
                print(f"   ❌ Error: {str(e)[:100]}")
            
            # Be nice to the server
            if i < len(product_urls):
                time.sleep(delay)
        
        # Summary
        print("\n" + "=" * 60)
        print("SCRAPING COMPLETE")
        print("=" * 60)
        print(f"✅ Successfully scraped: {len(all_products)}/{len(product_urls)} products")
        
        if failed_urls:
            print(f"❌ Failed URLs ({len(failed_urls)}):")
            for url in failed_urls[:5]:
                print(f"   - {url}")
            if len(failed_urls) > 5:
                print(f"   ... and {len(failed_urls) - 5} more")
        
        return all_products
    
    def save_results(self, products: List[dict], filename: str = None):
        """Save scraped products to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reiss_bulk_scrape_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(products, f, indent=2)
        
        print(f"\n💾 Saved {len(products)} products to {filename}")
        return filename
    
    def get_summary(self, products: List[dict]) -> dict:
        """Generate summary statistics"""
        if not products:
            return {}
        
        # Unique styles
        styles = set(p.get('style_code', '') for p in products if p.get('style_code'))
        
        # Unique product codes
        codes = set(p.get('product_code', '') for p in products if p.get('product_code'))
        
        # Price range
        prices = [p.get('price') for p in products if p.get('price')]
        min_price = min(prices) if prices else 0
        max_price = max(prices) if prices else 0
        avg_price = sum(prices) / len(prices) if prices else 0
        
        # Colors
        all_colors = set()
        for p in products:
            if p.get('color'):
                all_colors.add(p['color'])
        
        return {
            'total_products': len(products),
            'unique_styles': len(styles),
            'unique_product_codes': len(codes),
            'price_range': f"${min_price:.2f} - ${max_price:.2f}",
            'average_price': f"${avg_price:.2f}",
            'unique_colors': len(all_colors),
            'colors': sorted(list(all_colors))
        }


def main():
    """Test the bulk scraper"""
    scraper = ReissBulkScraper()
    
    # URL for Men's Formal Shirts
    category_url = "https://www.reiss.com/us/en/shop/gender-men-category-shirts/use-formal"
    
    print("=" * 80)
    print("REISS BULK SCRAPER")
    print("=" * 80)
    print(f"Target: {category_url}")
    print("=" * 80)
    
    # Scrape all products
    products = scraper.scrape_all_products(category_url, delay=0.5)  # 0.5 second delay between products
    
    if products:
        # Save results
        filename = scraper.save_results(products)
        
        # Show summary
        summary = scraper.get_summary(products)
        print("\n📊 SUMMARY:")
        print("=" * 60)
        for key, value in summary.items():
            print(f"{key:20}: {value}")
        
        # Show sample products
        print("\n📦 Sample Products:")
        print("=" * 60)
        for i, product in enumerate(products[:3], 1):
            print(f"\n{i}. {product.get('name', 'Unknown')}")
            print(f"   Code: {product.get('product_code')}")
            print(f"   Style: {product.get('style_code')}")
            print(f"   Color: {product.get('color')}")
            print(f"   Price: ${product.get('price')}")
            print(f"   Sizes: {len(product.get('sizes', []))} available")
    
    print("\n✅ Done!")


if __name__ == "__main__":
    main()
