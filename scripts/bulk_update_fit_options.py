#!/usr/bin/env python3
"""
Bulk update fit options for J.Crew products based on product categories
"""

import sys
sys.path.append('/Users/seandavey/projects/V10')
import psycopg2
from db_config import DB_CONFIG

# Standard J.Crew fit options by category
JCREW_FIT_OPTIONS = {
    # Casual shirts (oxford, chambray, linen, etc.)
    'casual_shirts': ['Classic', 'Slim', 'Slim Untucked', 'Tall', 'Relaxed'],
    
    # Dress shirts
    'dress_shirts': ['Classic', 'Slim', 'Tall'],
    
    # T-shirts and polos
    't_shirts': ['Classic', 'Slim', 'Tall'],
    
    # Sweaters
    'sweaters': ['Classic', 'Slim', 'Tall'],
    
    # Default for most tops
    'default': ['Classic', 'Slim', 'Tall']
}

def categorize_product(name, code):
    """Determine product category from name"""
    name_lower = name.lower()
    
    # Dress shirts
    if any(term in name_lower for term in ['dress shirt', 'bowery', 'ludlow', 'tuxedo']):
        return 'dress_shirts'
    
    # Casual shirts
    elif any(term in name_lower for term in ['oxford', 'chambray', 'linen shirt', 'flannel', 
                                             'broken-in', 'secret wash', 'casual shirt']):
        return 'casual_shirts'
    
    # T-shirts and polos
    elif any(term in name_lower for term in ['t-shirt', 'tee', 'polo', 'henley']):
        return 't_shirts'
    
    # Sweaters
    elif any(term in name_lower for term in ['sweater', 'cardigan', 'pullover']):
        return 'sweaters'
    
    # Default
    else:
        return 'default'

def main():
    print("🔄 BULK UPDATE FIT OPTIONS FOR J.CREW PRODUCTS")
    print("="*60)
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # Get all products missing fit options
    cur.execute("""
        SELECT product_code, product_name
        FROM jcrew_product_cache 
        WHERE (fit_options IS NULL OR array_length(fit_options, 1) = 0)
        AND product_name IS NOT NULL
        ORDER BY product_name
    """)
    
    products = cur.fetchall()
    print(f"📋 Found {len(products)} products missing fit options")
    
    updates = {
        'casual_shirts': [],
        'dress_shirts': [],
        't_shirts': [],
        'sweaters': [],
        'default': []
    }
    
    # Categorize each product
    for code, name in products:
        category = categorize_product(name, code)
        updates[category].append((code, name))
    
    # Show categorization
    print("\n📊 Product Categorization:")
    for category, items in updates.items():
        if items:
            print(f"  {category}: {len(items)} products")
            for code, name in items[:2]:  # Show first 2 examples
                print(f"    • {code}: {name[:50]}")
            if len(items) > 2:
                print(f"    ... and {len(items) - 2} more")
    
    # Perform updates
    print("\n🔧 Updating database...")
    total_updated = 0
    
    for category, items in updates.items():
        if items:
            fit_options = JCREW_FIT_OPTIONS[category]
            codes = [item[0] for item in items]
            
            # Update all products in this category
            for code in codes:
                try:
                    cur.execute("""
                        UPDATE jcrew_product_cache 
                        SET fit_options = %s,
                            updated_at = NOW()
                        WHERE product_code = %s
                    """, (fit_options, code))
                    total_updated += cur.rowcount
                except Exception as e:
                    print(f"  ❌ Error updating {code}: {e}")
    
    conn.commit()
    print(f"✅ Updated {total_updated} products")
    
    # Check final status
    cur.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(*) FILTER (WHERE array_length(fit_options, 1) > 0) as has_fits
        FROM jcrew_product_cache
    """)
    
    total, has_fits = cur.fetchone()
    print(f"\n📈 Final Status:")
    print(f"  Total products: {total}")
    print(f"  Products with fits: {has_fits} ({has_fits/total*100:.1f}%)")
    
    # Show some examples of updated products
    print(f"\n✨ Sample Updated Products:")
    cur.execute("""
        SELECT product_code, product_name, fit_options
        FROM jcrew_product_cache 
        WHERE fit_options IS NOT NULL 
        AND array_length(fit_options, 1) > 0
        ORDER BY updated_at DESC
        LIMIT 5
    """)
    
    for code, name, fits in cur.fetchall():
        print(f"  {code}: {name[:40]}")
        print(f"    Fits: {', '.join(fits)}")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()

