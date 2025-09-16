#!/usr/bin/env python3
"""
Safe database updater that validates data before updating to prevent corruption.
Prevents common issues like:
- Dress shirt sizes overwriting regular sizes
- Product category changes without validation
- Empty product names overwriting existing names
"""

import psycopg2
import json
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_config import DB_CONFIG

def is_dress_shirt_size(size):
    """Check if a size looks like a dress shirt size (neck/sleeve)"""
    return '/' in str(size) and any(c.isdigit() for c in str(size))

def validate_update(existing_data, new_data, product_code):
    """
    Validate that an update makes sense and won't corrupt data.
    Returns (is_valid, reason_if_invalid)
    """
    # Check 1: Don't overwrite non-empty name with empty name
    if existing_data.get('product_name') and not new_data.get('product_name'):
        return False, "Would overwrite existing product name with empty name"
    
    # Check 2: Don't switch between dress shirt sizes and regular sizes
    existing_sizes = existing_data.get('sizes_available', [])
    new_sizes = new_data.get('sizes_available', [])
    
    if existing_sizes and new_sizes:
        existing_is_dress = any(is_dress_shirt_size(s) for s in existing_sizes)
        new_is_dress = any(is_dress_shirt_size(s) for s in new_sizes)
        
        if existing_is_dress != new_is_dress:
            return False, f"Size type mismatch: existing={'dress shirt' if existing_is_dress else 'regular'}, new={'dress shirt' if new_is_dress else 'regular'}"
    
    # Check 3: Warn if product category is changing dramatically
    existing_cat = existing_data.get('category', '').lower()
    new_cat = new_data.get('category', '').lower()
    
    if existing_cat and new_cat:
        # These are incompatible category changes
        incompatible = [
            ('dress shirt', 'shirt'),
            ('oxford', 'dress'),
            ('casual', 'formal'),
            ('t-shirt', 'dress shirt')
        ]
        
        for cat1, cat2 in incompatible:
            if (cat1 in existing_cat and cat2 in new_cat) or (cat2 in existing_cat and cat1 in new_cat):
                return False, f"Suspicious category change: '{existing_cat}' -> '{new_cat}'"
    
    # Check 4: Don't overwrite many colors with few colors (likely bad scrape)
    existing_colors = existing_data.get('colors_available', [])
    new_colors = new_data.get('colors_available', [])
    
    if len(existing_colors) > 10 and len(new_colors) < 3:
        return False, f"Would reduce colors from {len(existing_colors)} to {len(new_colors)}"
    
    return True, "Valid update"

def safe_update_product(product_code, new_data):
    """Safely update a product in the database with validation"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    try:
        # Get existing data
        cur.execute("""
            SELECT product_name, product_code, sizes_available,
                   colors_available, category, subcategory, fit_options
            FROM jcrew_product_cache
            WHERE product_code = %s
        """, (product_code,))
        
        row = cur.fetchone()
        
        if row:
            existing_data = {
                'product_name': row[0],
                'product_code': row[1],
                'sizes_available': row[2],
                'colors_available': row[3],
                'category': row[4],
                'subcategory': row[5],
                'fit_options': row[6]
            }
            
            # Validate the update
            is_valid, reason = validate_update(existing_data, new_data, product_code)
            
            if not is_valid:
                print(f"❌ BLOCKED update for {product_code}: {reason}")
                print(f"   Existing: name='{existing_data.get('product_name')}', sizes={existing_data.get('sizes_available', [])[:3]}...")
                print(f"   New: name='{new_data.get('product_name')}', sizes={new_data.get('sizes_available', [])[:3]}...")
                return False
            
            # Perform the update
            print(f"✅ Updating {product_code}: {reason}")
            
        else:
            print(f"➕ Creating new entry for {product_code}")
        
        # Update or insert
        cur.execute("""
            INSERT INTO jcrew_product_cache 
                (product_code, product_name, sizes_available, colors_available, 
                 category, subcategory, fit_options, product_url, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ON CONFLICT (product_code) DO UPDATE SET
                product_name = EXCLUDED.product_name,
                sizes_available = EXCLUDED.sizes_available,
                colors_available = EXCLUDED.colors_available,
                category = EXCLUDED.category,
                subcategory = EXCLUDED.subcategory,
                fit_options = EXCLUDED.fit_options,
                updated_at = CURRENT_TIMESTAMP
            WHERE jcrew_product_cache.product_code = EXCLUDED.product_code
        """, (
            product_code,
            new_data.get('product_name', ''),
            new_data.get('sizes_available', []),
            new_data.get('colors_available', []),
            new_data.get('category', ''),
            new_data.get('subcategory', ''),
            new_data.get('fit_options', []),
            new_data.get('product_url', '')
        ))
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        conn.rollback()
        return False
        
    finally:
        cur.close()
        conn.close()

def main():
    if len(sys.argv) < 2:
        print("Usage: python safe_db_update.py <json_file>")
        print("\nThis script safely updates the database with validation to prevent corruption.")
        print("It will block updates that would:")
        print("  - Replace regular sizes with dress shirt sizes")
        print("  - Overwrite product names with empty values")
        print("  - Make suspicious category changes")
        print("  - Significantly reduce color options")
        sys.exit(1)
    
    json_file = sys.argv[1]
    
    try:
        with open(json_file, 'r') as f:
            products = json.load(f)
        
        print(f"\n📊 Processing {len(products)} products from {json_file}")
        print("=" * 60)
        
        success_count = 0
        blocked_count = 0
        
        for product in products:
            product_code = product.get('product_code') or product.get('code')
            
            if not product_code:
                print(f"⚠️ Skipping product without code: {product}")
                continue
            
            if safe_update_product(product_code, product):
                success_count += 1
            else:
                blocked_count += 1
        
        print("=" * 60)
        print(f"\n📈 Summary:")
        print(f"  ✅ Successfully updated: {success_count}")
        print(f"  ❌ Blocked (prevented corruption): {blocked_count}")
        
    except FileNotFoundError:
        print(f"❌ File not found: {json_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {json_file}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
