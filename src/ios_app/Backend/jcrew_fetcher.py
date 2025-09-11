"""
J.Crew Product Fetcher - Real-time product data fetching and caching
"""

import requests
from bs4 import BeautifulSoup
import re
import json
from typing import Dict, Optional
import psycopg2
import sys
import os

# Add parent directory to path to import db_config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from db_config import DB_CONFIG

class JCrewProductFetcher:
    """Fetch J.Crew product data on-demand and cache it"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
    
    def fetch_product(self, product_url: str) -> Optional[Dict]:
        """
        Fetch product data from J.Crew URL
        Returns product info or None if failed
        """
        # Check if it's a supported product type (all men's tops including outerwear)
        if not self._is_supported_product(product_url):
            print(f"❌ Unsupported product type. Only J.Crew men's tops (shirts, sweaters, jackets) are supported.")
            return None
        
        # First check cache
        cached = self._check_cache(product_url)
        if cached:
            print(f"✅ Found in cache: {cached['product_name']}")
            return cached
        
        # Fetch from website
        print(f"🔍 Fetching from J.Crew: {product_url}")
        product_data = self._scrape_product(product_url)
        
        if product_data:
            # Save to cache
            self._save_to_cache(product_data)
            print(f"✅ Cached new product: {product_data['product_name']}")
        
        return product_data
    
    def _is_supported_product(self, product_url: str) -> bool:
        """Check if the product URL is for a supported category"""
        url_lower = product_url.lower()
        
        # Must be men's product
        if "/mens/" not in url_lower and "/men/" not in url_lower:
            return False
        
        # Check against database rules for smarter detection
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        try:
            # Check if URL matches any guide selection rules
            cur.execute("""
                SELECT COUNT(*) 
                FROM guide_selection_rules gsr
                JOIN brands b ON gsr.brand_id = b.id
                WHERE b.name = 'J.Crew' 
                AND gsr.rule_type = 'url_pattern'
                AND %s LIKE '%%' || gsr.pattern || '%%'
                AND gsr.is_active = true
            """, (url_lower,))
            
            count = cur.fetchone()[0]
            if count > 0:
                return True
                
            # Fallback to hardcoded categories for backward compatibility
            supported_categories = [
                "/shirts/",
                "/dress-shirts/",
                "/business-casual-shirts/",
                "/t-shirts/",
                "/tshirts/",
                "/polos/",
                "/sweaters/",
                "/sweatshirts/",
                "/hoodies/",
                "/henleys/",
                "/crewneck/"
            ]
            
            return any(category in url_lower for category in supported_categories)
            
        finally:
            cur.close()
            conn.close()
    
    def get_measurement_set_for_product(self, product_url: str) -> Optional[int]:
        """Get the appropriate measurement_set_id for this product"""
        url_lower = product_url.lower()
        
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        try:
            # Find best matching rule
            cur.execute("""
                SELECT gsr.measurement_set_id, gsr.priority
                FROM guide_selection_rules gsr
                JOIN brands b ON gsr.brand_id = b.id
                WHERE b.name = 'J.Crew' 
                AND gsr.rule_type = 'url_pattern'
                AND %s LIKE '%%' || gsr.pattern || '%%'
                AND gsr.is_active = true
                ORDER BY gsr.priority DESC
                LIMIT 1
            """, (url_lower,))
            
            result = cur.fetchone()
            if result:
                return result[0]
            
            # Default to regular tops (ID 26)
            return 26
            
        finally:
            cur.close()
            conn.close()
    
    def _check_cache(self, product_url: str) -> Optional[Dict]:
        """Check if product exists in cache"""
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        try:
            cur.execute("""
                SELECT product_name, product_code, product_image,
                       category, subcategory, sizes_available,
                       colors_available, material, fit_type, price
                FROM jcrew_product_cache
                WHERE product_url = %s
            """, (product_url,))
            
            row = cur.fetchone()
            if row:
                return {
                    'product_url': product_url,
                    'product_name': row[0],
                    'product_code': row[1],
                    'product_image': row[2],
                    'category': row[3],
                    'subcategory': row[4],
                    'sizes_available': row[5],
                    'colors_available': row[6],
                    'material': row[7],
                    'fit_type': row[8],
                    'price': float(row[9]) if row[9] else None
                }
        finally:
            cur.close()
            conn.close()
        
        return None
    
    def _scrape_product(self, product_url: str) -> Optional[Dict]:
        """Scrape product data from J.Crew website"""
        try:
            response = requests.get(product_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Detect category from URL
            category_info = self._detect_category(product_url)
            
            # Extract product data
            product_data = {
                'product_url': product_url,
                'product_name': self._extract_name(soup),
                'product_code': self._extract_code(product_url, soup),
                'product_image': self._extract_image(soup),
                'price': self._extract_price(soup),
                'sizes_available': self._extract_sizes(soup),
                'colors_available': self._extract_colors(soup),
                'material': self._extract_material(soup),
                'fit_type': self._extract_fit(soup),
                'category': category_info['category'],
                'subcategory': category_info['subcategory']
            }
            
            return product_data
            
        except Exception as e:
            print(f"❌ Error scraping {product_url}: {e}")
            # Return minimal data as fallback
            category_info = self._detect_category(product_url)
            return {
                'product_url': product_url,
                'product_name': self._extract_name_from_url(product_url),
                'product_code': self._extract_code_from_url(product_url),
                'product_image': '',
                'price': None,
                'sizes_available': ['XS', 'S', 'M', 'L', 'XL', 'XXL'],
                'colors_available': ['Default'],
                'material': '',
                'fit_type': 'Regular',
                'category': category_info['category'],
                'subcategory': category_info['subcategory']
            }
    
    def _detect_category(self, url: str) -> Dict[str, str]:
        """Detect product category and subcategory from URL"""
        url_lower = url.lower()
        
        # Sweaters & Sweatshirts (we have t-shirt guide which works for these)
        if '/sweaters/' in url_lower:
            return {'category': 'Sweaters', 'subcategory': 'Pullover'}
        elif any(x in url_lower for x in ['/sweatshirts/', '/hoodies/']):
            return {'category': 'Sweaters', 'subcategory': 'Sweatshirts'}
        
        # T-Shirts & Polos
        elif '/t-shirts/' in url_lower or '/tshirts/' in url_lower:
            return {'category': 'T-Shirts', 'subcategory': 'Short Sleeve'}
        elif '/polos/' in url_lower:
            return {'category': 'T-Shirts', 'subcategory': 'Polos'}
        
        # Shirts (default for other tops)
        elif '/shirts/' in url_lower:
            if 'casual' in url_lower:
                return {'category': 'Shirts', 'subcategory': 'Casual'}
            elif 'dress' in url_lower:
                return {'category': 'Shirts', 'subcategory': 'Dress'}
            elif 'oxford' in url_lower:
                return {'category': 'Shirts', 'subcategory': 'Oxford'}
            else:
                return {'category': 'Shirts', 'subcategory': 'Casual'}
        
        # Default for men's tops
        else:
            return {'category': 'Shirts', 'subcategory': 'Casual'}
    
    def _extract_name(self, soup: BeautifulSoup) -> str:
        """Extract product name"""
        # Try multiple selectors
        selectors = [
            'h1.product-name',
            'h1[data-qaid="pdpProductName"]',
            'h1.product__name',
            'meta[property="og:title"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                if selector.startswith('meta'):
                    return element.get('content', '').strip()
                else:
                    return element.text.strip()
        
        return "J.Crew Product"
    
    def _extract_name_from_url(self, url: str) -> str:
        """Extract product name from URL as fallback"""
        # For URLs like: /p/mens/categories/clothing/shirts/casual/broken-in-oxford-shirt/BE996
        parts = url.split('/')
        for part in reversed(parts):
            if part and not part.startswith('?') and len(part) > 5:
                # Skip product codes (usually short uppercase)
                if not (len(part) < 10 and part.isupper()):
                    # Convert URL slug to readable name
                    name = part.replace('-', ' ').title()
                    return name
        return "J.Crew Shirt"
    
    def _extract_code(self, url: str, soup: BeautifulSoup) -> str:
        """Extract product code from URL or page"""
        # First try URL
        code = self._extract_code_from_url(url)
        if code:
            return code
        
        # Try from page
        sku_element = soup.select_one('[data-qaid="pdpItemNumber"]')
        if sku_element:
            return sku_element.text.strip()
        
        return ""
    
    def _extract_code_from_url(self, url: str) -> str:
        """Extract product code from URL"""
        # Look for pattern like /BE996 or /p/BE996
        match = re.search(r'/([A-Z]{2}\d{3,4})(?:\?|$|/)', url)
        if match:
            return match.group(1)
        
        # Try last segment
        parts = url.rstrip('/').split('/')
        if parts:
            last = parts[-1].split('?')[0]
            if len(last) <= 8 and any(c.isdigit() for c in last):
                return last
        
        return ""
    
    def _extract_image(self, soup: BeautifulSoup) -> str:
        """Extract main product image"""
        # Try multiple selectors
        selectors = [
            'img.product__image',
            'img[data-qaid="pdpMainImage"]',
            'meta[property="og:image"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                if selector.startswith('meta'):
                    img_url = element.get('content', '')
                else:
                    img_url = element.get('src', '')
                
                # Make URL absolute
                if img_url and not img_url.startswith('http'):
                    img_url = f"https://www.jcrew.com{img_url}"
                
                return img_url
        
        return ""
    
    def _extract_price(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract product price"""
        price_element = soup.select_one('[data-qaid="pdpSalePrice"], .product__price--sale, .product__price')
        if price_element:
            price_text = price_element.text.strip()
            # Extract number from price text
            match = re.search(r'[\d,]+\.?\d*', price_text)
            if match:
                return float(match.group().replace(',', ''))
        return None
    
    def _extract_sizes(self, soup: BeautifulSoup) -> list:
        """Extract available sizes"""
        sizes = []
        
        # Try to find size buttons
        size_elements = soup.select('[data-qaid*="size"], .size-selector__button, button[aria-label*="Size"]')
        for element in size_elements:
            size_text = element.text.strip()
            if size_text and size_text not in sizes:
                sizes.append(size_text)
        
        # Default sizes if none found
        if not sizes:
            sizes = ['XS', 'S', 'M', 'L', 'XL', 'XXL']
        
        return sizes
    
    def _extract_colors(self, soup: BeautifulSoup) -> list:
        """Extract available colors"""
        colors = []
        
        # Try to find color options
        color_elements = soup.select('[data-qaid*="color"], .color-selector__button, button[aria-label*="Color"]')
        for element in color_elements:
            color_text = element.get('aria-label', '') or element.text.strip()
            if color_text and color_text not in colors:
                colors.append(color_text)
        
        return colors if colors else ['Default']
    
    def _extract_material(self, soup: BeautifulSoup) -> str:
        """Extract material/fabric information"""
        # Look in product details
        details = soup.select('.product-details__content li, .pdp-details li')
        for detail in details:
            text = detail.text.lower()
            if 'cotton' in text or 'polyester' in text or 'wool' in text:
                return detail.text.strip()
        
        return ""
    
    def _extract_fit(self, soup: BeautifulSoup) -> str:
        """Extract fit type"""
        # Look for fit information
        fit_element = soup.select_one('[data-qaid*="fit"], .product__fit')
        if fit_element:
            return fit_element.text.strip()
        
        # Check in title or description
        text = soup.text.lower()
        if 'slim' in text:
            return 'Slim'
        elif 'classic' in text or 'regular' in text:
            return 'Classic'
        elif 'relaxed' in text:
            return 'Relaxed'
        
        return 'Regular'
    
    def _save_to_cache(self, product_data: Dict):
        """Save product data to cache"""
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        try:
            cur.execute("""
                INSERT INTO jcrew_product_cache (
                    product_url, product_code, product_name, product_image,
                    category, subcategory, price, sizes_available,
                    colors_available, material, fit_type, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT (product_url) DO UPDATE SET
                    product_name = EXCLUDED.product_name,
                    product_image = EXCLUDED.product_image,
                    price = EXCLUDED.price,
                    sizes_available = EXCLUDED.sizes_available,
                    updated_at = NOW()
            """, (
                product_data['product_url'],
                product_data.get('product_code', ''),
                product_data['product_name'],
                product_data.get('product_image', ''),
                product_data.get('category', 'Shirts'),
                product_data.get('subcategory', 'Casual'),
                product_data.get('price'),
                product_data.get('sizes_available', []),
                product_data.get('colors_available', []),
                product_data.get('material', ''),
                product_data.get('fit_type', 'Regular')
            ))
            
            conn.commit()
        except Exception as e:
            print(f"❌ Error saving to cache: {e}")
        finally:
            cur.close()
            conn.close()


# Test function
if __name__ == "__main__":
    # Test with some J.Crew URLs
    test_urls = [
        "https://www.jcrew.com/p/mens/categories/clothing/shirts/casual/BH290",
        "https://www.jcrew.com/p/mens/categories/clothing/shirts/broken-in-oxford/broken-in-organic-cotton-oxford-shirt/BE996",
    ]
    
    fetcher = JCrewProductFetcher()
    
    for url in test_urls:
        print(f"\n{'='*60}")
        print(f"Testing: {url}")
        print('='*60)
        product = fetcher.fetch_product(url)
        if product:
            print(f"✅ Name: {product['product_name']}")
            print(f"✅ Code: {product['product_code']}")
            print(f"✅ Image: {product['product_image'][:80] if product['product_image'] else 'No image'}...")
            print(f"✅ Sizes: {product['sizes_available']}")
            print(f"✅ Price: ${product['price']}" if product['price'] else "Price not found")
        else:
            print(f"❌ Failed to fetch product data")
