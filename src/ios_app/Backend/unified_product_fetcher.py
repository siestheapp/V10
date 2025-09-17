"""
Unified Product Fetcher - Simple database-only approach
No scraping, just checks product_master table for all brands
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, Dict
from urllib.parse import urlparse
import re
import sys
import os

# Add parent directory to path to import db_config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from db_config import DB_CONFIG

class UnifiedProductFetcher:
    """Simple fetcher that only checks the database for pre-loaded products"""
    
    def fetch_product(self, product_url: str) -> Optional[Dict]:
        """
        Fetch product from database based on URL
        Returns product data if found, None if not
        """
        # Extract product code from URL
        product_code = self._extract_product_code(product_url)
        brand_info = self._extract_brand_from_url(product_url)
        
        if not product_code or not brand_info:
            print(f"❌ Could not extract product code or brand from URL: {product_url}")
            return None
        
        print(f"🔍 Looking for {brand_info['brand_name']} product {product_code} in database...")
        
        try:
            conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
            cur = conn.cursor()
            
            # Query product_master table
            cur.execute("""
                SELECT 
                    pm.id,
                    pm.product_code,
                    pm.base_name as product_name,
                    b.name as brand_name,
                    pm.materials,
                    pm.care_instructions,
                    pm.description_texts,
                    pm.fit_information,
                    c.name as category,
                    sc.name as subcategory
                FROM product_master pm
                JOIN brands b ON pm.brand_id = b.id
                LEFT JOIN categories c ON pm.category_id = c.id
                LEFT JOIN subcategories sc ON pm.subcategory_id = sc.id
                WHERE pm.product_code = %s
                AND b.id = %s
            """, (product_code, brand_info['brand_id']))
            
            product = cur.fetchone()
            
            if product:
                print(f"✅ Found product: {product['product_name']}")
                
                # Get variants if they exist
                cur.execute("""
                    SELECT 
                        id as variant_id,
                        color_name,
                        fit_option,
                        current_price,
                        sizes_available,
                        in_stock
                    FROM product_variants
                    WHERE product_master_id = %s
                """, (product['id'],))
                
                variants = cur.fetchall()
                
                # Format response
                result = {
                    'product_master_id': product['id'],  # Added for database linking
                    'product_variant_id': variants[0]['variant_id'] if variants else None,  # First variant ID
                    'product_code': product['product_code'],
                    'product_name': product['product_name'],
                    'brand': product['brand_name'],
                    'category': product['category'],
                    'subcategory': product['subcategory'],
                    'materials': product['materials'],
                    'care_instructions': product['care_instructions'],
                    'description': product['description_texts'],
                    'fit_information': product['fit_information'],
                    'variants': variants if variants else [],
                    'product_url': product_url
                }
                
                cur.close()
                conn.close()
                return result
            else:
                print(f"❌ Product not found in database")
                cur.close()
                conn.close()
                return None
                
        except Exception as e:
            print(f"❌ Database error: {str(e)}")
            return None
    
    def _extract_product_code(self, url: str) -> Optional[str]:
        """Extract product code from various brand URL formats"""
        patterns = [
            # J.Crew patterns
            r'/([A-Z]{2}\d{3,4})(?:\?|$|/)',  # /CM389? or /CM389/
            r'[?&]productCode=([A-Z]{2}\d{3,4})',  # ?productCode=CM389
            r'/p/([A-Z]{2}\d{3,4})',  # /p/CM389
            r'/([A-Z]{2}\d{3,4})/',  # /ME625/
            
            # Banana Republic patterns (add more as needed)
            r'/([0-9]{6,})',  # Numeric product codes
            r'pid=([0-9]{6,})',  # pid parameter
            
            # Theory patterns (add more as needed)
            r'/([A-Z0-9]{5,10})\.html',  # Theory uses .html endings
            
            # Reiss patterns
            r'/([A-Z]\d{2,3}-?\d{3,4})',  # D43750 or D43-750
            r'#([A-Z]\d{2,3}-?\d{3,4})',  # After hash in URL
            r'/style/[^/]+/([^/#]+)',  # /style/st378878/d43750
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                return match.group(1).upper()
        
        return None
    
    def _extract_brand_from_url(self, url: str) -> Optional[Dict]:
        """Extract brand information from URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Brand detection
            if "jcrew.com" in domain:
                return {"brand_name": "J.Crew", "brand_id": 4}
            elif "bananarepublic" in domain:
                return {"brand_name": "Banana Republic", "brand_id": 5}
            elif "theory.com" in domain:
                return {"brand_name": "Theory", "brand_id": 9}
            elif "uniqlo.com" in domain:
                return {"brand_name": "Uniqlo", "brand_id": 1}
            elif "patagonia.com" in domain:
                return {"brand_name": "Patagonia", "brand_id": 2}
            elif "lululemon.com" in domain:
                return {"brand_name": "Lululemon", "brand_id": 1}
            elif "reiss.com" in domain:
                return {"brand_name": "Reiss", "brand_id": 10}
            
            return None
        except Exception as e:
            print(f"Error extracting brand: {str(e)}")
            return None

# For backwards compatibility
def fetch_product_simple(product_url: str) -> Optional[Dict]:
    """Simple function interface for fetching products"""
    fetcher = UnifiedProductFetcher()
    return fetcher.fetch_product(product_url)
