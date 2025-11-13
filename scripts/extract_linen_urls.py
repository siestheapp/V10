#!/usr/bin/env python3
"""
Extract actual product URLs from J.Crew's linen shirts page
"""

import requests
from bs4 import BeautifulSoup
import re
import json

def extract_linen_shirt_urls():
    """Extract product URLs from the J.Crew linen shirts page"""
    
    url = "https://www.jcrew.com/plp/mens/categories/clothing/shirts?sub-categories=men-shirts-linen"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    print(f"🔍 Fetching J.Crew linen shirts page...")
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Save HTML for inspection
    with open('jcrew_linen_page.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    print("📄 Saved page HTML to jcrew_linen_page.html for inspection")
    
    product_urls = set()
    
    # Method 1: Look for product links with specific patterns
    for link in soup.find_all('a', href=True):
        href = link['href']
        # J.Crew product URLs typically follow these patterns:
        # /p/mens/categories/clothing/shirts/.../PRODUCTCODE
        # /p/PRODUCTCODE
        if '/p/' in href and re.search(r'/[A-Z0-9]{4,6}(?:\?|$|/)', href):
            # Make absolute URL
            if href.startswith('/'):
                href = f"https://www.jcrew.com{href}"
            # Clean URL (remove query params)
            clean_url = href.split('?')[0]
            product_urls.add(clean_url)
    
    # Method 2: Look for data attributes that might contain product info
    for element in soup.find_all(attrs={'data-product-id': True}):
        product_id = element.get('data-product-id')
        if product_id:
            # Try to find associated link
            parent = element.find_parent('a', href=True)
            if parent:
                href = parent['href']
                if href.startswith('/'):
                    href = f"https://www.jcrew.com{href}"
                product_urls.add(href.split('?')[0])
    
    # Method 3: Look for product tiles/cards
    product_containers = soup.find_all('div', class_=re.compile(r'product|item|tile', re.I))
    for container in product_containers:
        link = container.find('a', href=True)
        if link:
            href = link['href']
            if '/p/' in href:
                if href.startswith('/'):
                    href = f"https://www.jcrew.com{href}"
                product_urls.add(href.split('?')[0])
    
    # Method 4: Look for JSON-LD structured data
    scripts = soup.find_all('script', type='application/ld+json')
    for script in scripts:
        try:
            data = json.loads(script.string)
            # Look for product URLs in structured data
            if isinstance(data, dict):
                if '@graph' in data:
                    for item in data['@graph']:
                        if item.get('@type') == 'Product' and 'url' in item:
                            product_urls.add(item['url'])
        except:
            pass
    
    # Method 5: Look for specific linen product codes mentioned on the page
    # These are common J.Crew linen shirt product codes
    known_linen_codes = [
        'BZ356', 'BZ357', 'BZ358',  # Baird McNutt variations
        'BC107', 'BC108',            # More Baird McNutt
        'H3096', 'H3097',            # Heritage linen
        'BW956', 'BW957',            # Camp collar
        'CB004', 'CB005',            # Classic linen
    ]
    
    for code in known_linen_codes:
        # Try different URL patterns
        product_urls.add(f"https://www.jcrew.com/p/{code}")
        product_urls.add(f"https://www.jcrew.com/p/mens/categories/clothing/shirts/linen-shirts/{code}")
    
    return list(product_urls)

def main():
    urls = extract_linen_shirt_urls()
    
    print(f"\n✅ Found {len(urls)} potential product URLs\n")
    
    # Group by product code
    by_code = {}
    for url in urls:
        match = re.search(r'/([A-Z0-9]{4,6})(?:\?|$|/)', url)
        if match:
            code = match.group(1)
            if code not in by_code:
                by_code[code] = []
            by_code[code].append(url)
    
    print(f"📊 Unique product codes: {len(by_code)}\n")
    
    # Save to file
    with open('jcrew_linen_urls.txt', 'w') as f:
        for code in sorted(by_code.keys()):
            urls_for_code = by_code[code]
            # Use the shortest URL for each code (likely the canonical one)
            best_url = min(urls_for_code, key=len)
            f.write(f"{best_url}\n")
            print(f"{code}: {best_url}")
    
    print(f"\n💾 Saved {len(by_code)} unique product URLs to jcrew_linen_urls.txt")

if __name__ == "__main__":
    main()

