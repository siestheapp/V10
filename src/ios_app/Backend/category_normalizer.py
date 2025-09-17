"""
Category Normalizer - Maps brand-specific categories to normalized ones
Enables cross-brand search and filtering
"""

class CategoryNormalizer:
    """Maps brand-specific categories to normalized categories"""
    
    # Normalized categories for cross-brand search
    NORMALIZED_CATEGORIES = {
        'FORMAL_SHIRTS': 'Formal Shirts',
        'CASUAL_SHIRTS': 'Casual Shirts', 
        'T_SHIRTS': 'T-Shirts',
        'POLOS': 'Polos',
        'SWEATERS': 'Sweaters',
        'PANTS': 'Pants',
        'JEANS': 'Jeans',
        'SHORTS': 'Shorts',
        'OUTERWEAR': 'Outerwear'
    }
    
    # Brand-specific mappings to normalized categories
    BRAND_MAPPINGS = {
        'J.Crew': {
            # J.Crew categories -> Normalized
            'Dress Shirts': 'FORMAL_SHIRTS',
            'Casual Shirts': 'CASUAL_SHIRTS',
            'Secret Wash': 'CASUAL_SHIRTS',
            'Oxford': 'CASUAL_SHIRTS',
            'Linen': 'CASUAL_SHIRTS',
            'Bowery': 'FORMAL_SHIRTS',
            'Ludlow Premium': 'FORMAL_SHIRTS',
            'T-Shirts': 'T_SHIRTS',
            'Polos': 'POLOS',
            'Sweaters': 'SWEATERS',
            'Chinos': 'PANTS',
            'Jeans': 'JEANS'
        },
        'Banana Republic': {
            # Banana Republic categories -> Normalized
            'Dress Shirts': 'FORMAL_SHIRTS',
            'Casual Shirts': 'CASUAL_SHIRTS',
            'Grant Slim': 'FORMAL_SHIRTS',
            'Camden Standard': 'FORMAL_SHIRTS',
            'Luxury Touch': 'POLOS',
            'Tees': 'T_SHIRTS',
            'Sweaters': 'SWEATERS',
            'Chinos': 'PANTS',
            'Jeans': 'JEANS',
            'Rapid Movement': 'PANTS'
        },
        'Theory': {
            # Theory categories -> Normalized
            'Wovens': 'FORMAL_SHIRTS',
            'Shirts': 'FORMAL_SHIRTS',
            'Essential': 'FORMAL_SHIRTS',
            'Precision': 'FORMAL_SHIRTS',
            'Tees': 'T_SHIRTS',
            'Knits': 'SWEATERS',
            'Pants': 'PANTS',
            'Trousers': 'PANTS'
        },
        'Reiss': {
            # Reiss categories -> Normalized
            'Oxford Shirts': 'CASUAL_SHIRTS',
            'Formal Shirts': 'FORMAL_SHIRTS',
            'Casual Shirts': 'CASUAL_SHIRTS',
            'Polos': 'POLOS',
            'T-Shirts': 'T_SHIRTS',
            'Knitwear': 'SWEATERS',
            'Trousers': 'PANTS',
            'Jeans': 'JEANS',
            'Shorts': 'SHORTS'
        }
    }
    
    # Fit normalization across brands
    FIT_MAPPINGS = {
        'J.Crew': {
            'Classic': 'regular',
            'Slim': 'slim',
            'Slim Untucked': 'slim_untucked',
            'Tall': 'tall',
            'Relaxed': 'relaxed'
        },
        'Banana Republic': {
            'Grant Slim-Fit': 'slim',
            'Camden Standard': 'regular',
            'Untucked': 'untucked',
            'Standard': 'regular',
            'Slim': 'slim'
        },
        'Theory': {
            'Irving': 'slim',
            'Sylvain': 'regular',
            'Straight': 'regular',
            'Slim': 'slim'
        },
        'Reiss': {
            'Slim': 'slim',
            'Regular': 'regular',
            'Tailored': 'slim',
            'Relaxed': 'relaxed'
        }
    }
    
    @classmethod
    def normalize_category(cls, brand: str, category: str) -> str:
        """
        Convert brand-specific category to normalized category
        
        Args:
            brand: Brand name (e.g., 'J.Crew')
            category: Brand-specific category (e.g., 'Bowery')
            
        Returns:
            Normalized category (e.g., 'Formal Shirts')
        """
        if brand in cls.BRAND_MAPPINGS:
            mapping = cls.BRAND_MAPPINGS[brand]
            if category in mapping:
                normalized_key = mapping[category]
                return cls.NORMALIZED_CATEGORIES.get(normalized_key, category)
        
        # Fallback: return original category
        return category
    
    @classmethod
    def normalize_fit(cls, brand: str, fit: str) -> str:
        """
        Convert brand-specific fit to normalized fit
        
        Args:
            brand: Brand name
            fit: Brand-specific fit name
            
        Returns:
            Normalized fit name
        """
        if brand in cls.FIT_MAPPINGS:
            mapping = cls.FIT_MAPPINGS[brand]
            return mapping.get(fit, fit.lower())
        
        return fit.lower()
    
    @classmethod
    def get_brands_for_category(cls, normalized_category: str) -> dict:
        """
        Get all brand-specific categories that map to a normalized category
        
        Args:
            normalized_category: e.g., 'FORMAL_SHIRTS'
            
        Returns:
            Dict of {brand: [brand_categories]}
        """
        result = {}
        
        for brand, mappings in cls.BRAND_MAPPINGS.items():
            brand_categories = [
                cat for cat, norm in mappings.items() 
                if norm == normalized_category
            ]
            if brand_categories:
                result[brand] = brand_categories
        
        return result
    
    @classmethod
    def search_across_brands(cls, normalized_category: str, db_connection):
        """
        Search for products across all brands in a normalized category
        
        Args:
            normalized_category: e.g., 'FORMAL_SHIRTS'
            db_connection: Database connection
            
        Returns:
            List of products from all brands in that category
        """
        import psycopg2.extras
        
        brands_and_categories = cls.get_brands_for_category(normalized_category)
        
        if not brands_and_categories:
            return []
        
        cur = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Build query for all brand/category combinations
        conditions = []
        params = []
        
        for brand, categories in brands_and_categories.items():
            for category in categories:
                conditions.append("(b.name = %s AND pm.category = %s)")
                params.extend([brand, category])
        
        query = f"""
            SELECT 
                pm.id,
                pm.product_code,
                pm.base_name,
                b.name as brand,
                pm.category as original_category,
                %s as normalized_category
            FROM product_master pm
            JOIN brands b ON pm.brand_id = b.id
            WHERE {' OR '.join(conditions)}
            ORDER BY b.name, pm.base_name
        """
        
        cur.execute(query, [normalized_category] + params)
        results = cur.fetchall()
        cur.close()
        
        return results


# Example usage:
if __name__ == "__main__":
    # Example: User searches for "dress shirts"
    print("User searches for: 'dress shirts'")
    print("-" * 40)
    
    # This would return products from:
    # - J.Crew: Bowery, Ludlow Premium
    # - Banana Republic: Grant Slim, Camden Standard  
    # - Theory: Wovens, Essential, Precision
    
    brands = CategoryNormalizer.get_brands_for_category('FORMAL_SHIRTS')
    for brand, categories in brands.items():
        print(f"{brand}: {', '.join(categories)}")
    
    print("\n" + "=" * 40)
    print("Normalizing specific categories:")
    print("-" * 40)
    
    # J.Crew Bowery -> Formal Shirts
    print(f"J.Crew 'Bowery' -> {CategoryNormalizer.normalize_category('J.Crew', 'Bowery')}")
    
    # Banana Republic Grant Slim -> Formal Shirts
    print(f"BR 'Grant Slim' -> {CategoryNormalizer.normalize_category('Banana Republic', 'Grant Slim')}")
    
    # Theory Wovens -> Formal Shirts
    print(f"Theory 'Wovens' -> {CategoryNormalizer.normalize_category('Theory', 'Wovens')}")
