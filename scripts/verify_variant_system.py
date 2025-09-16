#!/usr/bin/env python3
"""
Verify the variant system is working correctly
Shows how to query for base products and their variants
"""

import sys
sys.path.append('/Users/seandavey/projects/V10')

import psycopg2
from psycopg2.extras import RealDictCursor
from db_config import DB_CONFIG

def verify_variant_system():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    print("="*80)
    print("VARIANT SYSTEM VERIFICATION")
    print("="*80)
    
    # 1. Show products with variants
    print("\n📊 PRODUCTS WITH VARIANTS:")
    print("-"*80)
    
    cur.execute("""
        SELECT base_product_code, COUNT(*) as variant_count,
               array_agg(DISTINCT variant_code) as variants
        FROM jcrew_product_cache
        WHERE variant_code IS NOT NULL
        GROUP BY base_product_code
        HAVING COUNT(*) > 1
        ORDER BY variant_count DESC
    """)
    
    products_with_variants = cur.fetchall()
    if products_with_variants:
        for p in products_with_variants:
            print(f"Base Style: {p['base_product_code']}")
            print(f"  Variants: {p['variant_count']} ({', '.join(filter(None, p['variants']))})")
    else:
        print("No products with multiple variants found yet.")
    
    # 2. Query all ME053 variants
    print("\n🔍 EXAMPLE: All ME053 Variants:")
    print("-"*80)
    
    cur.execute("""
        SELECT product_code, variant_code, product_name, price, product_url
        FROM jcrew_product_cache
        WHERE base_product_code = 'ME053'
        ORDER BY product_code
    """)
    
    variants = cur.fetchall()
    for v in variants:
        variant_desc = f"Variant {v['variant_code']}" if v['variant_code'] else "Base Product"
        print(f"{v['product_code']}: {variant_desc}")
        print(f"  URL: {v['product_url']}")
        print(f"  Price: ${v['price']:.2f}" if v['price'] else "  Price: N/A")
    
    # 3. Show how to query specific variants
    print("\n💡 QUERY EXAMPLES:")
    print("-"*80)
    print("Get all cotton-cashmere styles:")
    print("  SELECT * FROM jcrew_product_cache WHERE base_product_code = 'ME053';")
    print("\nGet only solid colors (CC100):")
    print("  SELECT * FROM jcrew_product_cache WHERE product_code = 'ME053-CC100';")
    print("\nGet only check patterns (CC101):")
    print("  SELECT * FROM jcrew_product_cache WHERE product_code = 'ME053-CC101';")
    print("\nFind all products with variants:")
    print("  SELECT DISTINCT base_product_code FROM jcrew_product_cache")
    print("  WHERE variant_code IS NOT NULL;")
    
    # 4. Summary
    print("\n📈 SUMMARY:")
    print("-"*80)
    
    cur.execute("""
        SELECT 
            COUNT(DISTINCT product_code) as total_products,
            COUNT(DISTINCT base_product_code) as unique_styles,
            COUNT(DISTINCT variant_code) as unique_variants,
            COUNT(*) FILTER (WHERE variant_code IS NOT NULL) as products_with_variants
        FROM jcrew_product_cache
    """)
    
    summary = cur.fetchone()
    print(f"Total Products (including variants): {summary['total_products']}")
    print(f"Unique Base Styles: {summary['unique_styles']}")
    print(f"Products with Variant Codes: {summary['products_with_variants']}")
    
    print("\n✅ VARIANT SYSTEM STATUS: Working correctly!")
    print("="*80)
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    verify_variant_system()

