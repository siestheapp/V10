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
from datetime import datetime

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
    
    def _extract_product_code(self, product_url: str) -> Optional[str]:
        """
        Extract product code from J.Crew URL for consistent caching
        Examples:
        - /p/mens/.../CL752?color=white -> CL752
        - /p/mens/.../BE996 -> BE996
        """
        import re
        
        # Pattern to match J.Crew product codes (usually 5-6 alphanumeric characters)
        # They appear at the end of the path before query parameters
        pattern = r'/([A-Z0-9]{4,6})(?:\?|$)'
        match = re.search(pattern, product_url)
        
        if match:
            return match.group(1)
        
        # Fallback: try to extract from the last segment of the path
        try:
            from urllib.parse import urlparse
            parsed = urlparse(product_url)
            path_segments = [seg for seg in parsed.path.split('/') if seg]
            
            # Look for product code pattern in last few segments
            for segment in reversed(path_segments[-3:]):
                if re.match(r'^[A-Z0-9]{4,6}$', segment):
                    return segment
        except:
            pass
        
        return None
    
    def _normalize_url_for_caching(self, product_url: str) -> str:
        """
        Create a normalized cache key based on product code ONLY
        Fit options are the same across all colors, so we don't need color-specific caching
        """
        product_code = self._extract_product_code(product_url)
        
        # Don't include color in cache key - fit options are the same for all colors
        # This ensures we find products in the database regardless of color
        if product_code:
            return f"jcrew_product_{product_code}"
        
        # Fallback to URL-based key (without color/fit params for consistency)
        from urllib.parse import urlparse
        parsed = urlparse(product_url)
        base_path = parsed.path
        
        # Create normalized cache key from path only
        cache_key = base_path.replace('/', '_')
        return f"jcrew_url_{cache_key}"
    
    def fetch_product(self, product_url: str) -> Optional[Dict]:
        """
        Fetch product data from J.Crew URL
        Returns product info or None if failed
        """
        # Check if it's a supported product type (all men's tops including outerwear)
        if not self._is_supported_product(product_url):
            print(
                "❌ Unsupported product type. Only J.Crew men's tops, outerwear, and pants/chinos are supported."
            )
            return None
        
        # Get normalized cache key for consistent caching across color variants
        cache_key = self._normalize_url_for_caching(product_url)
        product_code = self._extract_product_code(product_url)
        
        # First check cache using normalized key
        cached = self._check_cache_by_key(cache_key)
        if cached:
            print(f"✅ Found in cache (product {product_code}): {cached['product_name']}")
            return cached
        
        # Fallback: Check by product_code if cache_key doesn't match
        if product_code:
            cached = self._check_cache_by_product_code(product_code)
            if cached:
                print(f"✅ Found in cache by product code {product_code}: {cached['product_name']}")
                return cached
        
        # Only scrape if not in database at all
        print(f"🔍 Not in database, fetching from J.Crew: {product_url}")
        product_data = self._scrape_product(product_url)
        
        if product_data:
            # Add cache metadata
            product_data['cache_key'] = cache_key
            product_data['product_code'] = product_code
            product_data['original_url'] = product_url
            
            # Save to cache using normalized key
            self._save_to_cache_by_key(cache_key, product_data)
            print(f"✅ Cached new product (code {product_code}): {product_data['product_name']}")
        
        return product_data
    
    def _is_supported_product(self, product_url: str) -> bool:
        """Check if the product URL is for a supported category"""
        url_lower = product_url.lower()
        
        # Must be men's product
        if "/mens/" not in url_lower and "/men/" not in url_lower:
            return False
        
        # Supported categories - ALL men's tops (J.Crew uses ONE guide for all)
        supported_categories = [
            "/shirts/",
            "/dress-shirts/",  # ✅ Added for dress shirt URLs
            "/denim-shirts/",  # ✅ Added for denim shirt URLs
            "/t-shirts/",
            "/tshirts/",
            "/tshirts-and-polos/",  # ✅ Added for URLs like /tshirts-and-polos/t-shirt/
            "/polos/",
            "/sweaters/",
            "/sweatshirts/",
            "/hoodies/",
            "/jacket",   # ✅ Now supported - same size guide
            "/coat",     # ✅ Now supported - same size guide  
            "/outerwear/",  # ✅ Now supported - same size guide
            "/blazer",   # ✅ Now supported - same size guide
            "/pants/",
            "/pant/",
            "/chinos/",
            "/denim/",
            "/jeans/",
            "/bottoms/",
        ]
        
        # Check if URL contains any supported category
        return any(category in url_lower for category in supported_categories)
    
    def _check_cache(self, product_url: str) -> Optional[Dict]:
        """Check if product exists in cache (pre-scraped products never expire)"""
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        try:
            cur.execute("""
                SELECT product_name, product_code, product_image,
                       category, subcategory, sizes_available,
                       colors_available, material, fit_type, fit_options, price,
                       product_description, fit_details, created_at
                FROM jcrew_product_cache
                WHERE product_url = %s
            """, (product_url,))
            
            row = cur.fetchone()
            if row:
                print(f"📦 Cache hit for product: {row[1]}")
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
                    'fit_options': row[9],
                    'price': float(row[10]) if row[10] else None,
                    'product_description': row[11] if len(row) > 11 else '',
                    'fit_details': row[12] if len(row) > 12 else {}
                }
            else:
                print(f"📭 No cache found for URL: {product_url[:50]}...")
        finally:
            cur.close()
            conn.close()
        
        return None
    
    def _check_cache_by_key(self, cache_key: str) -> Optional[Dict]:
        """Check if product exists in cache using normalized cache key
        
        Pre-scraped products (ingested from JSON) never expire.
        Only products scraped on-demand expire after 7 days.
        """
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        try:
            # First try to find by cache_key - NO EXPIRATION for pre-scraped data
            # We trust our pre-scraped data and only expire on-demand scrapes
            cur.execute("""
                SELECT product_name, product_code, product_image,
                       category, subcategory, sizes_available,
                       colors_available, material, fit_type, fit_options, price,
                       product_description, fit_details, product_url, created_at
                FROM jcrew_product_cache
                WHERE cache_key = %s
                -- Only expire if it was scraped on-demand (has full URL in product_url)
                AND (
                    product_url NOT LIKE 'http%'  -- Pre-scraped products don't have full URLs
                    OR created_at > NOW() - INTERVAL '7 days'  -- On-demand scrapes expire after 7 days
                )
                ORDER BY created_at DESC
                LIMIT 1
            """, (cache_key,))
            
            row = cur.fetchone()
            if row and len(row) >= 14:  # Ensure we have enough columns
                print(f"📦 CACHE HIT: Product {row[1]} found in cache")
                # Map columns correctly (0-indexed)
                return {
                    'product_url': row[13] if len(row) > 13 else '',  # product_url is column 14
                    'product_name': row[0],      # column 1
                    'product_code': row[1],       # column 2
                    'product_image': row[2],      # column 3
                    'category': row[3],           # column 4
                    'subcategory': row[4],        # column 5
                    'sizes_available': row[5],    # column 6
                    'colors_available': row[6],   # column 7
                    'material': row[7],           # column 8
                    'fit_type': row[8],           # column 9
                    'fit_options': row[9] if row[9] is not None else [],  # column 10 - IMPORTANT: use DB value!
                    'price': float(row[10]) if row[10] else None,  # column 11
                    'product_description': row[11] if len(row) > 11 else '',  # column 12
                    'fit_details': row[12] if len(row) > 12 else {},  # column 13
                    'cache_key': cache_key
                }
            else:
                print(f"📭 No cache found for key: {cache_key}")
        except Exception as e:
            print(f"Cache lookup error: {e}")
        finally:
            cur.close()
            conn.close()
        
        return None
    
    def _check_cache_by_product_code(self, product_code: str) -> Optional[Dict]:
        """Fallback: Check cache by product_code when cache_key doesn't match"""
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        try:
            cur.execute("""
                SELECT product_name, product_code, product_image,
                       category, subcategory, sizes_available,
                       colors_available, material, fit_type, fit_options, price,
                       product_description, fit_details, product_url, created_at
                FROM jcrew_product_cache
                WHERE product_code = %s
                ORDER BY created_at DESC
                LIMIT 1
            """, (product_code,))
            
            row = cur.fetchone()
            if row and len(row) >= 14:
                print(f"📦 CACHE HIT (by product_code): Product {row[1]} found")
                return {
                    'product_url': row[13] if len(row) > 13 else '',
                    'product_name': row[0],
                    'product_code': row[1],
                    'product_image': row[2],
                    'category': row[3],
                    'subcategory': row[4],
                    'sizes_available': row[5],
                    'colors_available': row[6],
                    'material': row[7],
                    'fit_type': row[8],
                    'fit_options': row[9] if row[9] is not None else [],
                    'price': float(row[10]) if row[10] else None,
                    'product_description': row[11] if len(row) > 11 else '',
                    'fit_details': row[12] if len(row) > 12 else {},
                    'cache_key': f"jcrew_product_{product_code}"
                }
        except Exception as e:
            print(f"Product code lookup error: {e}")
        finally:
            cur.close()
            conn.close()
        
        return None
    
    def _scrape_product(self, product_url: str) -> Optional[Dict]:
        """Scrape product data from J.Crew website"""
        try:
            # First, get the original URL with color parameters for accurate image/price extraction
            print(f"🔍 Fetching product data from original URL: {product_url}")
            response_original = requests.get(product_url, headers=self.headers, timeout=10)
            response_original.raise_for_status()
            soup_original = BeautifulSoup(response_original.text, 'html.parser')
            
            # For fit options extraction, use the base URL without any parameters
            # to get all available fits, not just the selected one
            base_url = product_url
            soup_base = soup_original  # Default to original if no parameters
            
            if '?' in product_url:
                import urllib.parse
                parsed = urllib.parse.urlparse(product_url)
                # Use just the base URL without any query parameters
                base_url = urllib.parse.urlunparse((
                    parsed.scheme, parsed.netloc, parsed.path,
                    '', '', ''
                ))
                print(f"🔍 Using clean base URL for fit extraction: {base_url}")
                
                # Only fetch base URL if it's different from original
                if base_url != product_url:
                    response_base = requests.get(base_url, headers=self.headers, timeout=10)
                    response_base.raise_for_status()
                    soup_base = BeautifulSoup(response_base.text, 'html.parser')
            
            # Detect category from URL
            category_info = self._detect_category(product_url)
            
            # Extract product data - use original soup for color-specific data, base soup for fit options
            product_data = {
                'product_url': product_url,
                'product_name': self._extract_name(soup_original),
                'product_code': self._extract_code(product_url, soup_original),
                'product_image': self._extract_image(soup_original),  # Use original for correct color image
                'price': self._extract_price(soup_original),  # Use original for correct color price
                'sizes_available': self._extract_sizes(soup_original),
                'colors_available': self._extract_colors(soup_original),  # Use original to get all colors
                'material': self._extract_material(soup_original),
                'fit_type': self._extract_fit(soup_original),
                'fit_options': self._extract_fit_options(soup_base, base_url),  # Use base for all fit options
                'product_description': self._extract_description(soup_original),
                'fit_details': self._extract_fit_details(soup_original),
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
        elif '/shirts/' in url_lower or '/denim-shirts/' in url_lower:
            if 'casual' in url_lower or 'denim' in url_lower:
                return {'category': 'Shirts', 'subcategory': 'Casual'}
            elif 'dress' in url_lower:
                return {'category': 'Shirts', 'subcategory': 'Dress'}
            elif 'oxford' in url_lower:
                return {'category': 'Shirts', 'subcategory': 'Oxford'}
            else:
                return {'category': 'Shirts', 'subcategory': 'Casual'}

        # Bottoms / Pants
        elif any(keyword in url_lower for keyword in ['/pants/', '/pant/', '/chinos/', '/denim/', '/jeans/', '/bottoms/']):
            if 'denim' in url_lower or 'jean' in url_lower:
                return {'category': 'Pants', 'subcategory': 'Denim'}
            if 'chino' in url_lower:
                return {'category': 'Pants', 'subcategory': 'Chinos'}
            return {'category': 'Pants', 'subcategory': 'Classic'}
        
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
        """Extract available colors with visual information from J.Crew"""
        colors = []
        
        # Target multiple possible DOM patterns used by J.Crew
        selector_list = [
            '.js-product__color.colors-list__item',
            '.js-product__color',
            '.ProductPriceColors__color',
            '[data-qaid^="pdpProductPriceColorsGroupListItem"]'
        ]
        jcrew_color_elements = soup.select(', '.join(selector_list))
        
        for element in jcrew_color_elements:
            # Extract color information from J.Crew's data attributes
            color_name = (element.get('data-name') or '').strip()
            if not color_name:
                # Fallback to aria-label like "NAVY $39.50"
                aria = (element.get('aria-label') or '').strip()
                if aria:
                    color_name = aria.split('$')[0].strip()
            color_code = (element.get('data-code') or '').strip()  # e.g., WT0002
            product_code = (element.get('data-product') or '').strip()  # e.g., BW379
            
            if not color_name:
                continue
            
            # Clean up name casing
            color_name = color_name.replace(' undefined', '').strip().title()
            
            # Skip duplicates
            existing_names = [c.get('name', '') if isinstance(c, dict) else str(c) for c in colors]
            if color_name in existing_names:
                continue
            
            color_info = {
                'name': color_name,
                'code': color_code if color_code else None,
                'productCode': product_code if product_code else None
            }
            
            # Try to extract image URL for this color (img src or data-src/srcset)
            img_element = element.find('img')
            img_src = ''
            if img_element:
                img_src = img_element.get('src') or img_element.get('data-src') or ''
                if not img_src:
                    srcset = img_element.get('srcset') or ''
                    if srcset:
                        # Take the first URL from srcset
                        img_src = srcset.split(',')[0].strip().split(' ')[0]
            if img_src:
                if img_src.startswith('/'):
                    img_src = f"https://www.jcrew.com{img_src}"
                color_info['imageUrl'] = img_src
            
            # Also attempt to read a background color if present
            style = element.get('style', '')
            if 'background-color:' in style:
                import re
                hex_match = re.search(r'background-color:\s*#([0-9a-fA-F]{6})', style)
                if hex_match:
                    color_info['hex'] = f"#{hex_match.group(1)}"
                else:
                    rgb_match = re.search(r'background-color:\s*rgb\((\d+),\s*(\d+),\s*(\d+)\)', style)
                    if rgb_match:
                        r, g, b = rgb_match.groups()
                        color_info['hex'] = f"#{int(r):02x}{int(g):02x}{int(b):02x}"
            
            colors.append(color_info)
            print(f"🎨 Found color: {color_name} (code: {color_code})")
        
        print(f"🎨 Total colors extracted: {len(colors)}")
        
        # Fallback: try older selectors if J.Crew specific didn't work
        if not colors:
            color_elements = soup.select('[data-qaid*="color"], .color-selector__button, button[aria-label*="Color"]')
            for element in color_elements:
                color_text = element.get('aria-label', '') or element.text.strip()
                if color_text and len(color_text) < 50:
                    # Check if this color name already exists
                    existing_names = [c['name'] if isinstance(c, dict) else c for c in colors]
                    if color_text not in existing_names:
                        colors.append({'name': color_text.title()})
        
        # Return default if no colors found
        if not colors:
            colors = [{'name': 'Default'}]
        
        return colors
    
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
    
    def _extract_fit_options(self, soup: BeautifulSoup, product_url: str) -> list:
        """
        Extract ONLY the fit options that are actually selectable buttons on the page.
        DO NOT extract from JavaScript metadata which includes ALL possible fits.
        """
        fit_options = []
        
        # IMPORTANT: Only look for actual clickable fit buttons, not JavaScript metadata
        # JavaScript contains ALL possible fits, but we need only the ones actually available
        
        # Strategy 1: Look for buttons with data-qaid="pdpProductVariationsItem"
        # This is what J.Crew uses for actual fit selection buttons
        variation_buttons = soup.find_all('button', attrs={'data-qaid': lambda x: x and 'ProductVariationsItem' in x})
        
        if variation_buttons:
            for button in variation_buttons:
                button_text = button.get_text(strip=True)
                # Check if this is a fit button (not size or color)
                if button_text and any(fit in button_text for fit in ['Classic', 'Slim', 'Tall', 'Relaxed', 'Untucked']):
                    # Handle multi-word fits like "Slim Untucked"
                    if 'Slim' in button_text and 'Untucked' in button_text:
                        fit_options.append('Slim Untucked')
                    elif button_text not in fit_options:
                        fit_options.append(button_text)
            
            if fit_options:
                print(f"✅ Found {len(fit_options)} actual fit button(s): {fit_options}")
                return fit_options
        
        # Strategy 2: Look for ProductVariations wrapper with actual buttons
        if not fit_options:
            # Find any element with class containing "ProductVariations"
            variation_wrappers = soup.find_all(attrs={'class': lambda x: x and 'ProductVariations' in str(x)})
            
            for wrapper in variation_wrappers:
                buttons = wrapper.find_all('button')
                for button in buttons:
                    button_text = button.get_text(strip=True)
                    # Only get fit-related buttons
                    if button_text and any(fit in button_text for fit in ['Classic', 'Slim', 'Tall', 'Relaxed', 'Untucked']):
                        if 'Slim' in button_text and 'Untucked' in button_text:
                            if 'Slim Untucked' not in fit_options:
                                fit_options.append('Slim Untucked')
                        elif button_text not in fit_options:
                            fit_options.append(button_text)
            
            if fit_options:
                print(f"✅ Found {len(fit_options)} fit button(s) in ProductVariations: {fit_options}")
                return fit_options
        
        
        # Method 4: Look for actual fit selector buttons on the page (last resort)
        if not fit_options:
            pass  # Code is commented out below
        #     scripts = soup.find_all('script')
        #     for script in scripts:
        #         if script.string and 'fit=' in script.string:
        #             script_content = script.string
        #             # Look for all URLs with fit parameters
        #             fit_urls = re.findall(r'fit=([^&"]*)', script_content)
        #             if fit_urls:
        #                 for fit in fit_urls:
        #                     if fit and fit not in fit_options:
        #                         # Filter out inappropriate fit options based on gender and product type
        #                         if is_mens_product and fit.lower() == 'petite':
        #                             print(f"⚠️ Skipping 'Petite' fit option for men's product")
        #                             continue  # Skip "Petite" for men's products
        #                         
        #                         # Allow all valid fit options for all products including T-shirts
        #                         # J.Crew T-shirts do have Classic and Tall fit variations
        #                         
        #                         fit_options.append(fit)
        #                 
        #                 if fit_options:
        #                     print(f"🎯 Found fit options in JSON data (filtered for {'mens' if is_mens_product else 'womens'}): {fit_options}")
        #                 else:
        #                     print(f"🎯 No valid fit options found in JSON data for this product")
        #                 break
        
        # Method 2: Look for fit selector buttons on the page (fallback)
        if not fit_options:
            fit_selectors = [
                'button[data-testid*="fit"]',
                'button[aria-label*="fit"]',
                'button[data-testid*="Fit"]',
                'button[aria-label*="Fit"]',
                '.fit-selector button',
                'button[class*="fit"]',
                'button[class*="Fit"]',
                # More generic selectors for J.Crew's current structure
                'button[aria-label*="Classic"]',
                'button[aria-label*="Tall"]',
                'button[aria-label*="Slim"]',
                'button[aria-label*="Relaxed"]',
                'button[data-testid*="Classic"]',
                'button[data-testid*="Tall"]',
                'button[data-testid*="Slim"]',
                'button[data-testid*="Relaxed"]'
            ]
            
            for selector in fit_selectors:
                elements = soup.select(selector)
                for element in elements:
                    # Check both text content and aria-label
                    fit_text = element.get_text().strip()
                    aria_label = element.get('aria-label', '').strip()
                    
                    for text_source in [fit_text, aria_label]:
                        if text_source and text_source not in fit_options:
                            # Common J.Crew fit types
                            if any(fit in text_source.lower() for fit in ['classic', 'slim', 'tall', 'relaxed', 'untucked']):
                                fit_options.append(text_source)
        
        # Method 3: Look for buttons that might contain fit information (broader search)
        if not fit_options:
            all_buttons = soup.select('button')
            for button in all_buttons:
                button_text = button.get_text().strip().lower()
                aria_label = button.get('aria-label', '').strip().lower()
                
                # Check if button contains fit-related text
                for text_source in [button_text, aria_label]:
                    if any(fit_word in text_source for fit_word in ['classic', 'tall', 'slim', 'relaxed']):
                        # Extract the fit name
                        if 'classic' in text_source:
                            if 'Classic' not in fit_options:
                                fit_options.append('Classic')
                        if 'tall' in text_source:
                            if 'Tall' not in fit_options:
                                fit_options.append('Tall')
                        if 'slim' in text_source and 'untucked' not in text_source:
                            if 'Slim' not in fit_options:
                                fit_options.append('Slim')
                        if 'relaxed' in text_source:
                            if 'Relaxed' not in fit_options:
                                fit_options.append('Relaxed')
        
        # Method 4: Check URL parameters for fit options (if user is on a specific fit page)
        # BUT ONLY if we haven't found any other fit options - URL params alone don't indicate multiple options
        if not fit_options and 'fit=' in product_url:
            import urllib.parse
            parsed = urllib.parse.urlparse(product_url)
            params = urllib.parse.parse_qs(parsed.query)
            if 'fit' in params:
                current_fit = params['fit'][0]
                # Only add if it's a meaningful fit type, not just a default
                if current_fit.lower() in ['classic', 'slim', 'tall', 'relaxed', 'untucked']:
                    print(f"⚠️ Found fit parameter in URL: {current_fit} - but this doesn't guarantee multiple options exist")
                    # Don't add it to fit_options yet - we need to verify multiple options exist
        
        # Method 5: Look for fit information in product details or descriptions
        if not fit_options:
            fit_text_indicators = soup.find_all(text=re.compile(r'(classic|slim|tall|relaxed|untucked)', re.I))
            for text in fit_text_indicators:
                parent = text.parent
                if parent and any(cls in parent.get('class', []) for cls in ['fit', 'size', 'product']):
                    # Extract fit types from the text
                    fits = re.findall(r'\b(Classic|Slim|Tall|Relaxed|Untucked)\b', text, re.I)
                    for fit in fits:
                        if fit.title() not in fit_options:
                            fit_options.append(fit.title())
        
        # Method 6: Check for common J.Crew fit patterns in the page
        if not fit_options:
            page_text = soup.get_text().lower()
            common_fits = ['classic', 'slim', 'slim untucked', 'tall', 'relaxed']
            
            # Look for fit selection context (e.g., "Available in Classic and Slim fits")
            if any(indicator in page_text for indicator in ['available in', 'choose your fit', 'fit options']):
                for fit in common_fits:
                    if fit in page_text and fit.title() not in fit_options:
                        fit_options.append(fit.title())
        
        # Clean up and standardize fit names
        standardized_fits = []
        for fit in fit_options:
            fit_clean = fit.strip().title()
            if fit_clean == 'Slim Untucked':
                fit_clean = 'Slim Untucked'
            elif 'untucked' in fit_clean.lower():
                fit_clean = 'Slim Untucked'
            
            if fit_clean not in standardized_fits:
                standardized_fits.append(fit_clean)
        
        # Final validation: Be smarter about returning fit options
        
        # Check for actual fit selection UI elements (broader search)
        actual_fit_selectors = soup.select(
            'button[data-testid*="fit"], '
            'button[aria-label*="fit"], '
            '.fit-selector button, '
            '[data-fit-type], '
            '.product__fit-option, '
            '[data-qaid*="fitOption"], '
            'a[href*="fit="], '  # Links with fit parameter
            'input[name*="fit"], '  # Form inputs for fit
            'select[name*="fit"], '  # Dropdown for fit
            '[class*="fit-option"], '  # Any element with fit-option class
            '[id*="fit-option"]'  # Any element with fit-option id
        )
        
        # Also check if we're on a product that typically has fit options (dress shirts, suits, etc)
        is_dress_shirt = 'dress-shirt' in product_url.lower() or 'bowery' in product_url.lower() or 'ludlow' in product_url.lower()
        is_formal_wear = 'suit' in product_url.lower() or 'tuxedo' in product_url.lower() or 'blazer' in product_url.lower()
        
        # Check if the page explicitly mentions multiple fits in text
        page_text = soup.get_text().lower()
        has_fit_mentions = any(phrase in page_text for phrase in [
            'available in classic, slim',
            'classic and slim fit',
            'classic, slim, and tall',
            'choose your fit',
            'select fit'
        ])
        
        # If we're on a dress shirt or formal wear page, these ALWAYS have fit options at J.Crew
        if is_dress_shirt or is_formal_wear:
            # Look for the common J.Crew dress shirt fits
            common_dress_shirt_fits = ['Classic', 'Slim', 'Tall']
            if not standardized_fits or len(standardized_fits) <= 1:
                # Dress shirts and formal wear always have these fits at J.Crew
                print(f"📋 Detected dress shirt/formal wear, using standard J.Crew fits")
                standardized_fits = common_dress_shirt_fits
            
        # If no actual fit selection UI elements exist and we're not on a known fit product, don't return
        if not actual_fit_selectors and not (is_dress_shirt or is_formal_wear or has_fit_mentions):
            print(f"🚫 No fit selection UI found and not a known fit product. Not returning: {standardized_fits}")
            return []
        
        # Require multiple fit options - a single fit means no choice
        if len(standardized_fits) <= 1:
            # For dress shirts, if we only found one but URL has fit parameter, add common options
            if (is_dress_shirt or is_formal_wear) and 'fit=' in product_url:
                print(f"📋 Dress shirt with single fit, adding standard options")
                standardized_fits = ['Classic', 'Slim', 'Tall']
            else:
                print(f"🚫 Only found {len(standardized_fits)} fit option(s): {standardized_fits}. No variations exist.")
                return []
        
        print(f"✅ Found {len(standardized_fits)} fit options: {standardized_fits}")
        return standardized_fits
    
    def _save_to_cache(self, product_data: Dict):
        """Save product data to cache"""
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        try:
            cur.execute("""
                INSERT INTO jcrew_product_cache (
                    product_url, product_code, product_name, product_image,
                    category, subcategory, price, sizes_available,
                    colors_available, material, fit_type, fit_options, 
                    product_description, fit_details, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT (product_url) DO UPDATE SET
                    product_name = EXCLUDED.product_name,
                    product_image = EXCLUDED.product_image,
                    price = EXCLUDED.price,
                    sizes_available = EXCLUDED.sizes_available,
                    fit_options = EXCLUDED.fit_options,
                    product_description = EXCLUDED.product_description,
                    fit_details = EXCLUDED.fit_details,
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
                # Convert color dicts to strings
                [c['name'] if isinstance(c, dict) else c for c in product_data.get('colors_available', [])],
                product_data.get('material', ''),
                product_data.get('fit_type', 'Regular'),
                product_data.get('fit_options', []),
                product_data.get('product_description', ''),
                json.dumps(product_data.get('fit_details', {}))
            ))
            
            conn.commit()
        except Exception as e:
            print(f"❌ Error saving to cache: {e}")
            conn.rollback()
        finally:
            cur.close()
            conn.close()
    
    def _save_to_cache_by_key(self, cache_key: str, product_data: Dict):
        """Save product data to cache using normalized cache key"""
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        try:
            # First, check if cache_key column exists, if not add it
            cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'jcrew_product_cache' AND column_name = 'cache_key'
            """)
            
            if not cur.fetchone():
                print("🔧 Adding cache_key column to jcrew_product_cache table...")
                cur.execute("""
                    ALTER TABLE jcrew_product_cache 
                    ADD COLUMN IF NOT EXISTS cache_key VARCHAR(255)
                """)
                cur.execute("""
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_jcrew_cache_key_unique 
                    ON jcrew_product_cache(cache_key)
                """)
                conn.commit()
            
            # Insert or update with cache_key
            cur.execute("""
                INSERT INTO jcrew_product_cache (
                    product_url, product_code, product_name, product_image,
                    category, subcategory, price, sizes_available,
                    colors_available, material, fit_type, fit_options, 
                    product_description, fit_details, cache_key, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT (cache_key) DO UPDATE SET
                    product_url = EXCLUDED.product_url,
                    product_name = EXCLUDED.product_name,
                    product_image = EXCLUDED.product_image,
                    price = EXCLUDED.price,
                    sizes_available = EXCLUDED.sizes_available,
                    fit_options = EXCLUDED.fit_options,
                    product_description = EXCLUDED.product_description,
                    fit_details = EXCLUDED.fit_details,
                    updated_at = NOW()
            """, (
                product_data.get('original_url', product_data.get('product_url', '')),
                product_data.get('product_code', ''),
                product_data['product_name'],
                product_data.get('product_image', ''),
                product_data.get('category', 'Shirts'),
                product_data.get('subcategory', 'Casual'),
                product_data.get('price'),
                product_data.get('sizes_available', []),
                # Convert color dicts to strings
                [c['name'] if isinstance(c, dict) else c for c in product_data.get('colors_available', [])],
                product_data.get('material', ''),
                product_data.get('fit_type', 'Regular'),
                product_data.get('fit_options', []),
                product_data.get('product_description', ''),
                json.dumps(product_data.get('fit_details', {})),
                cache_key
            ))
            
            conn.commit()
            print(f"💾 Cached product with key: {cache_key}")
            
        except Exception as e:
            print(f"❌ Error saving to cache with key: {e}")
            conn.rollback()
        finally:
            cur.close()
            conn.close()
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract product description with fit and fabric details"""
        description_parts = []
        
        # Method 1: Look for specific product description text patterns
        # J.Crew often has description text in specific areas
        text_content = soup.get_text()
        
        # Look for common description patterns
        description_patterns = [
            r'Inspired by[^.]*\.[^.]*\.[^.]*\.',  # "Inspired by..." sentences
            r'[Tt]his [^.]*(?:cotton|fabric|fit|cut|made|designed)[^.]*\.[^.]*\.',  # "This tee is made from..."
            r'[Mm]ade from[^.]*\.[^.]*\.',  # "Made from..." sentences
            r'\d+(?:\.\d+)?[- ]ounce[^.]*\.[^.]*\.',  # Weight descriptions
            r'[Ww]ith [^.]*(?:room|fit|cut)[^.]*\.[^.]*\.',  # Fit descriptions
        ]
        
        for pattern in description_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                # Clean up the match
                clean_match = re.sub(r'\s+', ' ', match.strip())
                if len(clean_match) > 30 and clean_match not in description_parts:
                    description_parts.append(clean_match)
        
        # Method 2: Look for material and construction details
        material_patterns = [
            r'100% [^.]*\.',  # "100% cotton."
            r'[Rr]ib trim[^.]*\.',  # "Rib trim at neck."
            r'[Ss]hort sleeves\.',  # "Short sleeves."
            r'[Mm]achine wash\.',  # "Machine wash."
            r'[Ii]mported\.',  # "Imported."
        ]
        
        for pattern in material_patterns:
            matches = re.findall(pattern, text_content)
            for match in matches:
                clean_match = match.strip()
                if clean_match not in description_parts:
                    description_parts.append(clean_match)
        
        # Method 3: Look for fit-specific information
        fit_patterns = [
            r'[Ff]its? true to size[^.]*\.',  # "Fits true to size..."
            r'[Ss]leeves? (?:are )?[^.]*(?:longer|shorter)[^.]*\.',  # Sleeve length info
            r'[Mm]ore room (?:across|in)[^.]*\.',  # Room descriptions
        ]
        
        for pattern in fit_patterns:
            matches = re.findall(pattern, text_content)
            for match in matches:
                clean_match = match.strip()
                if clean_match not in description_parts:
                    description_parts.append(clean_match)
        
        # Combine and clean up
        if description_parts:
            # Join with spaces and limit length
            full_description = ' '.join(description_parts)
            # Remove excessive whitespace
            full_description = re.sub(r'\s+', ' ', full_description)
            # Limit to reasonable length (500 chars)
            if len(full_description) > 500:
                full_description = full_description[:500] + '...'
            return full_description
        
        return ""
    
    def _extract_fit_details(self, soup: BeautifulSoup) -> dict:
        """Extract specific fit details like model info, sizing notes, etc."""
        fit_details = {}
        
        # Look for model information
        model_info = soup.find(text=re.compile(r'Model is.*wearing', re.I))
        if model_info:
            fit_details['model_info'] = model_info.strip()
        
        # Look for fit information
        fit_info_selectors = [
            '[data-testid="size-fit"]',
            '.size-fit-info',
            '.fit-information'
        ]
        
        for selector in fit_info_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text().strip()
                if 'fit' in text.lower():
                    fit_details['fit_notes'] = text
        
        # Look for customer review summary
        review_text = soup.find(text=re.compile(r'based on.*customer reviews', re.I))
        if review_text:
            fit_details['customer_feedback'] = review_text.strip()
        
        # Look for specific fit notes (like sleeve length differences)
        fit_notes = soup.find_all(text=re.compile(r'(longer|shorter|different|due to|because of)', re.I))
        for note in fit_notes:
            if any(keyword in note.lower() for keyword in ['sleeve', 'fit', 'length', 'size']):
                if 'fit_notes' not in fit_details:
                    fit_details['fit_notes'] = []
                elif isinstance(fit_details['fit_notes'], str):
                    fit_details['fit_notes'] = [fit_details['fit_notes']]
                
                if isinstance(fit_details['fit_notes'], list):
                    fit_details['fit_notes'].append(note.strip())
        
        return fit_details


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
