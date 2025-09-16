#!/usr/bin/env python3
"""
Import ONE J.Crew product at a time - no hanging, no timeouts
"""

import json
import psycopg2
from psycopg2.extras import RealDictCursor

def import_single_product():
    """Import just the first product to test"""
    
    # Load the JSON data
    with open('jcrew_broken_in_oxford_complete_20250915_120745.json', 'r') as f:
        products = json.load(f)
    
    # Get the first product
    product = products[0]
    print(f"Processing: {product['code']} - {product['name']}")
    
    # Connect to database with short timeout
    try:
        conn = psycopg2.connect(
            database='postgres',
            user='postgres.lbilxlkchzpducggkrxx',
            password='efvTower12',
            host='aws-0-us-east-2.pooler.supabase.com',
            port='6543',
            cursor_factory=RealDictCursor,
            connect_timeout=10  # 10 second connection timeout
        )
        
        cur = conn.cursor()
        
        # Insert the product
        cur.execute("""
            INSERT INTO jcrew_product_cache (
                product_code, product_name, category, subcategory,
                colors, fit_options, sizes, price, image_url,
                description, product_url, scraped_at, created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
            )
        """, (
            product['code'],
            product['name'],
            product['category'],
            product['subcategory'],
            json.dumps(product['colors']),
            json.dumps(product['fit_options']),
            json.dumps(product['sizes']),
            product['price'],
            product['image_url'],
            product['description'],
            product['url'],
            product['scraped_at']
        ))
        
        conn.commit()
        print("✅ Successfully inserted product!")
        
        # Verify
        cur.execute("SELECT COUNT(*) FROM jcrew_product_cache WHERE product_code = %s", (product['code'],))
        count = cur.fetchone()[0]
        print(f"✅ Verification: {count} products with code {product['code']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
        print("🔒 Database connection closed")

if __name__ == "__main__":
    import_single_product()

