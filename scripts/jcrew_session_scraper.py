#!/usr/bin/env python3
"""
J.Crew scraper with better session handling to avoid 403s
"""

import requests
import time
import json
from typing import Dict, Optional

class JCrewSessionScraper:
    def __init__(self):
        self.session = requests.Session()
        # More complete headers to look like a real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
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
        })
    
    def establish_session(self):
        """Visit homepage first to get cookies"""
        print("🍪 Establishing session with J.Crew...")
        
        # Visit homepage to get initial cookies
        homepage = self.session.get('https://www.jcrew.com', allow_redirects=True)
        if homepage.status_code == 200:
            print(f"   ✅ Got {len(self.session.cookies)} cookies")
            time.sleep(1)  # Be polite
            return True
        else:
            print(f"   ❌ Failed to establish session: {homepage.status_code}")
            return False
    
    def scrape_product(self, url: str) -> Optional[Dict]:
        """Scrape with established session"""
        # Add referer as if we clicked from homepage
        headers = {'Referer': 'https://www.jcrew.com/'}
        
        print(f"📡 Fetching: {url}")
        response = self.session.get(url, headers=headers)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            # Parse with the JSON scraper
            from scripts.jcrew_json_scraper import JCrewJSONScraper
            scraper = JCrewJSONScraper()
            return scraper.scrape_from_html(response.text)
        else:
            return None
    
    def scrape_batch(self, urls):
        """Scrape multiple URLs with session"""
        if not self.establish_session():
            print("❌ Failed to establish session")
            return []
        
        results = []
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}]")
            result = self.scrape_product(url)
            if result:
                results.append(result)
            
            # Random delay to look human
            import random
            time.sleep(random.uniform(1, 3))
        
        return results

if __name__ == "__main__":
    # Test with one URL
    test_url = "https://www.jcrew.com/p/mens/categories/clothing/jeans/denim-shirts/midweight-denim-western-shirt/BX004"
    
    scraper = JCrewSessionScraper()
    result = scraper.scrape_product(test_url)
    
    if result:
        print("✅ Success!")
        print(json.dumps(result, indent=2))
    else:
        print("❌ Still blocked - might need Selenium or manual download")

