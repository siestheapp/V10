#!/usr/bin/env python3
"""
Smart Product Deduplicator - Prevents duplicate products when scraping at scale
Handles complex brand hierarchies intelligently
"""

import re
import json
from typing import Dict, Optional, List, Tuple
from difflib import SequenceMatcher
import psycopg2
from datetime import datetime
from abc import ABC, abstractmethod

class BrandAdapter(ABC):
    """Base class for brand-specific product logic"""
    
    @abstractmethod
    def is_master_code(self, code: str) -> bool:
        """Check if code is a master product code"""
        pass
    
    @abstractmethod
    def is_variant_code(self, code: str) -> bool:
        """Check if code is a variant/color code"""
        pass
    
    @abstractmethod
    def extract_all_codes(self, scraped_data: Dict) -> List[str]:
        """Extract all possible product codes from scraped data"""
        pass
    
    @abstractmethod
    def should_merge(self, existing_product: Dict, new_data: Dict) -> Tuple[bool, float]:
        """Determine if new data should merge with existing product
        Returns (should_merge, confidence_score)"""
        pass


class JCrewAdapter(BrandAdapter):
    """J.Crew specific product logic"""
    
    def is_master_code(self, code: str) -> bool:
        """J.Crew master codes: MP123, ME105, etc."""
        return bool(re.match(r'^M[EP]\d{3,4}$', code))
    
    def is_variant_code(self, code: str) -> bool:
        """J.Crew variant codes: BE996, BK273, etc."""
        return bool(re.match(r'^B[A-Z]\d{3,4}$', code))
    
    def extract_all_codes(self, scraped_data: Dict) -> List[str]:
        """Extract product codes from URL and content"""
        codes = []
        
        # Get code from scraped data
        if 'product_code' in scraped_data:
            codes.append(scraped_data['product_code'])
        
        # Try to extract from URL if present
        if 'url' in scraped_data:
            url_match = re.search(r'/([A-Z]{2}\d{3,4})(?:\?|$)', scraped_data['url'])
            if url_match:
                codes.append(url_match.group(1))
            
            # Also check colorProductCode parameter
            color_match = re.search(r'colorProductCode=([A-Z]{2}\d{3,4})', scraped_data['url'])
            if color_match:
                codes.append(color_match.group(1))
        
        return list(set(codes))  # Remove duplicates
    
    def should_merge(self, existing_product: Dict, new_data: Dict) -> Tuple[bool, float]:
        """Check if products should be merged"""
        confidence = 0.0
        
        # Check name similarity
        name_similarity = SequenceMatcher(
            None, 
            existing_product.get('base_name', '').lower(),
            new_data.get('name', '').lower()
        ).ratio()
        
        if name_similarity > 0.85:
            confidence = name_similarity
            
            # Boost confidence if prices are similar
            existing_price = existing_product.get('price')
            new_price = new_data.get('price')
            if existing_price and new_price:
                price_diff = abs(float(existing_price) - float(new_price))
                if price_diff < 10:  # Within $10
                    confidence = min(1.0, confidence + 0.1)
            
            return (True, confidence)
        
        return (False, 0.0)


class ReissAdapter(BrandAdapter):
    """Reiss specific product logic"""
    
    def is_master_code(self, code: str) -> bool:
        """Reiss uses style codes like T53709"""
        return bool(re.match(r'^[A-Z]\d{5}$', code))
    
    def is_variant_code(self, code: str) -> bool:
        """Reiss variants are usually the same as master"""
        return self.is_master_code(code)
    
    def extract_all_codes(self, scraped_data: Dict) -> List[str]:
        codes = []
        if 'product_code' in scraped_data:
            codes.append(scraped_data['product_code'])
        if 'style_code' in scraped_data:
            codes.append(scraped_data['style_code'])
        return list(set(codes))
    
    def should_merge(self, existing_product: Dict, new_data: Dict) -> Tuple[bool, float]:
        # Simpler logic for Reiss
        if existing_product.get('product_code') == new_data.get('product_code'):
            return (True, 1.0)
        
        name_similarity = SequenceMatcher(
            None,
            existing_product.get('base_name', '').lower(),
            new_data.get('name', '').lower()
        ).ratio()
        
        if name_similarity > 0.9:  # Higher threshold for Reiss
            return (True, name_similarity)
        
        return (False, 0.0)


class SmartProductDeduplicator:
    """Main deduplication engine"""
    
    def __init__(self, db_config):
        self.db_config = db_config
        self.adapters = {
            4: JCrewAdapter(),    # J.Crew
            10: ReissAdapter(),   # Reiss
            # Add more brands as needed
        }
        self.decisions_log = []
    
    def get_adapter(self, brand_id: int) -> BrandAdapter:
        """Get brand-specific adapter"""
        return self.adapters.get(brand_id)
    
    def process_product(self, scraped_data: Dict, brand_id: int) -> Dict:
        """
        Process a scraped product and determine action
        Returns: {
            'action': 'create_master' | 'add_variant' | 'update_existing' | 'skip',
            'master_id': existing product ID if applicable,
            'confidence': float,
            'reason': str
        }
        """
        adapter = self.get_adapter(brand_id)
        if not adapter:
            return {
                'action': 'create_master',
                'confidence': 0.5,
                'reason': 'No adapter for brand, using default'
            }
        
        # Extract all possible codes
        codes = adapter.extract_all_codes(scraped_data)
        
        # Check database for existing products
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor()
        
        try:
            # Look for exact code matches
            if codes:
                placeholders = ','.join(['%s'] * len(codes))
                cur.execute(f"""
                    SELECT id, product_code, base_name, pricing_data->>'price' as price
                    FROM product_master
                    WHERE brand_id = %s AND product_code IN ({placeholders})
                """, [brand_id] + codes)
                
                exact_match = cur.fetchone()
                if exact_match:
                    return {
                        'action': 'skip',
                        'master_id': exact_match[0],
                        'confidence': 1.0,
                        'reason': f'Exact code match: {exact_match[1]}'
                    }
            
            # Look for similar products by name
            cur.execute("""
                SELECT id, product_code, base_name, pricing_data->>'price' as price
                FROM product_master
                WHERE brand_id = %s
                AND base_name ILIKE %s
            """, (brand_id, f"%{scraped_data.get('name', '')[:30]}%"))
            
            similar_products = cur.fetchall()
            
            # Check each similar product
            best_match = None
            best_confidence = 0.0
            
            for product in similar_products:
                existing = {
                    'id': product[0],
                    'product_code': product[1],
                    'base_name': product[2],
                    'price': product[3]
                }
                
                should_merge, confidence = adapter.should_merge(existing, scraped_data)
                
                if should_merge and confidence > best_confidence:
                    best_match = existing
                    best_confidence = confidence
            
            if best_match:
                # Determine if it's a variant or duplicate
                product_code = scraped_data.get('product_code', '')
                
                if adapter.is_variant_code(product_code) and not adapter.is_master_code(product_code):
                    return {
                        'action': 'add_variant',
                        'master_id': best_match['id'],
                        'confidence': best_confidence,
                        'reason': f"Variant of {best_match['product_code']}: {best_match['base_name'][:30]}"
                    }
                else:
                    return {
                        'action': 'skip',
                        'master_id': best_match['id'],
                        'confidence': best_confidence,
                        'reason': f"Duplicate of {best_match['product_code']}"
                    }
            
            # No match found - create new product
            return {
                'action': 'create_master',
                'confidence': 0.9,
                'reason': 'No similar products found'
            }
            
        finally:
            conn.close()
    
    def log_decision(self, scraped_data: Dict, decision: Dict):
        """Log deduplication decisions for review"""
        self.decisions_log.append({
            'timestamp': datetime.now().isoformat(),
            'product': scraped_data.get('name', 'Unknown'),
            'code': scraped_data.get('product_code', 'Unknown'),
            'decision': decision
        })
    
    def save_log(self, filename: str = 'deduplication_log.json'):
        """Save decision log to file"""
        with open(filename, 'w') as f:
            json.dump(self.decisions_log, f, indent=2)
        print(f"💾 Saved deduplication log to {filename}")


def test_deduplicator():
    """Test the deduplicator with sample data"""
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from db_config import DB_CONFIG
    
    deduper = SmartProductDeduplicator(DB_CONFIG)
    
    # Test cases
    test_products = [
        {
            'name': 'Midweight denim workshirt',
            'product_code': 'BK273',
            'price': 98.0,
            'url': 'https://www.jcrew.com/m/mens/ME105?colorProductCode=BK273'
        },
        {
            'name': 'Short-sleeve indigo organic chambray shirt',
            'product_code': 'BE164',
            'price': 89.5,
            'url': 'https://www.jcrew.com/m/mens/MP600?colorProductCode=BE164'
        }
    ]
    
    print("🧪 Testing Smart Product Deduplicator")
    print("=" * 60)
    
    for product in test_products:
        print(f"\n📦 Product: {product['name']}")
        print(f"   Code: {product['product_code']}")
        
        decision = deduper.process_product(product, brand_id=4)  # J.Crew
        
        print(f"   Decision: {decision['action'].upper()}")
        print(f"   Confidence: {decision['confidence']:.2f}")
        print(f"   Reason: {decision['reason']}")
        
        deduper.log_decision(product, decision)
    
    deduper.save_log('test_deduplication.json')


if __name__ == "__main__":
    test_deduplicator()
