#!/usr/bin/env python3
"""
Category Normalizer for Multi-Brand Product Comparison
Handles different brand terminologies and maps them to standard categories
"""

import re
from typing import Dict, Tuple, Optional

class CategoryNormalizer:
    """Normalize product categories across different brands"""
    
    def __init__(self):
        # Define garment type patterns and keywords
        self.garment_patterns = {
            'dress_shirt': {
                'keywords': ['dress shirt', 'bowery', 'ludlow', 'thomas mason', 'spread collar', 'french cuff', 'non-iron'],
                'exclude': ['casual', 't-shirt', 'polo'],
                'fabric': 'various',
                'formality': 'formal'
            },
            'oxford_shirt': {
                'keywords': ['oxford', 'button-down', 'button down', 'bd shirt', 'broken-in'],
                'exclude': ['shorts', 'pants', 'jacket'],
                'fabric': 'oxford_cotton',
                'formality': 'casual'
            },
            'poplin_shirt': {
                'keywords': ['poplin', 'secret wash'],
                'exclude': ['t-shirt', 'polo'],
                'fabric': 'cotton_poplin',
                'formality': 'business_casual'
            },
            'linen_shirt': {
                'keywords': ['linen', 'irish linen', 'baird mcnutt'],
                'exclude': ['pants', 'shorts', 'blend'],
                'fabric': 'linen'
            },
            'flannel_shirt': {
                'keywords': ['flannel', 'brushed cotton', 'plaid shirt'],
                'exclude': ['pajama', 'sleepwear'],
                'fabric': 'flannel'
            },
            'chambray_shirt': {
                'keywords': ['chambray', 'denim shirt', 'workshirt'],
                'exclude': ['jeans', 'jacket'],
                'fabric': 'chambray'
            },
            'tshirt': {
                'keywords': ['t-shirt', 'tee', 'crew neck', 'v-neck'],
                'exclude': ['polo', 'button'],
                'fabric': 'cotton_jersey'
            },
            'polo_shirt': {
                'keywords': ['polo', 'golf shirt', 'tennis shirt'],
                'exclude': ['t-shirt'],
                'fabric': 'pique_cotton'
            }
        }
        
        # Brand-specific category mappings
        self.brand_mappings = {
            'jcrew': {
                'casual shirts': 'casual_shirts',
                'dress shirts': 'dress_shirts',
                't-shirts & polos': 'knitwear',
                'sweaters': 'knitwear',
                'pants & chinos': 'bottoms',
                'jeans': 'bottoms'
            },
            'banana_republic': {
                'tops': 'shirts',
                'shirts': 'shirts',
                'polos & tees': 'knitwear',
                'sweaters': 'knitwear',
                'pants': 'bottoms',
                'denim': 'bottoms'
            },
            'uniqlo': {
                'men shirts': 'shirts',
                'casual shirts': 'shirts',
                't-shirts': 'knitwear',
                'knitwear': 'knitwear',
                'bottoms': 'bottoms'
            },
            'gap': {
                'shirts': 'shirts',
                'tees & polos': 'knitwear',
                'pants & shorts': 'bottoms'
            }
        }
    
    def detect_garment_type(self, product_name: str, category: str = None, 
                           subcategory: str = None) -> Optional[str]:
        """
        Detect garment type from product name and categories
        
        Args:
            product_name: Product name/title
            category: Brand's category
            subcategory: Brand's subcategory
            
        Returns:
            Detected garment type key or None
        """
        # Combine all text for analysis
        text = f"{product_name} {category or ''} {subcategory or ''}".lower()
        
        # Check each garment type pattern
        for garment_type, pattern in self.garment_patterns.items():
            # Check if any keyword matches
            has_keyword = any(keyword in text for keyword in pattern['keywords'])
            
            # Check if any exclude word is present
            has_exclude = any(exclude in text for exclude in pattern['exclude'])
            
            if has_keyword and not has_exclude:
                return garment_type
        
        return None
    
    def normalize_category(self, brand: str, category: str) -> str:
        """
        Normalize brand-specific category to standard category
        
        Args:
            brand: Brand name
            category: Brand's category name
            
        Returns:
            Normalized category
        """
        brand_lower = brand.lower().replace(' ', '_')
        category_lower = category.lower()
        
        # Check if we have brand-specific mappings
        if brand_lower in self.brand_mappings:
            mappings = self.brand_mappings[brand_lower]
            for brand_cat, standard_cat in mappings.items():
                if brand_cat in category_lower:
                    return standard_cat.title()
        
        # Default mappings for common terms
        if any(term in category_lower for term in ['shirt', 'top', 'blouse']):
            return 'Shirts'
        elif any(term in category_lower for term in ['pant', 'trouser', 'jean', 'chino']):
            return 'Bottoms'
        elif any(term in category_lower for term in ['knit', 'sweater', 'cardigan']):
            return 'Knitwear'
        elif any(term in category_lower for term in ['jacket', 'coat', 'blazer']):
            return 'Outerwear'
        
        return category.title()
    
    def extract_fabric(self, product_name: str, description: str = None) -> Optional[str]:
        """
        Extract primary fabric from product information
        
        Args:
            product_name: Product name
            description: Product description
            
        Returns:
            Primary fabric type
        """
        text = f"{product_name} {description or ''}".lower()
        
        fabric_keywords = {
            'oxford_cotton': ['oxford', 'oxford cloth'],
            'poplin': ['poplin', 'cotton poplin'],
            'linen': ['linen', '100% linen', 'irish linen'],
            'flannel': ['flannel', 'brushed cotton'],
            'chambray': ['chambray'],
            'denim': ['denim', 'jean'],
            'cotton': ['100% cotton', 'cotton'],
            'wool': ['wool', 'merino', 'cashmere'],
            'synthetic': ['polyester', 'nylon', 'spandex', 'elastane']
        }
        
        for fabric, keywords in fabric_keywords.items():
            if any(keyword in text for keyword in keywords):
                return fabric
        
        return None
    
    def create_comparison_key(self, garment_type: str, fabric: str = None) -> str:
        """
        Create a comparison key for cross-brand matching
        
        Args:
            garment_type: Type of garment
            fabric: Primary fabric (optional)
            
        Returns:
            Comparison key string
        """
        if fabric:
            return f"{garment_type}_{fabric}".lower()
        return garment_type.lower()
    
    def normalize_product(self, product: Dict) -> Dict:
        """
        Normalize a product's categories for cross-brand comparison
        
        Args:
            product: Product dictionary with brand, name, category, etc.
            
        Returns:
            Product dict with added normalized fields
        """
        # Detect garment type
        garment_type = self.detect_garment_type(
            product.get('product_name', ''),
            product.get('category'),
            product.get('subcategory')
        )
        
        # Normalize category
        standard_category = self.normalize_category(
            product.get('brand_name', 'unknown'),
            product.get('category', '')
        )
        
        # Extract fabric
        fabric = self.extract_fabric(
            product.get('product_name', ''),
            product.get('description')
        )
        
        # Create comparison key
        comparison_key = self.create_comparison_key(garment_type or 'unknown', fabric)
        
        # Add normalized fields
        product['standard_category'] = standard_category
        product['garment_type'] = garment_type
        product['fabric_primary'] = fabric
        product['comparison_key'] = comparison_key
        
        return product


# Example usage
if __name__ == "__main__":
    normalizer = CategoryNormalizer()
    
    # Test with different brand products
    test_products = [
        {
            'brand_name': 'J.Crew',
            'product_name': 'Broken-in organic cotton oxford shirt',
            'category': 'Casual Shirts',
            'subcategory': 'Broken-In Oxford'
        },
        {
            'brand_name': 'Banana Republic',
            'product_name': 'Grant Slim-Fit Oxford Shirt',
            'category': 'Tops',
            'subcategory': None
        },
        {
            'brand_name': 'Uniqlo',
            'product_name': 'Men Oxford Slim Fit Long Sleeve Shirt',
            'category': 'Men Shirts',
            'subcategory': 'Oxford'
        }
    ]
    
    print("Product Normalization Test:")
    print("=" * 60)
    
    for product in test_products:
        normalized = normalizer.normalize_product(product)
        print(f"\nBrand: {normalized['brand_name']}")
        print(f"Product: {normalized['product_name']}")
        print(f"Original Category: {normalized['category']} > {normalized.get('subcategory')}")
        print(f"Standard Category: {normalized['standard_category']}")
        print(f"Garment Type: {normalized['garment_type']}")
        print(f"Fabric: {normalized['fabric_primary']}")
        print(f"Comparison Key: {normalized['comparison_key']}")
