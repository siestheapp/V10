#!/usr/bin/env python3
"""
Add missing Secret Wash products to database using safe import process
"""

import sys
import json
from datetime import datetime
sys.path.append('/Users/seandavey/projects/V10')
from create_staging_process import SafeJCrewImporter

def prepare_products_for_import():
    """Prepare the missing products for import"""
    
    # These are the two missing Secret Wash products
    products = [
        {
            'product_code': 'CF783',
            'product_name': 'Secret Wash cotton poplin shirt with point collar',
            'product_url': 'https://www.jcrew.com/p/mens/categories/clothing/shirts/secret-wash/secret-wash-cotton-poplin-shirt-with-point-collar/CF783',
            'fit_options': ['Classic', 'Slim', 'Slim Untucked', 'Tall', 'Relaxed'],  # Standard Secret Wash fits
            'colors': None,  # Will be scraped later if needed
            'sizes': None,
            'category': 'Casual Shirts',
            'subcategory': 'Secret Wash'
        },
        {
            'product_code': 'BF792',
            'product_name': 'Secret Wash organic cotton poplin shirt',
            'product_url': 'https://www.jcrew.com/p/mens/categories/clothing/shirts/secret-wash/secret-wash-organic-cotton-poplin-shirt/BF792',
            'fit_options': ['Classic', 'Slim', 'Slim Untucked', 'Tall', 'Relaxed'],  # Standard Secret Wash fits
            'colors': None,
            'sizes': None,
            'category': 'Casual Shirts',
            'subcategory': 'Secret Wash'
        }
    ]
    
    # Save to JSON for import
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'secret_wash_missing_{timestamp}.json'
    
    with open(filename, 'w') as f:
        json.dump(products, f, indent=2)
    
    print(f"✅ Prepared {len(products)} products for import")
    print(f"📁 Saved to: {filename}")
    
    return filename

def import_products(json_file):
    """Import products using safe import process"""
    
    print("\n" + "=" * 80)
    print("IMPORTING MISSING SECRET WASH PRODUCTS")
    print("=" * 80)
    
    # Use our safe importer
    importer = SafeJCrewImporter()
    
    # Load products
    with open(json_file, 'r') as f:
        products = json.load(f)
    
    print(f"\n📦 Importing {len(products)} products:")
    for p in products:
        print(f"   - {p['product_code']}: {p['product_name']}")
    
    # Run safe import process
    success = importer.safe_import_process(json_file)
    
    if success:
        print("\n✅ Import completed successfully")
    else:
        print("\n❌ Import failed or was cancelled")
    
    return success

def verify_import():
    """Verify products were added correctly"""
    
    import psycopg2
    from db_config import DB_CONFIG
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    print("\n" + "=" * 80)
    print("VERIFYING IMPORT")
    print("=" * 80)
    
    codes = ['CF783', 'BF792']
    
    for code in codes:
        cur.execute("""
            SELECT product_code, product_name, fit_options, subcategory
            FROM jcrew_product_cache
            WHERE product_code = %s
        """, (code,))
        
        result = cur.fetchone()
        if result:
            pc, name, fits, subcat = result
            print(f"\n✅ {code}: Added successfully")
            print(f"   Name: {name}")
            print(f"   Fits: {fits}")
            print(f"   Subcategory: {subcat}")
        else:
            print(f"\n❌ {code}: Not found in database")
    
    # Check new total
    cur.execute("""
        SELECT COUNT(*)
        FROM jcrew_product_cache
        WHERE LOWER(product_name) LIKE '%secret wash%'
    """)
    
    total = cur.fetchone()[0]
    print(f"\n📊 Total Secret Wash products now: {total}")
    
    cur.close()
    conn.close()

def main():
    """Main execution"""
    
    print("=" * 80)
    print("ADDING MISSING SECRET WASH PRODUCTS")
    print("=" * 80)
    
    # Step 1: Prepare products
    json_file = prepare_products_for_import()
    
    # Step 2: Import using safe process
    response = input("\n🔄 Ready to import. Continue? (y/n): ")
    if response.lower() == 'y':
        success = import_products(json_file)
        
        if success:
            # Step 3: Verify
            verify_import()
    else:
        print("\n❌ Import cancelled")

if __name__ == "__main__":
    main()
