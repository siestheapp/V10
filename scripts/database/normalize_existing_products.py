#!/usr/bin/env python3
"""
Apply category normalization to existing products in database
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from category_normalizer import CategoryNormalizer

def normalize_database_products(brand_filter=None):
    """Apply normalization to products in database"""
    
    # Connect to database
    conn = psycopg2.connect(
        database='postgres',
        user='postgres.lbilxlkchzpducggkrxx',
        password='efvTower12',
        host='aws-0-us-east-2.pooler.supabase.com',
        port='6543',
        cursor_factory=RealDictCursor,
        connect_timeout=10
    )
    cur = conn.cursor()
    
    # First, add columns if they don't exist
    print("📊 Adding normalization columns to database...")
    
    alter_queries = [
        "ALTER TABLE jcrew_product_cache ADD COLUMN IF NOT EXISTS brand_name VARCHAR(100) DEFAULT 'J.Crew';",
        "ALTER TABLE jcrew_product_cache ADD COLUMN IF NOT EXISTS standard_category VARCHAR(100);",
        "ALTER TABLE jcrew_product_cache ADD COLUMN IF NOT EXISTS standard_subcategory VARCHAR(100);",
        "ALTER TABLE jcrew_product_cache ADD COLUMN IF NOT EXISTS garment_type VARCHAR(100);",
        "ALTER TABLE jcrew_product_cache ADD COLUMN IF NOT EXISTS fabric_primary VARCHAR(100);",
        "ALTER TABLE jcrew_product_cache ADD COLUMN IF NOT EXISTS comparison_key VARCHAR(100);"
    ]
    
    for query in alter_queries:
        try:
            cur.execute(query)
            conn.commit()
        except Exception as e:
            print(f"Note: {e}")
            conn.rollback()
    
    # Get products to normalize
    where_clause = ""
    params = []
    if brand_filter:
        where_clause = "WHERE brand_name = %s"
        params = [brand_filter]
    
    cur.execute(f"""
        SELECT id, product_code, product_name, category, subcategory, 
               description, brand_name
        FROM jcrew_product_cache
        {where_clause}
    """, params)
    
    products = cur.fetchall()
    print(f"🔍 Found {len(products)} products to normalize")
    
    # Initialize normalizer
    normalizer = CategoryNormalizer()
    
    # Process each product
    updated = 0
    for product in products:
        # Normalize the product
        normalized = normalizer.normalize_product({
            'brand_name': product['brand_name'] or 'J.Crew',
            'product_name': product['product_name'],
            'category': product['category'],
            'subcategory': product['subcategory'],
            'description': product['description']
        })
        
        # Update database
        cur.execute("""
            UPDATE jcrew_product_cache SET
                standard_category = %s,
                standard_subcategory = %s,
                garment_type = %s,
                fabric_primary = %s,
                comparison_key = %s,
                updated_at = NOW()
            WHERE id = %s
        """, (
            normalized['standard_category'],
            normalized.get('standard_subcategory'),
            normalized['garment_type'],
            normalized['fabric_primary'],
            normalized['comparison_key'],
            product['id']
        ))
        
        updated += 1
        if updated % 10 == 0:
            print(f"  ✅ Normalized {updated} products...")
    
    conn.commit()
    print(f"\n✅ Successfully normalized {updated} products!")
    
    # Show summary
    cur.execute("""
        SELECT 
            standard_category,
            garment_type,
            COUNT(*) as count
        FROM jcrew_product_cache
        WHERE garment_type IS NOT NULL
        GROUP BY standard_category, garment_type
        ORDER BY standard_category, count DESC
    """)
    
    results = cur.fetchall()
    
    print("\n📊 Normalization Summary:")
    print("-" * 50)
    current_category = None
    for row in results:
        if row['standard_category'] != current_category:
            current_category = row['standard_category']
            print(f"\n{current_category}:")
        print(f"  • {row['garment_type']}: {row['count']} products")
    
    # Show products that couldn't be normalized
    cur.execute("""
        SELECT product_code, product_name, category, subcategory
        FROM jcrew_product_cache
        WHERE garment_type IS NULL
        LIMIT 10
    """)
    
    unmatched = cur.fetchall()
    if unmatched:
        print(f"\n⚠️ {len(unmatched)} products couldn't be normalized:")
        for product in unmatched[:5]:
            print(f"  - {product['product_code']}: {product['product_name'][:50]}...")
    
    conn.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Normalize product categories')
    parser.add_argument('--brand', help='Filter by brand name')
    args = parser.parse_args()
    
    normalize_database_products(args.brand)

