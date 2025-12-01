#!/usr/bin/env python3
"""
Import J.Crew broken-in oxford products from scraped JSON data into database
"""

import json
import sys
import os
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def connect_to_database():
    """Connect to the database using direct connection (not pooled)"""
    try:
        conn = psycopg2.connect(
            database='postgres',
            user='fs_core_rw',
            password='CHANGE_ME',
            host='aws-1-us-east-1.pooler.supabase.com',
            port='5432',
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

def load_scraped_data(json_file_path):
    """Load the scraped JSON data"""
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
        print(f"✅ Loaded {len(data)} products from {json_file_path}")
        return data
    except Exception as e:
        print(f"❌ Failed to load JSON data: {e}")
        return None

def insert_product_to_cache(conn, product_data):
    """Insert a single product into jcrew_product_cache table"""
    cur = conn.cursor()
    
    try:
        # Extract product information
        product_code = product_data.get('code', '')
        product_name = product_data.get('name', '')
        category = product_data.get('category', '')
        subcategory = product_data.get('subcategory', '')
        colors = product_data.get('colors', [])
        fit_options = product_data.get('fit_options', [])
        sizes = product_data.get('sizes', [])
        price = product_data.get('price')
        image_url = product_data.get('image_url', '')
        description = product_data.get('description', '')
        url = product_data.get('url', '')
        scraped_at = product_data.get('scraped_at', datetime.now().isoformat())
        
        # Convert lists to JSON strings for database storage
        colors_json = json.dumps(colors) if colors else '[]'
        fit_options_json = json.dumps(fit_options) if fit_options else '[]'
        sizes_json = json.dumps(sizes) if sizes else '[]'
        
        # Check if product already exists
        cur.execute("""
            SELECT id FROM jcrew_product_cache 
            WHERE product_code = %s
        """, (product_code,))
        
        existing = cur.fetchone()
        
        if existing:
            # Update existing product
            cur.execute("""
                UPDATE jcrew_product_cache SET
                    product_name = %s,
                    category = %s,
                    subcategory = %s,
                    colors = %s,
                    fit_options = %s,
                    sizes = %s,
                    price = %s,
                    image_url = %s,
                    description = %s,
                    product_url = %s,
                    scraped_at = %s,
                    updated_at = NOW()
                WHERE product_code = %s
            """, (
                product_name, category, subcategory, colors_json, 
                fit_options_json, sizes_json, price, image_url, 
                description, url, scraped_at, product_code
            ))
            print(f"🔄 Updated existing product: {product_code} - {product_name}")
        else:
            # Insert new product
            cur.execute("""
                INSERT INTO jcrew_product_cache (
                    product_code, product_name, category, subcategory,
                    colors, fit_options, sizes, price, image_url,
                    description, product_url, scraped_at, created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
                )
            """, (
                product_code, product_name, category, subcategory,
                colors_json, fit_options_json, sizes_json, price, image_url,
                description, url, scraped_at
            ))
            print(f"✅ Inserted new product: {product_code} - {product_name}")
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"❌ Error inserting product {product_data.get('code', 'unknown')}: {e}")
        conn.rollback()
        return False

def main():
    """Main function to import J.Crew broken-in oxford products"""
    print("🚀 Starting J.Crew Broken-in Oxford Import")
    print("=" * 50)
    
    # Find the most recent complete JSON file
    json_files = [
        "jcrew_broken_in_oxford_complete_20250915_120745.json",
        "jcrew_broken_in_oxford_complete_20250915_120358.json"
    ]
    
    json_file_path = None
    for file_name in json_files:
        file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), file_name)
        if os.path.exists(file_path):
            json_file_path = file_path
            break
    
    if not json_file_path:
        print("❌ No JSON data file found!")
        return
    
    print(f"📁 Using data file: {json_file_path}")
    
    # Load scraped data
    products = load_scraped_data(json_file_path)
    if not products:
        return
    
    # Connect to database
    conn = connect_to_database()
    if not conn:
        return
    
    try:
        print(f"\n📊 Processing {len(products)} products...")
        
        success_count = 0
        error_count = 0
        
        for i, product in enumerate(products, 1):
            print(f"\n[{i}/{len(products)}] Processing {product.get('code', 'unknown')}...")
            
            if insert_product_to_cache(conn, product):
                success_count += 1
            else:
                error_count += 1
        
        print(f"\n🎉 Import Complete!")
        print(f"✅ Successfully processed: {success_count} products")
        print(f"❌ Errors: {error_count} products")
        
        # Verify import
        cur = conn.cursor()
        cur.execute("""
            SELECT COUNT(*) as total, 
                   COUNT(DISTINCT product_code) as unique_products,
                   COUNT(DISTINCT subcategory) as subcategories
            FROM jcrew_product_cache 
            WHERE subcategory = 'Oxford'
        """)
        
        stats = cur.fetchone()
        print(f"\n📈 Database Stats:")
        print(f"   Total Oxford products: {stats['total']}")
        print(f"   Unique product codes: {stats['unique_products']}")
        print(f"   Subcategories: {stats['subcategories']}")
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()

