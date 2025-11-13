#!/usr/bin/env python3
"""
Ingest all J.Crew products from JSON files into the database
This will populate jcrew_product_cache with all pre-scraped data
"""

import json
import psycopg2
import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db_config import DB_CONFIG

def ingest_json_file(filename, conn, cur):
    """Ingest products from a single JSON file"""
    print(f"\n📂 Processing {filename}...")
    
    with open(filename, 'r') as f:
        data = json.load(f)
    
    if not isinstance(data, list):
        print(f"  ⚠️ Skipping - not a list of products")
        return 0, 0
    
    success_count = 0
    skip_count = 0
    
    for item in data:
        try:
            # Extract product data
            product_code = item.get('product_code') or item.get('code') or item.get('productCode')
            product_name = item.get('product_name') or item.get('name')
            product_url = item.get('product_url') or item.get('url', '')
            
            if not product_code or not product_name:
                continue
            
            # Normalize URL if needed
            if product_url and not product_url.startswith('http'):
                product_url = f"https://www.jcrew.com{product_url}"
            
            # Extract other data
            fits = item.get('fits', [])
            colors = item.get('colors', [])
            
            # Handle different color formats
            if colors and isinstance(colors[0], dict):
                colors = [c.get('name', c) for c in colors]
            
            sizes = item.get('sizes_available', item.get('sizes', []))
            price = item.get('price')
            material = item.get('material', '')
            category = item.get('category', 'Tops')
            subcategory = item.get('subcategory', '')
            
            # Create cache key
            cache_key = f"jcrew_product_{product_code}"
            
            # Check if already exists
            cur.execute("""
                SELECT id FROM jcrew_product_cache 
                WHERE cache_key = %s OR product_code = %s
            """, (cache_key, product_code))
            
            if cur.fetchone():
                skip_count += 1
                continue
            
            # Insert into cache
            cur.execute("""
                INSERT INTO jcrew_product_cache (
                    product_url, product_name, product_code, product_image,
                    category, subcategory, sizes_available,
                    colors_available, material, fit_type, fit_options,
                    price, product_description, fit_details,
                    cache_key, created_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW()
                )
            """, (
                product_url,
                product_name,
                product_code,
                '',  # product_image - we'll fetch this on demand
                category,
                subcategory,
                sizes,
                colors,
                material,
                fits[0] if fits else 'Regular',  # Primary fit type
                fits,  # All fit options
                price,
                '',  # product_description
                json.dumps({}),  # fit_details
                cache_key
            ))
            
            success_count += 1
            print(f"  ✅ Added {product_code}: {product_name}")
            print(f"     Fits: {fits}")
            print(f"     Colors: {len(colors)} colors")
            
        except Exception as e:
            print(f"  ❌ Error with product: {e}")
            continue
    
    conn.commit()
    return success_count, skip_count

def main():
    """Main ingestion function"""
    print("🚀 J.Crew Product Ingestion Script")
    print("=" * 50)
    
    # List of JSON files to ingest
    json_files = [
        'jcrew_bowery_shirts_20250915_133708.json',
        'jcrew_broken_in_oxford_complete_20250915_120745.json',
        'jcrew_linen_all_21_complete.json',
        'jcrew_secret_wash_complete.json',
        'jcrew_all_21_urls.json',
        # Add more files as needed
    ]
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    total_success = 0
    total_skip = 0
    
    for filename in json_files:
        if os.path.exists(filename):
            success, skip = ingest_json_file(filename, conn, cur)
            total_success += success
            total_skip += skip
        else:
            print(f"\n⚠️ File not found: {filename}")
    
    # Also check for any other J.Crew JSON files
    print("\n🔍 Looking for additional J.Crew JSON files...")
    for file in os.listdir('.'):
        if file.startswith('jcrew') and file.endswith('.json') and file not in json_files:
            print(f"Found: {file}")
            if input("  Ingest this file? (y/n): ").lower() == 'y':
                success, skip = ingest_json_file(file, conn, cur)
                total_success += success
                total_skip += skip
    
    print("\n" + "=" * 50)
    print(f"✅ Successfully ingested: {total_success} products")
    print(f"⏭️ Skipped (already exists): {total_skip} products")
    
    # Show current state
    cur.execute("SELECT COUNT(*), COUNT(DISTINCT product_code) FROM jcrew_product_cache")
    total, unique = cur.fetchone()
    print(f"\n📊 Database now contains: {total} entries, {unique} unique J.Crew products")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
