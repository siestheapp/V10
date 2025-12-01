"""
J.Crew Comprehensive Product Fetcher
=====================================
This fetcher returns ALL fit options for a product family, regardless of which
fit URL was provided. This allows the app to toggle between fits without
requiring the user to go back to Safari.

For example, if user enters BE996 with fit=Classic, we return:
- All fits: ['Classic', 'Slim', 'Slim Untucked', 'Tall', 'Relaxed']
- Current selection: 'Classic'
- Product can then toggle between fits in-app
"""

import requests
from bs4 import BeautifulSoup
import re
from typing import Optional, Dict, List
import psycopg2
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import json

# Database configuration
DB_CONFIG = {
    'database': 'postgres',
    'user': 'fs_core_rw',
    'password': 'CHANGE_ME',
    'host': 'aws-1-us-east-1.pooler.supabase.com',
    'port': '5432'
}

class JCrewComprehensiveFetcher:
    """
    Fetches comprehensive product data including ALL fit variations
    for the product family, not just the currently selected fit.
    """
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def fetch_product(self, product_url: str) -> Optional[Dict]:
        """
        Fetch comprehensive product data including ALL fit options
        """
        product_code = self._extract_product_code(product_url)
        current_fit = self._extract_current_fit(product_url)
        
        print(f"🔍 Fetching comprehensive data for {product_code}")
        print(f"   Current fit from URL: {current_fit or 'Classic (default)'}")
        
        # First check if we have this product family in cache
        cached_data = self._get_product_family_from_cache(product_code)
        if cached_data:
            print(f"✅ Found {product_code} family in cache with {len(cached_data.get('all_fit_options', []))} fit options")
            # Update current selection based on URL
            cached_data['current_fit'] = current_fit or 'Classic'
            cached_data['current_url'] = product_url
            return cached_data
        
        # Scrape comprehensive data from website
        product_data = self._scrape_comprehensive_data(product_url)
        
        if product_data:
            # Save to cache for future use
            self._save_comprehensive_to_cache(product_code, product_data)
            
        return product_data
    
    def _extract_product_code(self, url: str) -> str:
        """Extract product code from URL"""
        patterns = [
            r'/([A-Z]{2}\d{3,4})(?:\?|$|/)',
            r'[?&]productCode=([A-Z]{2}\d{3,4})',
            r'/p/([A-Z]{2}\d{3,4})',
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
            # Normalize fit name
            if fit.lower() == 'slim untucked':
                return 'Slim Untucked'
            return fit.title()
        
        return None  # Classic is default when no fit parameter
    
    def _scrape_comprehensive_data(self, product_url: str) -> Optional[Dict]:
        """
        Scrape ALL fit options and data for the product family
        """
        try:
            # Get the base URL without fit parameter to find all variations
            base_url = self._get_base_url(product_url)
            
            print(f"🔍 Scraping comprehensive data from: {base_url}")
            response = requests.get(base_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract all available fit options
            all_fit_options = self._extract_all_fit_options(soup, base_url)
            
            # Get basic product info
            product_name = self._extract_name(soup)
            product_code = self._extract_product_code(product_url)
            
            # For each fit option, get its specific data
            fit_specific_data = {}
            for fit in all_fit_options:
                fit_url = self._build_fit_url(base_url, fit)
                fit_data = self._get_fit_specific_data(fit_url, fit)
                if fit_data:
                    fit_specific_data[fit] = fit_data
            
            # Get current fit from URL
            current_fit = self._extract_current_fit(product_url) or 'Classic'
            
            # Build comprehensive response
            return {
                'product_code': product_code,
                'product_name': product_name or "J.Crew Product",  # Ensure never null
                'base_url': base_url,
                'current_url': product_url,
                'current_fit': current_fit,
                'all_fit_options': all_fit_options,  # ALL available fits
                'fit_specific_data': fit_specific_data,  # Data for each fit
                'current_fit_data': fit_specific_data.get(current_fit, {}),
                
                # Current selection data (for backward compatibility)
                'colors_available': fit_specific_data.get(current_fit, {}).get('colors', []),
                'product_image': fit_specific_data.get(current_fit, {}).get('image', '') or "",  # Never null
                'sizes_available': fit_specific_data.get(current_fit, {}).get('sizes', ['XS', 'S', 'M', 'L', 'XL', 'XXL']),
                
                # This is the key field - ALL fit options available
                'fit_options': all_fit_options
            }
            
        except Exception as e:
            print(f"❌ Error scraping comprehensive data: {e}")
            return None
    
    def _extract_all_fit_options(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """
        Extract ALL fit options available for this product family.
        This looks for the fit selector/navigation on the page.
        """
        all_fits = []
        
        # Strategy 1: Look for fit navigation links/buttons
        # These appear as Classic, Slim, Tall, etc. options on the page
        fit_elements = soup.find_all(['a', 'button'], 
                                     text=re.compile(r'(Classic|Slim|Tall|Relaxed|Untucked)', re.I))
        
        for element in fit_elements:
            text = element.get_text(strip=True)
            if text and any(fit in text for fit in ['Classic', 'Slim', 'Tall', 'Relaxed', 'Untucked']):
                # Handle multi-word fits
                if 'Slim' in text and 'Untucked' in text:
                    if 'Slim Untucked' not in all_fits:
                        all_fits.append('Slim Untucked')
                elif text in ['Classic', 'Slim', 'Tall', 'Relaxed']:
                    if text not in all_fits:
                        all_fits.append(text)
        
        # Strategy 2: Look in JavaScript data for all product variations
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                # Look for fit variations in JS
                matches = re.findall(r'"fit":\s*"([^"]+)"', script.string)
                for fit in matches:
                    fit_clean = fit.replace('%20', ' ').strip()
                    if fit_clean and fit_clean not in all_fits:
                        if fit_clean.lower() == 'slim untucked':
                            fit_clean = 'Slim Untucked'
                        else:
                            fit_clean = fit_clean.title()
                        if fit_clean not in all_fits:
                            all_fits.append(fit_clean)
        
        # Strategy 3: Check URLs in the page for fit parameters
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link['href']
            if 'fit=' in href:
                fit_match = re.search(r'fit=([^&]+)', href)
                if fit_match:
                    fit = fit_match.group(1).replace('%20', ' ').replace('+', ' ')
                    if fit.lower() == 'slim untucked':
                        fit = 'Slim Untucked'
                    else:
                        fit = fit.title()
                    if fit not in all_fits and fit in ['Classic', 'Slim', 'Tall', 'Relaxed', 'Slim Untucked']:
                        all_fits.append(fit)
        
        # If no fits found, check if this is a single-fit product
        if not all_fits:
            print("   No fit variations found - likely a single-fit product")
            return []
        
        # Sort fits in a logical order
        fit_order = ['Classic', 'Slim', 'Slim Untucked', 'Tall', 'Relaxed']
        all_fits.sort(key=lambda x: fit_order.index(x) if x in fit_order else 999)
        
        print(f"   ✅ Found {len(all_fits)} fit options: {all_fits}")
        return all_fits
    
    def _get_base_url(self, url: str) -> str:
        """Get base URL without fit parameter"""
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        # Remove fit parameter
        params.pop('fit', None)
        
        # Rebuild URL
        new_query = urlencode(params, doseq=True)
        return urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))
    
    def _build_fit_url(self, base_url: str, fit: str) -> str:
        """Build URL for specific fit"""
        if fit == 'Classic':
            # Classic is default, no fit parameter needed
            return base_url
        
        parsed = urlparse(base_url)
        params = parse_qs(parsed.query)
        
        # Add fit parameter
        params['fit'] = [fit]
        
        new_query = urlencode(params, doseq=True)
        return urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))
    
    def _get_fit_specific_data(self, fit_url: str, fit_name: str) -> Dict:
        """
        Get fit-specific data (colors, product name, image)
        """
        try:
            print(f"   📊 Getting data for {fit_name} fit...")
            response = requests.get(fit_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract fit-specific product name
            product_name = self._extract_name(soup)
            
            # Extract available colors for this fit
            colors = self._extract_colors(soup)
            
            # Extract main image
            image = self._extract_image(soup)
            
            # Extract sizes (usually same for all fits)
            sizes = self._extract_sizes(soup)
            
            return {
                'fit_name': fit_name,
                'product_name': product_name,
                'colors': colors,
                'image': image,
                'sizes': sizes or ['XS', 'S', 'M', 'L', 'XL', 'XXL'],
                'url': fit_url
            }
            
        except Exception as e:
            print(f"   ⚠️ Could not get data for {fit_name}: {e}")
            return {}
    
    def _extract_name(self, soup: BeautifulSoup) -> str:
        """Extract product name"""
        selectors = [
            'h1[class*="product-name"]',
            'h1[data-qaid*="productName"]',
            'h1[itemprop="name"]',
            'h1',
            '.product-header h1'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        return "Unknown Product"
    
    def _extract_colors(self, soup: BeautifulSoup) -> List[str]:
        """Extract available colors"""
        colors = []
        
        # Look for color swatches
        color_elements = soup.find_all(['button', 'input'], 
                                       attrs={'aria-label': re.compile(r'color', re.I)})
        
        for element in color_elements:
            aria_label = element.get('aria-label', '')
            # Extract color name from aria-label
            color_match = re.match(r'^([^$]+)', aria_label.strip())
            if color_match:
                color_name = color_match.group(1).strip()
                if color_name and color_name not in colors:
                    colors.append(color_name)
        
        return colors
    
    def _extract_image(self, soup: BeautifulSoup) -> str:
        """Extract main product image"""
        selectors = [
            'img[class*="mainImg"]',
            'img[itemprop="image"]',
            '.product-image img',
            'img[src*="/s7-img-facade/"]'
        ]
        
        for selector in selectors:
            img = soup.select_one(selector)
            if img and img.get('src'):
                src = img['src']
                if src.startswith('//'):
                    src = 'https:' + src
                elif not src.startswith('http'):
                    src = 'https://www.jcrew.com' + src
                return src
        
        return ""
    
    def _extract_sizes(self, soup: BeautifulSoup) -> List[str]:
        """Extract available sizes"""
        sizes = []
        
        size_elements = soup.find_all(['button', 'input'], 
                                      text=re.compile(r'^(XS|S|M|L|XL|XXL|XXXL)$'))
        
        for element in size_elements:
            size = element.get_text(strip=True)
            if size and size not in sizes:
                sizes.append(size)
        
        # Sort sizes logically
        size_order = ['XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL']
        sizes.sort(key=lambda x: size_order.index(x) if x in size_order else 999)
        
        return sizes
    
    def _get_product_family_from_cache(self, product_code: str) -> Optional[Dict]:
        """Get product family data from cache"""
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        try:
            # Get the product with its fit options
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
                return {
                    'product_name': row[0] or "J.Crew Product",
                    'product_code': row[1],
                    'product_image': row[2] or "",  # Never null
                    'category': row[3],
                    'subcategory': row[4],
                    'sizes_available': row[5] or ['XS', 'S', 'M', 'L', 'XL', 'XXL'],
                    'colors_available': row[6] or [],
                    'material': row[7],
                    'fit_type': row[8],
                    'all_fit_options': row[9] or [],  # This is the key field
                    'fit_options': row[9] or [],  # Duplicate for compatibility
                    'price': float(row[10]) if row[10] else None
                }
        
        except Exception as e:
            print(f"Cache lookup error: {e}")
        finally:
            cur.close()
            conn.close()
        
        return None
    
    def _save_comprehensive_to_cache(self, product_code: str, data: Dict):
        """Save comprehensive product data to cache"""
        # Implementation would save the comprehensive data
        # For now, just log
        print(f"📦 Would save comprehensive data for {product_code} with {len(data.get('all_fit_options', []))} fit options")


# Test the comprehensive fetcher
if __name__ == "__main__":
    fetcher = JCrewComprehensiveFetcher()
    
    # Test with BE996 Classic URL
    test_url = "https://www.jcrew.com/p/mens/categories/clothing/shirts/broken-in-oxford/broken-in-organic-cotton-oxford-shirt/BE996?fit=Classic"
    
    print("=" * 70)
    print("Testing Comprehensive Fit Detection")
    print("=" * 70)
    
    result = fetcher.fetch_product(test_url)
    
    if result:
        print(f"\n✅ Product: {result['product_name']}")
        print(f"📦 Product Code: {result['product_code']}")
        print(f"🎯 Current Fit: {result['current_fit']}")
        print(f"👔 ALL Available Fits: {result['all_fit_options']}")
        print(f"\n🎨 Colors for each fit:")
        for fit, data in result.get('fit_specific_data', {}).items():
            print(f"   {fit}: {len(data.get('colors', []))} colors")
