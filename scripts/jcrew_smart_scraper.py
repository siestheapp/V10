#!/usr/bin/env python3
"""
Smart J.Crew Scraper - Only scrapes NEW products not in database
"""

import json
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.jcrew_json_scraper import JCrewJSONScraper

class SmartJCrewScraper:
    def __init__(self):
        self.scraper = JCrewJSONScraper()
        self.existing_codes = self.load_existing_codes()
        self.new_products = []
        self.skipped_products = []
    
    def load_existing_codes(self):
        """Load existing J.Crew product codes from database export"""
        try:
            with open('existing_jcrew_codes.json', 'r') as f:
                data = json.load(f)
                print(f"📋 Loaded {data['count']} existing J.Crew products from database")
                print(f"   Brand ID: {data['brand_id']}")
                return set(data['codes'])
        except FileNotFoundError:
            print("⚠️ No existing codes file found, will scrape all")
            return set()
    
    def should_scrape(self, product_code):
        """Check if product should be scraped"""
        return product_code not in self.existing_codes
    
    def scrape_url(self, url):
        """Scrape a URL only if product is not in database"""
        # Extract product code from URL
        import re
        match = re.search(r'/([A-Z]{2}\d{3,4})(?:\?|$)', url)
        if not match:
            print(f"❌ Can't extract product code from: {url}")
            return None
        
        product_code = match.group(1)
        
        if self.should_scrape(product_code):
            print(f"✅ Scraping NEW product: {product_code}")
            result = self.scraper.scrape_product(url)
            if result:
                self.new_products.append(result)
            return result
        else:
            print(f"⏭️ Skipping EXISTING product: {product_code}")
            self.skipped_products.append(product_code)
            return None
    
    def scrape_batch(self, urls):
        """Scrape multiple URLs, skipping existing products"""
        print(f"\n🚀 Processing {len(urls)} URLs...")
        print(f"   Existing products in DB: {len(self.existing_codes)}")
        print("=" * 60)
        
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] {url}")
            self.scrape_url(url)
        
        # Summary
        print("\n" + "=" * 60)
        print("SCRAPING SUMMARY")
        print("=" * 60)
        print(f"✅ New products scraped: {len(self.new_products)}")
        print(f"⏭️ Existing products skipped: {len(self.skipped_products)}")
        
        if self.new_products:
            # Save new products
            filename = f'jcrew_new_products_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            with open(filename, 'w') as f:
                json.dump(self.new_products, f, indent=2)
            print(f"\n💾 Saved {len(self.new_products)} new products to {filename}")
            
            print("\nNew product codes:")
            for p in self.new_products[:10]:
                print(f"   {p['product_code']}: {p['name']}")
        
        if self.skipped_products:
            print(f"\nSkipped {len(self.skipped_products)} existing products:")
            print(f"   {', '.join(self.skipped_products[:10])}")
            if len(self.skipped_products) > 10:
                print(f"   ... and {len(self.skipped_products) - 10} more")
        
        return self.new_products


def main():
    # Test with some URLs
    test_urls = [
        "https://www.jcrew.com/p/mens/categories/clothing/shirts/broken-in-oxford/broken-in-organic-cotton-oxford-shirt/BE996",  # EXISTS
        "https://www.jcrew.com/p/mens/categories/clothing/shirts/secret-wash/secret-wash-cotton-poplin-shirt/BF792",  # EXISTS  
        "https://www.jcrew.com/p/mens/categories/clothing/sweaters/pullover/cotton-cashmere-crewneck-sweater/AZ455",  # NEW?
        "https://www.jcrew.com/p/mens/categories/clothing/pants/athletic/giant-fit-chino-pant/BN123",  # NEW?
    ]
    
    scraper = SmartJCrewScraper()
    
    # Or load URLs from file
    urls_file = 'jcrew_urls_to_scrape.txt'
    if os.path.exists(urls_file):
        with open(urls_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        print(f"📂 Loaded {len(urls)} URLs from {urls_file}")
    else:
        urls = test_urls
        print(f"🧪 Using {len(urls)} test URLs")
    
    scraper.scrape_batch(urls)


if __name__ == "__main__":
    main()
