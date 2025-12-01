#!/usr/bin/env python3
"""Test real-time extraction for J.Crew product URLs"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def test_jcrew_extraction(product_url):
    """Test if we can extract product info from J.Crew URLs in real-time"""
    
    print(f"\n🔍 Testing extraction for: {product_url}")
    print("=" * 60)
    
    # Test product name extraction
    def extract_product_name_from_url(product_url: str) -> str:
        """Extract product name from URL path"""
        try:
            from urllib.parse import urlparse, unquote
            parsed = urlparse(product_url)
            path_parts = parsed.path.strip('/').split('/')
            
            # For J.Crew URLs
            if 'jcrew.com' in product_url.lower():
                # Look for the product name part (usually the last meaningful part before the product code)
                for part in reversed(path_parts):
                    if part and not part.isdigit() and len(part) > 3 and not part.isupper():
                        # Decode URL encoding and format nicely
                        name = unquote(part).replace('-', ' ').title()
                        return name
            
            return "Product Name Not Found"
        except:
            return "Product Name Not Found"
    
    # Test image extraction
    def extract_product_image_from_url(product_url: str) -> str:
        """Extract the main product image from a J.Crew product page"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = requests.get(product_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # J.Crew specific selectors
            image_selectors = [
                # J.Crew specific
                'img[data-testid="product-hero-image"]',
                'img[class*="hero-image"]',
                'img[class*="product-hero"]',
                'img[class*="product-image"]',
                'img[class*="main-image"]',
                # Meta tags (often more reliable)
                'meta[property="og:image"]',
                'meta[name="twitter:image"]',
                'meta[property="og:image:secure_url"]',
                # Any img with product in class or id
                'img[id*="product"]',
                'img[class*="product"]',
            ]
            
            for selector in image_selectors:
                element = soup.select_one(selector)
                if element:
                    if element.name == 'meta':
                        image_url = element.get('content')
                    else:
                        image_url = element.get('src') or element.get('data-src') or element.get('data-lazy-src')
                    
                    if image_url:
                        # Handle relative URLs
                        if image_url.startswith('//'):
                            image_url = 'https:' + image_url
                        elif image_url.startswith('/'):
                            parsed_url = urlparse(product_url)
                            image_url = f"{parsed_url.scheme}://{parsed_url.netloc}{image_url}"
                        elif not image_url.startswith('http'):
                            parsed_url = urlparse(product_url)
                            image_url = f"{parsed_url.scheme}://{parsed_url.netloc}/{image_url}"
                        
                        # Basic validation - check if it's likely an image
                        if any(ext in image_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']):
                            return image_url
            
            # Fallback: Look for any reasonable image
            images = soup.find_all('img')
            for img in images:
                src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                if src and any(keyword in src.lower() for keyword in ['product', 'item', 'main', 'hero', 'image']):
                    if src.startswith('//'):
                        src = 'https:' + src
                    elif src.startswith('/'):
                        parsed_url = urlparse(product_url)
                        src = f"{parsed_url.scheme}://{parsed_url.netloc}{src}"
                    elif not src.startswith('http'):
                        parsed_url = urlparse(product_url)
                        src = f"{parsed_url.scheme}://{parsed_url.netloc}/{src}"
                    
                    if any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']):
                        return src
            
            return "https://via.placeholder.com/300x400/000000/ffffff?text=J.Crew"
            
        except Exception as e:
            print(f"⚠️ Failed to extract product image: {str(e)}")
            return "https://via.placeholder.com/300x400/000000/ffffff?text=J.Crew"
    
    # Extract product info
    product_name = extract_product_name_from_url(product_url)
    print(f"✅ Product Name: {product_name}")
    
    product_image = extract_product_image_from_url(product_url)
    print(f"✅ Product Image: {product_image}")
    
    # Test if image is accessible
    if not product_image.startswith("https://via.placeholder"):
        try:
            img_response = requests.head(product_image, timeout=5)
            if img_response.status_code == 200:
                print(f"✅ Image is accessible (Status: {img_response.status_code})")
            else:
                print(f"⚠️  Image might not be accessible (Status: {img_response.status_code})")
        except:
            print("⚠️  Could not verify image accessibility")
    
    return {
        "product_name": product_name,
        "product_image": product_image,
        "extraction_successful": product_name != "Product Name Not Found" and not product_image.startswith("https://via.placeholder")
    }

# Test with sample J.Crew URLs
test_urls = [
    "https://www.jcrew.com/p/mens/categories/clothing/shirts/broken-in-oxford/broken-in-organic-cotton-oxford-shirt/BE996",
    "https://www.jcrew.com/p/mens/categories/clothing/t-shirts-polos/long-sleeve-t-shirts/long-sleeve-broken-in-t-shirt/AW939",
    "https://www.jcrew.com/p/mens/categories/clothing/shirts/flex-casual/flex-casual-shirt/BU222"
]

print("\n🧪 Testing J.Crew Real-Time Extraction")
print("=" * 60)

all_successful = True
for url in test_urls:
    result = test_jcrew_extraction(url)
    if not result["extraction_successful"]:
        all_successful = False
    print()

print("\n" + "=" * 60)
if all_successful:
    print("✅ All extractions successful - real-time extraction works well!")
else:
    print("⚠️  Some extractions failed - may need pre-scraping or improved extraction logic")

