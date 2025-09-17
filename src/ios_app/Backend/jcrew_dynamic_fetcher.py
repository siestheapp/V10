#!/usr/bin/env python3
"""
Dynamic J.Crew product fetcher that returns fit-specific data
allowing the app to update product name and colors as user toggles fits.

This replicates the J.Crew website behavior where selecting different fits:
1. Changes the product name (e.g., "Slim Broken-in..." vs "Broken-in...")
2. Updates available colors (different fits have different color options)
3. Updates the URL with fit parameter
"""

import re
import requests
import psycopg2
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import sys
import os

# Add parent directory to path to import db_config (matching jcrew_fetcher.py pattern)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from db_config import DB_CONFIG

# Try to import the precise scraper for fit extraction
try:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    from scripts.precise_jcrew_html_scraper_v2 import PreciseJCrewScraperV2
    PRECISE_SCRAPER_AVAILABLE = True
except ImportError:
    PRECISE_SCRAPER_AVAILABLE = False
    print("⚠️ Precise scraper not available, using fallback fit detection")

class JCrewDynamicFetcher:
    # Class-level cache shared across all instances
    _product_cache = {}
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
    
    def fetch_product(self, product_url: str) -> Optional[Dict]:
        """
        Fetch product with fit-specific variations
        Returns data that allows dynamic UI updates
        """
        product_code = self._extract_product_code(product_url)
        if not product_code:
            print(f"❌ Could not extract product code from URL")
            return None
        
        print(f"🔍 Fetching dynamic data for {product_code}")
        
        # Get base product data from database cache (primary) with memory cache optimization
        cached_base = self._get_base_from_cache(product_code)
        
        if cached_base:
            print(f"✅ Found {product_code} in cache with {len(cached_base.get('fit_options', []))} fit options")
            
            # Build fit variations data structure
            fit_variations = self._build_fit_variations(cached_base, product_code)
            
            # Get current fit from URL
            current_fit = self._extract_current_fit(product_url) or 'Classic'
            
            # Build response with dynamic data
            return {
                'product_code': product_code,
                'base_product_name': self._get_base_product_name(cached_base['product_name']),
                'current_fit': current_fit,
                'current_product_name': self._build_product_name(cached_base['product_name'], current_fit),
                'product_url': product_url,
                'product_image': cached_base.get('product_image') or f'https://www.jcrew.com/s7-img-facade/{product_code}_SU0001?$pdp_enlarge$',
                
                # All available fit options
                'fit_options': cached_base.get('fit_options', []),
                
                # Fit-specific variations (for dynamic updates)
                'fit_variations': fit_variations,
                
                # Current selection data
                'sizes_available': cached_base.get('sizes_available', ['XS', 'S', 'M', 'L', 'XL', 'XXL']),
                'colors_available': self._get_colors_for_fit(fit_variations, current_fit, cached_base.get('colors_available', [])),
                
                # Other metadata
                'price': cached_base.get('price'),
                'category': cached_base.get('category'),
                'subcategory': cached_base.get('subcategory'),
                'material': cached_base.get('material')
            }
        
        # If not in database cache, return None (no real-time scraping in production)
        print(f"📦 DATABASE CACHE MISS: Product {product_code} not available in cache")
        print(f"💡 To add this product, run the scraper script to populate the cache")
        return None
    
    def _get_base_product_name(self, full_name: str) -> str:
        """Extract base product name without fit prefix"""
        if not full_name:
            return "J.Crew Product"
        
        # Remove fit prefixes
        name = full_name
        fit_prefixes = ['Slim Untucked ', 'Slim ', 'Tall ', 'Relaxed ', 'Classic ']
        for prefix in fit_prefixes:
            if name.startswith(prefix):
                name = name[len(prefix):]
                break
        
        return name
    
    def _build_product_name(self, base_name: str, fit: str) -> str:
        """Build product name with fit prefix"""
        base = self._get_base_product_name(base_name)
        
        if fit == 'Classic' or not fit:
            return base
        elif fit == 'Slim':
            return f"Slim {base}"
        elif fit == 'Slim Untucked':
            return f"Slim Untucked {base}"
        elif fit == 'Tall':
            return f"Tall {base}"
        elif fit == 'Relaxed':
            return f"Relaxed {base}"
        else:
            return base
    
    def _build_fit_variations(self, cached_data: Dict, product_code: str) -> Dict:
        """
        Build fit-specific variations data
        This allows the app to update dynamically when user toggles fits
        """
        base_name = self._get_base_product_name(cached_data.get('product_name', ''))
        fit_options = cached_data.get('fit_options', [])
        base_colors = cached_data.get('colors_available', [])
        
        variations = {}
        
        for fit in fit_options:
            variations[fit] = {
                'product_name': self._build_product_name(base_name, fit),
                'colors_available': self._estimate_colors_for_fit(fit, base_colors),
                'product_url': self._build_fit_url(product_code, fit)
            }
        
        # If no fit options, treat as single variant
        if not fit_options:
            variations['Classic'] = {
                'product_name': base_name,
                'colors_available': base_colors,
                'product_url': f"https://www.jcrew.com/p/{product_code}"
            }
        
        return variations
    
    def _estimate_colors_for_fit(self, fit: str, base_colors: List[str]) -> List[str]:
        """
        Estimate colors for a specific fit
        In reality, different fits may have different colors available
        This is a simplified version - ideally we'd scrape each fit URL
        """
        # For now, return all colors for all fits
        # A more sophisticated version would track fit-specific colors
        return base_colors
    
    def _get_colors_for_fit(self, variations: Dict, fit: str, default_colors: List[str]) -> List[str]:
        """Get colors available for a specific fit"""
        if fit in variations:
            return variations[fit].get('colors_available', default_colors)
        return default_colors
    
    def _build_fit_url(self, product_code: str, fit: str) -> str:
        """Build URL for a specific fit"""
        base_url = f"https://www.jcrew.com/p/{product_code}"
        
        if fit == 'Classic':
            return f"{base_url}?display=standard&fit=Classic"
        elif fit == 'Slim':
            return f"{base_url}?display=standard&fit=Slim"
        elif fit == 'Slim Untucked':
            return f"{base_url}?display=standard&fit=Slim%20Untucked"
        elif fit == 'Tall':
            return f"{base_url}?display=standard&fit=Tall"
        elif fit == 'Relaxed':
            return f"{base_url}?display=standard&fit=Relaxed"
        else:
            return base_url
    
    def _extract_product_code(self, url: str) -> str:
        """Extract product code from URL"""
        patterns = [
            r'/([A-Z]{2}\d{3,4})(?:\?|$|/)',  # /CM389? or /CM389/
            r'[?&]productCode=([A-Z]{2}\d{3,4})',  # ?productCode=CM389
            r'/p/([A-Z]{2}\d{3,4})',  # /p/CM389
            r'/([A-Z]{2}\d{3,4})/',  # /ME625/ (for mobile URLs)
            r'[?&]colorProductCode=([A-Z]{2}\d{3,4})',  # ?colorProductCode=CM390
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                return match.group(1).upper()
        return ""
    
    def _extract_current_fit(self, url: str) -> Optional[str]:
        """Extract currently selected fit from URL"""
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        if 'fit' in params:
            fit = params['fit'][0]
            if fit.lower() == 'slim untucked':
                return 'Slim Untucked'
            return fit.title()
        
        return 'Classic'  # Default to Classic
    
    def _get_base_from_cache(self, product_code: str) -> Optional[Dict]:
        """Get base product data from database cache (primary) with memory cache as optimization"""
        # Check in-memory cache first for performance optimization
        if product_code in JCrewDynamicFetcher._product_cache:
            print(f"💾 Found {product_code} in memory cache")
            return JCrewDynamicFetcher._product_cache[product_code]
        
        # Primary source: database cache (persistent across restarts)
        print(f"🔍 Checking database cache for {product_code}")
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        try:
            cur.execute("""
                SELECT product_name, product_code, product_image,
                       category, subcategory, sizes_available,
                       colors_available, material, fit_type, fit_options, price
                FROM jcrew_product_cache
                WHERE product_code = %s
                LIMIT 1
            """, (product_code,))
            
            row = cur.fetchone()
            if row:
                print(f"✅ Found {product_code} in database cache")
                data = {
                    'product_name': row[0] or "J.Crew Product",
                    'product_code': row[1],
                    'product_image': row[2],
                    'category': row[3],
                    'subcategory': row[4],
                    'sizes_available': row[5] or ['XS', 'S', 'M', 'L', 'XL', 'XXL'],
                    'colors_available': row[6] or [],
                    'material': row[7],
                    'fit_type': row[8],
                    'fit_options': row[9] or [],
                    'price': float(row[10]) if row[10] else None
                }
                # Save to memory cache for performance optimization (not primary storage)
                JCrewDynamicFetcher._product_cache[product_code] = data
                print(f"💾 Cached {product_code} in memory for performance")
                return data
            else:
                print(f"❌ {product_code} not found in database cache")
        
        except Exception as e:
            print(f"❌ Database error for {product_code}: {e}")
            # Database table might not exist, ignore
            pass
        finally:
            cur.close()
            conn.close()
        
        return None
    
    def _scrape_dynamic_data(self, product_url: str) -> Optional[Dict]:
        """
        Scrape fresh dynamic data from J.Crew
        This would ideally scrape each fit URL for accurate colors
        """
        try:
            product_code = self._extract_product_code(product_url)
            current_fit = self._extract_current_fit(product_url)
            
            # Use precise scraper for fit extraction if available
            if PRECISE_SCRAPER_AVAILABLE:
                print("🔧 Using precise scraper for fit extraction")
                scraper = PreciseJCrewScraperV2(headless=False)  # Changed to False for better detection
                try:
                    precise_result = scraper.scrape_product(product_url)
                    fit_options = precise_result.get('fits', [])
                    print(f"✅ Precise scraper found {len(fit_options)} fit options: {fit_options}")
                except Exception as e:
                    print(f"⚠️ Precise scraper failed: {e}, falling back to regular extraction")
                    fit_options = []
                finally:
                    scraper.close()
            else:
                fit_options = []
            
            response = requests.get(product_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract product name
            name_elem = soup.select_one('h1[class*="product"]')
            product_name = name_elem.get_text(strip=True) if name_elem else "J.Crew Product"
            base_name = self._get_base_product_name(product_name)
            
            # If precise scraper didn't find fits, try regular extraction
            if not fit_options:
                fit_options = self._extract_fit_options(soup)
            
            # Extract colors
            colors = self._extract_colors(soup)
            
            # Extract sizes
            sizes = self._extract_sizes(soup)
            
            # Extract image
            image = self._extract_image(soup)
            
            # Build fit variations
            variations = {}
            for fit in fit_options:
                variations[fit] = {
                    'product_name': self._build_product_name(base_name, fit),
                    'colors_available': colors,  # Would need per-fit scraping for accuracy
                    'product_url': self._build_fit_url(product_code, fit)
                }
            
            if not fit_options:
                fit_options = ['Classic']
                variations['Classic'] = {
                    'product_name': base_name,
                    'colors_available': colors,
                    'product_url': product_url
                }
            
            return {
                'product_code': product_code,
                'base_product_name': base_name,
                'current_fit': current_fit,
                'current_product_name': product_name,
                'product_url': product_url,
                'product_image': image or f'https://www.jcrew.com/s7-img-facade/{product_code}_SU0001?$pdp_enlarge$',
                'fit_options': fit_options,
                'fit_variations': variations,
                'sizes_available': sizes or ['XS', 'S', 'M', 'L', 'XL', 'XXL'],
                'colors_available': colors,
                'price': None
            }
            
        except Exception as e:
            print(f"❌ Error scraping dynamic data: {e}")
            return None
    
    def _extract_fit_options(self, soup: BeautifulSoup) -> List[str]:
        """Extract available fit options from page"""
        fits = []
        
        # Strategy 1: Look for variant selector elements (most reliable)
        variant_selectors = soup.find_all('button', attrs={'class': re.compile(r'variant-selector', re.I)})
        
        for button in variant_selectors:
            text = button.get_text(strip=True)
            if text and text not in fits:
                # Check if it's a fit option (not size/color)
                fit_keywords = ['Classic', 'Slim', 'Tall', 'Relaxed', 'Untucked', 'Regular', 'Athletic']
                if any(keyword in text for keyword in fit_keywords):
                    fits.append(text)
                    print(f"      Found fit (Strategy 1): {text}")
        
        # Strategy 2: Look for button groups with fit-related aria-labels
        if not fits:
            button_groups = soup.find_all(attrs={'aria-label': re.compile(r'fit', re.I)})
            for group in button_groups:
                buttons = group.find_all('button')
                for button in buttons:
                    text = button.get_text(strip=True)
                    if text and text not in fits:
                        fits.append(text)
                        print(f"      Found fit (Strategy 2): {text}")
        
        # Strategy 3: Look for any buttons with fit keywords
        if not fits:
            all_buttons = soup.find_all('button')
            fit_keywords = ['Classic', 'Slim', 'Tall', 'Relaxed', 'Untucked', 'Regular', 'Athletic', 'Traditional']
            
            for button in all_buttons:
                text = button.get_text(strip=True)
                # Check if this looks like a fit option
                if text and any(keyword in text for keyword in fit_keywords):
                    # Avoid navigation buttons
                    if not any(x in text.lower() for x in ['shop', 'add', 'cart', 'size', 'review']):
                        if text not in fits:
                            fits.append(text)
                            print(f"      Found fit (Strategy 3): {text}")
        
        # Handle multi-word fits like "Slim Untucked"
        if 'Slim' in fits and 'Untucked' in fits and 'Slim Untucked' not in fits:
            # Check if there's actually a "Slim Untucked" button
            slim_untucked_elem = soup.find('button', string=re.compile(r'Slim\s+Untucked', re.I))
            if slim_untucked_elem:
                fits.append('Slim Untucked')
                # Remove individual parts if they exist
                if 'Untucked' in fits and len([f for f in fits if 'Untucked' in f]) > 1:
                    fits.remove('Untucked')
                print(f"      Found compound fit: Slim Untucked")
        
        print(f"   ✅ Found {len(fits)} fit options: {fits}")
        return fits if fits else []
    
    def _extract_colors(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract available colors with visual information from J.Crew"""
        colors = []
        
        # Target multiple possible DOM patterns used by J.Crew (matching jcrew_fetcher.py)
        selector_list = [
            '.js-product__color.colors-list__item',
            '.js-product__color',
            '.ProductPriceColors__color',
            '[data-qaid^="pdpProductPriceColorsGroupListItem"]',
            'div[data-code][data-name]'  # Added to match the HTML user provided
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
            color_code = (element.get('data-code') or '').strip()  # e.g., YD8609
            product_code = (element.get('data-product') or '').strip()  # e.g., BE996
            
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
                # Remove dollar sign parameters that might cause issues in Swift URL handling
                if '$' in img_src:
                    img_src = img_src.split('?')[0]  # Keep base URL without parameters
                color_info['imageUrl'] = img_src
            
            # Also attempt to read a background color if present
            style = element.get('style', '')
            if 'background-color:' in style:
                import re as regex
                hex_match = regex.search(r'background-color:\s*#([0-9a-fA-F]{6})', style)
                if hex_match:
                    color_info['hex'] = f"#{hex_match.group(1)}"
                else:
                    rgb_match = regex.search(r'background-color:\s*rgb\((\d+),\s*(\d+),\s*(\d+)\)', style)
                    if rgb_match:
                        r, g, b = rgb_match.groups()
                        color_info['hex'] = f"#{int(r):02x}{int(g):02x}{int(b):02x}"
            
            colors.append(color_info)
            print(f"🎨 Found color: {color_name} (code: {color_code}, image: {bool(img_src)})")
        
        print(f"🎨 Total colors extracted: {len(colors)}")
        
        # Fallback to simpler extraction if no colors found with above method
        if not colors:
            color_inputs = soup.find_all('input', attrs={'aria-label': re.compile(r'^[^$]+\$\d+', re.I)})
            
            for inp in color_inputs:
                aria_label = inp.get('aria-label', '')
                color_match = re.match(r'^([^$]+)', aria_label.strip())
                if color_match:
                    color_name = color_match.group(1).strip().title()
                    if color_name and color_name not in [c.get('name', c) for c in colors]:
                        colors.append({'name': color_name})
        
        return colors
    
    def _extract_sizes(self, soup: BeautifulSoup) -> List[str]:
        """Extract available sizes"""
        sizes = []
        
        size_buttons = soup.find_all(['button', 'input'], text=re.compile(r'^(XS|S|M|L|XL|XXL)$'))
        
        for elem in size_buttons:
            size = elem.get_text(strip=True)
            if size and size not in sizes:
                sizes.append(size)
        
        size_order = ['XS', 'S', 'M', 'L', 'XL', 'XXL']
        sizes.sort(key=lambda x: size_order.index(x) if x in size_order else 999)
        
        return sizes
    
    def _extract_image(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product image"""
        img = soup.select_one('img[class*="mainImg"], img[src*="/s7-img-facade/"]')
        if img and img.get('src'):
            src = img['src']
            if src.startswith('//'):
                src = 'https:' + src
            elif not src.startswith('http'):
                src = 'https://www.jcrew.com' + src
            return src
        return None
    
    def _save_to_cache(self, product_code: str, data: Dict):
        """Save scraped data to in-memory cache"""
        # Save to memory cache
        JCrewDynamicFetcher._product_cache[product_code] = data
        print(f"💾 Saved {product_code} to memory cache")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python jcrew_dynamic_fetcher.py <url>")
        sys.exit(1)
    
    fetcher = JCrewDynamicFetcher()
    result = fetcher.fetch_product(sys.argv[1])
    
    if result:
        import json
        print("\n📊 Dynamic Product Data:")
        print(json.dumps(result, indent=2))
    else:
        print("❌ Failed to fetch product")
