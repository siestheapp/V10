#!/usr/bin/env python3
"""
Fixed J.Crew product ingestion script that properly maps JSON keys
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
    """Ingest products from a single JSON file with correct key mapping"""
    print(f"\n📂 Processing {filename}...")
    
    with open(filename, 'r') as f:
        data = json.load(f)
    
    if not isinstance(data, list):
        print(f"  ⚠️ Skipping - not a list of products")
        return 0, 0
    
    success_count = 0
    skip_count = 0
    update_count = 0
    
    for item in data:
        try:
            # Map JSON keys to database columns
            product_code = item.get('code') or item.get('productCode')
            product_name = item.get('name') or item.get('product_name')
            product_url = item.get('url') or item.get('product_url')
            
            # CRITICAL: Get fit_options from the JSON
            fit_options = item.get('fit_options') or item.get('fits') or []
            
            # Get other fields
            colors = item.get('colors') or item.get('colors_available') or []
            if colors and isinstance(colors[0], dict):
                # Convert color objects to strings
                colors = [c.get('name', str(c)) for c in colors]
            
            material = item.get('material') or item.get('fabric')
            price = item.get('price')
            if price and isinstance(price, str):
                # Clean price string
                price = float(price.replace('$', '').replace(',', ''))
            
            sizes = item.get('sizes') or item.get('sizes_available') or []
            
            if not product_code:
                print(f"  ⚠️ Skipping item without product code")
                continue
            
            # Check if product exists
            cur.execute("""
                SELECT id, fit_options 
                FROM jcrew_product_cache 
                WHERE product_code = %s
            """, (product_code,))
            
            existing = cur.fetchone()
            
            if existing:
                existing_id, existing_fits = existing
                # Update if we have better fit data
                if fit_options and (not existing_fits or len(fit_options) > len(existing_fits or [])):
                    cur.execute("""
                        UPDATE jcrew_product_cache
                        SET fit_options = %s,
                            product_name = COALESCE(%s, product_name),
                            colors_available = COALESCE(%s, colors_available),
                            material = COALESCE(%s, material),
                            price = COALESCE(%s, price),
                            sizes_available = COALESCE(%s, sizes_available),
                            updated_at = NOW()
                        WHERE id = %s
                    """, (
                        fit_options, product_name, colors, material, 
                        price, sizes, existing_id
                    ))
                    update_count += 1
                    print(f"  ✅ Updated {product_code}: {product_name[:40]}")
                    print(f"     Fit options: {fit_options}")
                else:
                    skip_count += 1
            else:
                # Insert new product
                cur.execute("""
                    INSERT INTO jcrew_product_cache (
                        product_code, product_name, product_url,
                        fit_options, colors_available, material,
                        price, sizes_available, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                """, (
                    product_code, product_name, product_url,
                    fit_options, colors, material, price, sizes
                ))
                success_count += 1
                print(f"  ✅ Added {product_code}: {product_name[:40] if product_name else 'No name'}")
                print(f"     Fit options: {fit_options}")
                
        except Exception as e:
            print(f"  ❌ Error with item: {e}")
            continue
    
    conn.commit()
    return success_count, skip_count, update_count

def main():
    print("\n" + "=" * 70)
    print("🚀 FIXED J.Crew Product Ingestion Script")
    print("=" * 70)
    
    # List of JSON files to process
    json_files = [
        'jcrew_secret_wash_complete.json',
        'jcrew_broken_in_oxford_complete_20250915_120745.json',
        'jcrew_bowery_shirts_20250915_133708.json',
        'jcrew_linen_all_21_complete.json',
    ]
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    total_added = 0
    total_skipped = 0
    total_updated = 0
    
    for filename in json_files:
        if os.path.exists(filename):
            added, skipped, updated = ingest_json_file(filename, conn, cur)
            total_added += added
            total_skipped += skipped
            total_updated += updated
        else:
            print(f"\n⚠️ File not found: {filename}")
    
    # Get final count
    cur.execute("SELECT COUNT(*), COUNT(DISTINCT product_code) FROM jcrew_product_cache")
    total_entries, unique_codes = cur.fetchone()
    
    # Count products with fit options
    cur.execute("""
        SELECT COUNT(*) 
        FROM jcrew_product_cache 
        WHERE fit_options IS NOT NULL 
        AND array_length(fit_options, 1) > 0
    """)
    products_with_fits = cur.fetchone()[0]
    
    print("\n" + "=" * 70)
    print("✅ INGESTION COMPLETE")
    print("=" * 70)
    print(f"📊 New products added: {total_added}")
    print(f"📊 Products updated: {total_updated}")
    print(f"📊 Products skipped: {total_skipped}")
    print(f"\n📊 Database totals:")
    print(f"   Total entries: {total_entries}")
    print(f"   Unique products: {unique_codes}")
    print(f"   Products with fit options: {products_with_fits}")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
