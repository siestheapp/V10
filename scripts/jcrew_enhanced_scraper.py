#!/usr/bin/env python3
"""
Enhanced J.Crew Scraper - Extracts complete product data including materials and descriptions
Uses both JSON extraction AND Selenium for dynamic content when needed
"""

import requests
import json
import re
from typing import Dict, Optional, List, Tuple
from bs4 import BeautifulSoup
import sys
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_config import DB_CONFIG

class JCrewEnhancedScraper:
    """Enhanced scraper for J.Crew that extracts ALL product information"""
    
    def __init__(self, use_selenium=False):
        self.use_selenium = use_selenium
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        if self.use_selenium:
            self.setup_selenium()
    
    def setup_selenium(self):
        """Setup Selenium for dynamic content extraction"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    def extract_with_api(self, product_code: str) -> Optional[Dict]:
        """
        Try to extract product data using J.Crew's internal API endpoints
        """
        # J.Crew API endpoints for product data
        api_endpoints = [
            f"https://www.jcrew.com/api/productsearch/v1/products/{product_code}",
            f"https://www.jcrew.com/data/v1/US/products/{product_code}",
            f"https://www.jcrew.com/s7-img-facade/{product_code}_detail.json",
        ]
        
        for endpoint in api_endpoints:
            try:
                resp = self.session.get(endpoint, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    return self.parse_api_response(data, product_code)
            except:
                continue
        
        return None
    
    def parse_api_response(self, data: Dict, product_code: str) -> Dict:
        """Parse API response to extract all product details"""
        result = {
            'product_code': product_code,
            'name': data.get('name', ''),
            'brand': 'J.Crew',
            'price': None,
            'materials': [],
            'description': '',
            'details': [],
            'care_instructions': [],
            'sizes': [],
            'colors': [],
            'fits': [],
            'images': [],
            'category': '',
            'subcategory': ''
        }
        
        # Extract price
        if 'price' in data:
            if isinstance(data['price'], dict):
                result['price'] = data['price'].get('regularPrice', data['price'].get('salePrice'))
            else:
                result['price'] = data['price']
        
        # Extract materials and fabric composition
        if 'materials' in data:
            result['materials'] = data['materials']
        elif 'fabricContent' in data:
            result['materials'] = [data['fabricContent']]
        elif 'productDetails' in data:
            for detail in data['productDetails']:
                if 'fabric' in detail.lower() or 'material' in detail.lower():
                    result['materials'].append(detail)
        
        # Extract description
        if 'description' in data:
            result['description'] = data['description']
        elif 'longDescription' in data:
            result['description'] = data['longDescription']
        
        # Extract care instructions
        if 'careInstructions' in data:
            result['care_instructions'] = data['careInstructions']
        elif 'care' in data:
            result['care_instructions'] = [data['care']]
        
        # Extract product details
        if 'details' in data:
            if isinstance(data['details'], list):
                result['details'] = data['details']
            else:
                result['details'] = [data['details']]
        
        # Extract variants (colors, fits)
        if 'variants' in data:
            for variant in data['variants']:
                if 'color' in variant:
                    result['colors'].append(variant['color'])
                if 'fit' in variant:
                    result['fits'].append(variant['fit'])
                if 'size' in variant:
                    result['sizes'].append(variant['size'])
        
        return result
    
    def extract_with_selenium(self, url: str) -> Dict:
        """
        Use Selenium to extract ALL product information from fully rendered page
        """
        self.driver.get(url)
        time.sleep(3)  # Wait for page to load
        
        result = {
            'product_code': self.extract_product_code_from_url(url),
            'name': '',
            'brand': 'J.Crew',
            'price': None,
            'materials': [],
            'description': '',
            'details': [],
            'care_instructions': [],
            'sizes': [],
            'colors': [],
            'fits': [],
            'images': [],
            'category': '',
            'subcategory': '',
            'url': url
        }
        
        try:
            # Wait for product name
            name_elem = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1, .product-name"))
            )
            result['name'] = name_elem.text.strip()
        except:
            pass
        
        # Extract price
        try:
            price_elem = self.driver.find_element(By.CSS_SELECTOR, ".product-price, .price-sales, span[data-price]")
            price_text = price_elem.text
            price_match = re.search(r'\$?([\d.]+)', price_text)
            if price_match:
                result['price'] = float(price_match.group(1))
        except:
            pass
        
        # Extract materials and fabric - MOST IMPORTANT
        material_selectors = [
            ".product-details__fabric",
            ".fabric-content",
            "div[data-testid='fabric-content']",
            ".accordion__content li:contains('cotton')",
            ".accordion__content li:contains('polyester')",
            ".product-description li",
            ".details-section li"
        ]
        
        for selector in material_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in elements:
                    text = elem.text.strip()
                    if any(word in text.lower() for word in ['cotton', 'polyester', 'wool', 'linen', 'silk', 'nylon', '%']):
                        result['materials'].append(text)
            except:
                pass
        
        # Try to find materials in accordion/expandable sections
        try:
            # Click on "Details & Care" or similar accordion
            accordions = self.driver.find_elements(By.CSS_SELECTOR, ".accordion__header, button[aria-expanded], .expandable-header")
            for accordion in accordions:
                if any(word in accordion.text.lower() for word in ['detail', 'care', 'fabric', 'material']):
                    self.driver.execute_script("arguments[0].click();", accordion)
                    time.sleep(1)
                    
                    # Now look for content
                    content = self.driver.find_element(By.CSS_SELECTOR, ".accordion__content, .expandable-content")
                    lines = content.text.strip().split('\n')
                    
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        
                        # Categorize the line
                        if any(word in line.lower() for word in ['cotton', 'polyester', 'wool', 'linen', '%']):
                            result['materials'].append(line)
                        elif any(word in line.lower() for word in ['wash', 'dry', 'iron', 'clean']):
                            result['care_instructions'].append(line)
                        else:
                            result['details'].append(line)
        except:
            pass
        
        # Extract description
        try:
            desc_elem = self.driver.find_element(By.CSS_SELECTOR, ".product-description, .product-details__description")
            result['description'] = desc_elem.text.strip()
        except:
            pass
        
        # Extract fits
        try:
            fit_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[data-fit], .fit-selector button, .radio-group__option")
            for button in fit_buttons:
                fit_text = button.text.strip()
                if fit_text and len(fit_text) < 30:  # Reasonable length for fit name
                    result['fits'].append(fit_text)
        except:
            pass
        
        # Extract colors
        try:
            color_swatches = self.driver.find_elements(By.CSS_SELECTOR, ".color-swatch, button[aria-label*='color'], .swatch")
            for swatch in color_swatches:
                color_name = swatch.get_attribute('aria-label') or swatch.get_attribute('title') or swatch.get_attribute('data-color')
                if color_name:
                    result['colors'].append(color_name.strip())
        except:
            pass
        
        # Extract sizes
        try:
            size_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[data-size], .size-selector button")
            for button in size_buttons:
                size_text = button.text.strip()
                if size_text and len(size_text) <= 5:  # Size labels are short
                    result['sizes'].append(size_text)
        except:
            pass
        
        # Extract images
        try:
            img_elements = self.driver.find_elements(By.CSS_SELECTOR, ".product-image img, .carousel img, picture img")
            for img in img_elements:
                src = img.get_attribute('src')
                if src and 'facade' in src:
                    result['images'].append(src)
        except:
            pass
        
        # Clean up duplicates
        result['materials'] = list(set(result['materials']))
        result['details'] = list(set(result['details']))
        result['care_instructions'] = list(set(result['care_instructions']))
        result['colors'] = list(set(result['colors']))
        result['fits'] = list(set(result['fits']))
        result['sizes'] = list(set(result['sizes']))
        
        return result
    
    def extract_product_code_from_url(self, url: str) -> str:
        """Extract product code from URL"""
        match = re.search(r'/([A-Z]{2}\d{3,4})(?:\?|$)', url)
        return match.group(1) if match else ''
    
    def scrape_product(self, url_or_file: str) -> Dict:
        """
        Main method to scrape a J.Crew product
        """
        # Check if it's a file or URL
        if os.path.exists(url_or_file):
            # Local HTML file - extract basic info
            print(f"📂 Processing local file: {url_or_file}")
            with open(url_or_file, 'r', encoding='utf-8') as f:
                html = f.read()
            
            # Extract product code from HTML
            product_code_match = re.search(r'BE996|[A-Z]{2}\d{3,4}', html)
            if product_code_match:
                product_code = product_code_match.group(0)
                
                # First try API
                print(f"🔍 Trying API for product {product_code}...")
                api_data = self.extract_with_api(product_code)
                if api_data and api_data.get('materials'):
                    return api_data
                
                # If API doesn't give us materials, we need the live page
                print("⚠️ Local HTML doesn't contain full product details")
                print("💡 Would need to fetch from live URL for materials and descriptions")
                
                # Return what we can extract from local HTML
                from scripts.jcrew_json_scraper import JCrewJSONScraper
                basic_scraper = JCrewJSONScraper()
                return basic_scraper.scrape_from_html(html)
        
        else:
            # It's a URL
            print(f"🌐 Fetching from URL: {url_or_file}")
            
            # First try API
            product_code = self.extract_product_code_from_url(url_or_file)
            if product_code:
                api_data = self.extract_with_api(product_code)
                if api_data and api_data.get('materials'):
                    print("✅ Got full data from API")
                    return api_data
            
            # Fall back to Selenium for complete data
            if self.use_selenium:
                print("🤖 Using Selenium for dynamic content...")
                return self.extract_with_selenium(url_or_file)
            else:
                print("⚠️ Selenium not enabled, getting basic data only")
                resp = self.session.get(url_or_file)
                from scripts.jcrew_json_scraper import JCrewJSONScraper
                basic_scraper = JCrewJSONScraper()
                return basic_scraper.scrape_from_html(resp.text)
    
    def __del__(self):
        """Cleanup Selenium driver"""
        if hasattr(self, 'driver'):
            self.driver.quit()


def main():
    """Test the enhanced scraper"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced J.Crew Product Scraper')
    parser.add_argument('input', help='Product URL or local HTML file')
    parser.add_argument('--selenium', action='store_true', help='Use Selenium for dynamic content')
    parser.add_argument('--output', help='Output JSON file')
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("J.CREW ENHANCED SCRAPER")
    print("=" * 80)
    
    scraper = JCrewEnhancedScraper(use_selenium=args.selenium)
    result = scraper.scrape_product(args.input)
    
    if result:
        # Save to file
        output_file = args.output or f'jcrew_enhanced_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print("\n" + "=" * 80)
        print("EXTRACTION RESULTS")
        print("=" * 80)
        print(f"📦 Product: {result.get('name', 'Unknown')}")
        print(f"   Code: {result.get('product_code', 'Unknown')}")
        print(f"   Price: ${result.get('price', 'N/A')}")
        
        if result.get('materials'):
            print(f"\n🧵 Materials:")
            for material in result['materials']:
                print(f"   • {material}")
        else:
            print(f"\n⚠️ No materials found")
        
        if result.get('description'):
            print(f"\n📝 Description:")
            print(f"   {result['description'][:200]}...")
        
        if result.get('details'):
            print(f"\n📋 Details: {len(result['details'])} items")
            for detail in result['details'][:3]:
                print(f"   • {detail}")
        
        if result.get('care_instructions'):
            print(f"\n🧺 Care Instructions:")
            for care in result['care_instructions'][:3]:
                print(f"   • {care}")
        
        print(f"\n🎨 Colors: {len(result.get('colors', []))} found")
        print(f"📏 Fits: {result.get('fits', [])}")
        print(f"👕 Sizes: {result.get('sizes', [])[:10]}")
        
        print(f"\n💾 Saved to {output_file}")
    else:
        print("❌ Failed to extract product data")
    
    print("=" * 80)


if __name__ == "__main__":
    main()

