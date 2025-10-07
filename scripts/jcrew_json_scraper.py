#!/usr/bin/env python3
"""
J.Crew Fast JSON Scraper - Extracts product data from embedded JSON instead of Selenium
Much faster than browser automation - inspired by successful Reiss JSON scraper
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

class JCrewJSONScraper:
    """Fast scraper for J.Crew using embedded JSON data extraction"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"macOS"',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Add some cookies to look more like a real browser
        self.session.cookies.update({
            'jcrew_siteid': '1',
            'OptanonAlertBoxClosed': '2024-01-01T00:00:00.000Z',
        })
    
    def extract_structured_data(self, html: str) -> Optional[Dict]:
        """
        Extract structured data from J.Crew HTML
        Look for:
        1. Facebook Pixel tracking data
        2. TikTok Pixel data  
        3. Google Tag Manager data
        4. LilyAI product data
        5. HTML fallback
        """
        
        # Method 1: Extract from Facebook Pixel tracking data
        facebook_data = self.extract_facebook_pixel_data(html)
        if facebook_data:
            print("✅ Found Facebook Pixel product data")
            return facebook_data
        
        # Method 2: Extract from TikTok Pixel data
        tiktok_data = self.extract_tiktok_pixel_data(html)
        if tiktok_data:
            print("✅ Found TikTok Pixel product data")
            return tiktok_data
        
        # Method 3: Look for Google Tag Manager data
        gtm_data = self.extract_gtm_data(html)
        if gtm_data:
            print("✅ Found Google Tag Manager product data")
            return gtm_data
        
        # Method 4: Parse from HTML as fallback
        print("⚠️ No structured JSON found, falling back to HTML parsing")
        return self.parse_html_fallback(html)
    
    def extract_facebook_pixel_data(self, html: str) -> Optional[Dict]:
        """Extract product data from Facebook Pixel tracking calls"""
        # Look for fbq tracking calls with product data
        patterns = [
            r'fbq\([^)]*"CREW_ViewProduct"[^)]*\{([^}]+)\}',
            r'fbq\([^)]*"ViewContent"[^)]*\{([^}]+)\}',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html, re.DOTALL)
            for match in matches:
                try:
                    # Clean up the match and try to parse as JSON-like data
                    # Extract key-value pairs
                    data_str = '{' + match + '}'
                    
                    # Extract product info using regex
                    product_code_match = re.search(r'content_ids:\s*\["([^"]+)"\]', match)
                    product_name_match = re.search(r'content_name:\s*"([^"]+)"', match)
                    price_match = re.search(r'value:\s*"([^"]+)"', match)
                    category_match = re.search(r'content_category:\s*"([^"]+)"', match)
                    subcategory_match = re.search(r'content_subCategory:\s*"([^"]+)"', match)
                    
                    if product_code_match and product_name_match:
                        product_data = {
                            'product_code': product_code_match.group(1),
                            'name': product_name_match.group(1).replace('PDP - ', '').replace(f' ({product_code_match.group(1)})', ''),
                            'price': float(price_match.group(1)) if price_match else None,
                            'category': category_match.group(1) if category_match else '',
                            'subcategory': subcategory_match.group(1) if subcategory_match else '',
                            'currency': 'USD',
                            'brand': 'J.Crew',
                            'colors': [],  
                            'fits': [],    
                            'sizes': [],   
                            'images': []   
                        }
                        
                        # Try to extract additional data from the same HTML
                        product_data.update(self.extract_additional_data(html, product_data['product_code']))
                        return product_data
                except Exception as e:
                    continue
        
        return None
    
    def extract_tiktok_pixel_data(self, html: str) -> Optional[Dict]:
        """Extract product data from TikTok Pixel tracking calls"""
        pattern = r'ttq\.track\("ViewContent",\s*\{([^}]+)\}'
        match = re.search(pattern, html)
        
        if match:
            try:
                content = match.group(1)
                
                product_code_match = re.search(r'content_id:\s*"([^"]+)"', content)
                product_name_match = re.search(r'content_name:\s*"([^"]+)"', content)
                price_match = re.search(r'value:\s*"([^"]+)"', content)
                
                if product_code_match and product_name_match:
                    return {
                        'product_code': product_code_match.group(1),
                        'name': product_name_match.group(1).replace('PDP - ', '').replace(f' ({product_code_match.group(1)})', ''),
                        'price': float(price_match.group(1)) if price_match else None,
                        'currency': 'USD',
                        'brand': 'J.Crew',
                        'colors': [],
                        'fits': [],
                        'sizes': [],
                        'images': []
                    }
            except Exception as e:
                pass
        
        return None
    
    def extract_additional_data(self, html: str, product_code: str) -> Dict:
        """Extract additional product data like colors, fits, sizes"""
        additional_data = {
            'colors': [],
            'fits': [],
            'sizes': [],
            'images': []
        }
        
        # Extract colors from image preload links
        color_pattern = rf'{product_code}_([A-Z0-9]+)_'
        color_matches = re.findall(color_pattern, html)
        if color_matches:
            additional_data['colors'] = list(set(color_matches))
        
        # Extract fits from various patterns
        fit_patterns = [
            r'"fit":\s*"([^"]+)"',
            r'data-fit="([^"]+)"',
            r'"fits":\s*\[([^\]]+)\]',
        ]
        
        fits = []
        for pattern in fit_patterns:
            fit_matches = re.findall(pattern, html, re.IGNORECASE)
            for match in fit_matches:
                if ',' in match:  # Array format
                    array_fits = [f.strip().strip('"') for f in match.split(',')]
                    fits.extend(array_fits)
                else:
                    fits.append(match)
        
        additional_data['fits'] = list(set([f for f in fits if f and len(f) > 1]))
        
        # Extract image URLs
        image_pattern = rf'{product_code}_[A-Z0-9]+[^"]*\.jpg|{product_code}_[A-Z0-9]+[^"]*\.jpeg'
        image_matches = re.findall(image_pattern, html, re.IGNORECASE)
        if image_matches:
            # Make URLs absolute
            full_images = []
            for img in image_matches:
                if not img.startswith('http'):
                    img = 'https://www.jcrew.com/' + img.lstrip('/')
                full_images.append(img)
            additional_data['images'] = list(set(full_images))
        
        return additional_data
    
    def extract_gtm_data(self, html: str) -> Optional[Dict]:
        """Extract product data from Google Tag Manager calls"""
        # Look for GTM data patterns - this would need more analysis of the actual GTM payload
        # For now, return None to fall back to other methods
        return None
    
    def parse_html_fallback(self, html: str) -> Optional[Dict]:
        """Fallback to parsing HTML directly"""
        soup = BeautifulSoup(html, 'html.parser')
        
        result = {
            'name': '',
            'product_code': '',
            'brand': 'J.Crew',
            'price': None,
            'currency': 'USD',
            'sizes': [],
            'colors': [],
            'fits': [],
            'images': [],
            'category': '',
            'subcategory': ''
        }
        
        # Get product name from h1
        h1 = soup.find('h1')
        if h1:
            result['name'] = h1.get_text(strip=True)
        
        # Extract product code from URL or page
        # Look for BE996 pattern in various places
        code_patterns = [
            r'/([A-Z]{2}\d{3,4})(?:\?|$|")',  # BE996, CM456 patterns
            r'"([A-Z]{2}\d{3,4})"',           # In quotes
        ]
        
        for pattern in code_patterns:
            matches = re.findall(pattern, html)
            if matches:
                result['product_code'] = matches[0]
                break
        
        # Get colors from image preload links (found in the HTML)
        # Extract product code dynamically
        product_code = result.get('product_code', 'BE996')
        color_pattern = rf'{product_code}_([A-Z0-9]+)_'
        color_matches = re.findall(color_pattern, html)
        if color_matches:
            # Convert color codes to more readable names and remove duplicates
            result['colors'] = list(set(color_matches))
        
        # Also try to extract fits from HTML elements or data attributes
        fit_patterns = [
            r'"fit":\s*"([^"]+)"',
            r'data-fit="([^"]+)"',
            r'"fits":\s*\[([^\]]+)\]',
        ]
        
        fits = []
        for pattern in fit_patterns:
            fit_matches = re.findall(pattern, html, re.IGNORECASE)
            for match in fit_matches:
                if ',' in match:  # Array format
                    array_fits = [f.strip().strip('"') for f in match.split(',')]
                    fits.extend(array_fits)
                else:
                    fits.append(match)
        
        # Remove duplicates and clean up
        result['fits'] = list(set([f for f in fits if f and len(f) > 1]))
        
        # Try to extract sizes
        size_patterns = [
            r'"sizes":\s*\[([^\]]+)\]',
            r'data-size="([^"]+)"',
        ]
        
        sizes = []
        for pattern in size_patterns:
            size_matches = re.findall(pattern, html, re.IGNORECASE)
            for match in size_matches:
                if ',' in match:  # Array format
                    array_sizes = [s.strip().strip('"') for s in match.split(',')]
                    sizes.extend(array_sizes)
                else:
                    sizes.append(match)
        
        result['sizes'] = list(set([s for s in sizes if s and len(s) <= 4]))  # Size labels are usually short
        
        # If no fits found yet, try to extract from HTML elements
        if not result['fits']:
            fit_elements = soup.find_all(['button', 'option'], text=re.compile(r'(Classic|Slim|Tall|Relaxed)', re.I))
            html_fits = []
            for elem in fit_elements:
                fit_text = elem.get_text(strip=True)
                if fit_text and fit_text not in html_fits:
                    html_fits.append(fit_text)
            result['fits'] = html_fits
        
        return result if result['product_code'] else None
    
    def scrape_product(self, url: str) -> Optional[Dict]:
        """
        Main entry point - scrape a J.Crew product URL
        Returns structured product data
        """
        print(f"\n🔍 Scraping J.Crew product: {url}")
        
        # Extract product code from URL
        url_parts = self.parse_url(url)
        print(f"   Product code: {url_parts['product_code']}")
        
        try:
            # Fetch HTML
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            html = response.text
            print(f"   ✅ Fetched HTML ({len(html)} bytes)")
            
            # Extract structured data
            product_data = self.extract_structured_data(html)
            
            if product_data:
                # Enhance with URL data
                product_data['url'] = url
                if not product_data.get('product_code'):
                    product_data['product_code'] = url_parts['product_code']
                
                # Add timestamp
                product_data['scraped_at'] = datetime.now().isoformat()
                
                print(f"   ✅ Extracted product: {product_data.get('name', 'Unknown')}")
                print(f"   💰 Price: ${product_data.get('price', 'N/A')}")
                print(f"   🎨 Colors found: {len(product_data.get('colors', []))}")
                print(f"   👔 Fits found: {len(product_data.get('fits', []))}")
                print(f"   📏 Sizes found: {len(product_data.get('sizes', []))}")
                
                return product_data
            else:
                print("   ❌ Failed to extract product data")
                return None
                
        except requests.RequestException as e:
            print(f"   ❌ Request failed: {e}")
            return None
    
    def parse_url(self, url: str) -> Dict:
        """Extract product code from J.Crew URL"""
        # Pattern: /p/.../BE996 or /p/BE996
        match = re.search(r'/([A-Z]{2}\d{3,4})(?:\?|$)', url)
        if match:
            return {'product_code': match.group(1)}
        return {'product_code': ''}
    
    def scrape_multiple(self, urls: List[str]) -> List[Dict]:
        """Scrape multiple J.Crew products"""
        results = []
        for url in urls:
            data = self.scrape_product(url)
            if data:
                results.append(data)
        return results


def main():
    """Test the scraper with J.Crew products"""
    scraper = JCrewJSONScraper()
    
    print("=" * 80)
    print("J.CREW FAST JSON SCRAPER TEST")
    print("=" * 80)
    
    # Test with the actual HTML file we have
    test_html_path = "dev/jcrew-example-page.html"
    if os.path.exists(test_html_path):
        print(f"🧪 Testing with local HTML file: {test_html_path}")
        
        with open(test_html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        print(f"   ✅ Loaded HTML ({len(html_content)} bytes)")
        
        # Extract structured data
        product_data = scraper.extract_structured_data(html_content)
        
        if product_data:
            # Add URL and timestamp
            product_data['url'] = "https://www.jcrew.com/p/mens/categories/clothing/shirts/broken-in-oxford/broken-in-organic-cotton-oxford-shirt/BE996"
            product_data['scraped_at'] = datetime.now().isoformat()
            
            # Save to JSON file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"jcrew_json_scraper_results_{timestamp}.json"
            with open(filename, 'w') as f:
                json.dump([product_data], f, indent=2)
            print(f"\n💾 Saved to {filename}")
            
            # Summary
            print("\n" + "=" * 80)
            print("SUCCESS - EXTRACTED DATA")
            print("=" * 80)
            print(f"📦 {product_data.get('name', 'Unknown')}")
            print(f"   Code: {product_data.get('product_code')}")
            print(f"   Price: ${product_data.get('price')}")
            print(f"   Category: {product_data.get('category')}")
            print(f"   Subcategory: {product_data.get('subcategory')}")
            print(f"   Colors: {len(product_data.get('colors', []))} found")
            print(f"   Fits: {product_data.get('fits', [])}")
            
        else:
            print("   ❌ Failed to extract product data from HTML")
    
    else:
        print("❌ HTML test file not found, trying live URL...")
        
        # Test URLs - known J.Crew products
        test_urls = [
            "https://www.jcrew.com/p/mens/categories/clothing/shirts/broken-in-oxford/broken-in-organic-cotton-oxford-shirt/BE996",
        ]
        
        all_results = []
        for url in test_urls:
            result = scraper.scrape_product(url)
            if result:
                all_results.append(result)
        
        if all_results:
            # Save to JSON file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"jcrew_json_scraper_results_{timestamp}.json"
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
            print(f"   Code: {result.get('product_code')}")
            print(f"   Price: ${result.get('price')}")
            print(f"   Colors: {len(result.get('colors', []))} found")
            print(f"   Fits: {result.get('fits', [])}")


if __name__ == "__main__":
    main()
