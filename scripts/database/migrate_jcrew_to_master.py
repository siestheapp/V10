#!/usr/bin/env python3
"""
Migrate existing J.Crew products from jcrew_product_cache to new product_master/variants structure
Shows the power of the new schema by consolidating duplicate data
"""

import psycopg2
import json
from datetime import datetime
from collections import defaultdict

# Database configuration
DB_CONFIG = {
    "database": "postgres",
    "user": "postgres.lbilxlkchzpducggkrxx",
    "password": "efvTower12",
    "host": "aws-0-us-east-2.pooler.supabase.com",
    "port": "6543"
}

def migrate_jcrew_products():
    """Migrate J.Crew products to new structure"""
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        print("🚀 Migrating J.Crew Products to New Structure")
        print("=" * 60)
        
        # Get J.Crew brand ID
        cur.execute("SELECT id FROM brands WHERE name ILIKE '%j.crew%' OR name ILIKE '%jcrew%' LIMIT 1")
        brand_result = cur.fetchone()
        if not brand_result:
            print("❌ J.Crew brand not found. Creating it...")
            cur.execute("""
                INSERT INTO brands (name, created_at) 
                VALUES ('J.Crew', NOW()) 
                RETURNING id
            """)
            brand_id = cur.fetchone()[0]
        else:
            brand_id = brand_result[0]
        
        print(f"✅ Using J.Crew brand_id: {brand_id}")
        
        # Get category IDs
        cur.execute("SELECT id FROM categories WHERE name = 'Tops' LIMIT 1")
        tops_category = cur.fetchone()
        category_id = tops_category[0] if tops_category else None
        
        # Fetch all J.Crew products from cache
        print("\n📊 Analyzing existing J.Crew products...")
        cur.execute("""
            SELECT DISTINCT ON (product_code) 
                product_code,
                product_name,
                product_description,
                material,
                fit_details,
                fit_options,
                colors_available,
                sizes_available,
                price,
                product_url
            FROM jcrew_product_cache
            WHERE product_code IS NOT NULL
            ORDER BY product_code, created_at DESC
        """)
        
        products = cur.fetchall()
        print(f"Found {len(products)} unique products in cache")
        
        # Group products by code to consolidate data
        product_groups = defaultdict(list)
        
        # Also get all records for color consolidation
        cur.execute("""
            SELECT 
                product_code,
                product_name,
                colors_available,
                fit_options,
                price,
                product_url
            FROM jcrew_product_cache
            WHERE product_code IS NOT NULL
        """)
        
        all_records = cur.fetchall()
        
        # Consolidate all color/fit variations
        product_data = {}
        for code, name, colors, fits, price, url in all_records:
            if code not in product_data:
                product_data[code] = {
                    'name': name,
                    'all_colors': [],
                    'all_fits': set(),
                    'prices': [],
                    'urls': []
                }
            
            # Parse colors (stored as array of JSON strings)
            if colors:
                for color_json in colors:
                    try:
                        if isinstance(color_json, str):
                            color = json.loads(color_json)
                            product_data[code]['all_colors'].append(color)
                    except:
                        pass
            
            # Collect fits
            if fits:
                for fit in fits:
                    product_data[code]['all_fits'].add(fit)
            
            # Collect prices
            if price:
                product_data[code]['prices'].append(price)
            
            product_data[code]['urls'].append(url)
        
        # Statistics before migration
        total_colors = sum(len(p['all_colors']) for p in product_data.values())
        print(f"\n📈 Pre-migration statistics:")
        print(f"   • Unique products: {len(product_data)}")
        print(f"   • Total color variants: {total_colors}")
        print(f"   • Average colors per product: {total_colors/len(product_data):.1f}" if product_data else "")
        
        # Migrate each unique product
        migrated_masters = 0
        migrated_variants = 0
        
        print("\n🔄 Starting migration...")
        print("-" * 40)
        
        for product_code, data in product_data.items():
            if not product_code or not data['name']:
                continue
            
            print(f"\n📦 Processing {product_code}: {data['name'][:40]}...")
            
            # Extract base product info
            base_name = data['name']
            
            # Create product_master record
            try:
                # Prepare materials data (we'll enhance this with scrapers later)
                materials = {
                    "primary": "Cotton",  # Default for now
                    "composition": {"cotton": 100} if "cotton" in base_name.lower() else {}
                }
                
                # Prepare care instructions (defaults for now)
                care_instructions = [
                    "Machine wash cold",
                    "Tumble dry low",
                    "Warm iron if needed"
                ]
                
                # Prepare product details
                product_details = []
                if "secret wash" in base_name.lower():
                    product_details = [
                        "Premium 100% cotton poplin",
                        "Pre-washed for softness",
                        "Button-down collar",
                        "Patch chest pocket"
                    ]
                elif "linen" in base_name.lower():
                    product_details = [
                        "Lightweight linen",
                        "Natural breathability",
                        "Relaxed fit",
                        "Perfect for warm weather"
                    ]
                
                # Insert product_master
                cur.execute("""
                    INSERT INTO product_master (
                        brand_id, product_code, base_name,
                        materials, care_instructions, product_details,
                        category_id, created_at, last_scraped
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                    ON CONFLICT (brand_id, product_code) 
                    DO UPDATE SET 
                        base_name = EXCLUDED.base_name,
                        updated_at = NOW()
                    RETURNING id
                """, (
                    brand_id,
                    product_code,
                    base_name,
                    json.dumps(materials),
                    care_instructions,
                    product_details,
                    category_id
                ))
                
                master_id = cur.fetchone()[0]
                migrated_masters += 1
                print(f"   ✅ Created master record (ID: {master_id})")
                
                # Create variant records for each color
                unique_colors = {}
                for color in data['all_colors']:
                    if isinstance(color, dict):
                        color_name = color.get('name', 'Unknown')
                        # Deduplicate by color name
                        if color_name not in unique_colors:
                            unique_colors[color_name] = color
                
                # Get average price
                avg_price = sum(data['prices']) / len(data['prices']) if data['prices'] else None
                
                # Create variants for each unique color
                for color_name, color_data in unique_colors.items():
                    # For each fit option (or default if none)
                    fits_to_create = list(data['all_fits']) if data['all_fits'] else ['Classic']
                    
                    for fit in fits_to_create:
                        try:
                            cur.execute("""
                                INSERT INTO product_variants (
                                    product_master_id, brand_id,
                                    color_name, color_code, color_hex, color_swatch_url,
                                    fit_option, current_price,
                                    sizes_available, in_stock,
                                    created_at
                                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                                ON CONFLICT (product_master_id, color_name, fit_option) 
                                DO NOTHING
                            """, (
                                master_id,
                                brand_id,
                                color_name,
                                color_data.get('code', ''),
                                color_data.get('hex', ''),
                                color_data.get('imageUrl', ''),
                                fit,
                                avg_price,
                                ['XS', 'S', 'M', 'L', 'XL', 'XXL'],  # Default sizes
                                True
                            ))
                            
                            if cur.rowcount > 0:
                                migrated_variants += 1
                        except Exception as e:
                            print(f"      ⚠️ Skipped variant {color_name}/{fit}: {str(e)[:50]}")
                
                print(f"   ✅ Created {len(unique_colors)} color × {len(fits_to_create)} fit = {len(unique_colors) * len(fits_to_create)} variants")
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)[:100]}")
                conn.rollback()
                continue
        
        # Commit all changes
        conn.commit()
        
        # Show results
        print("\n" + "=" * 60)
        print("✅ MIGRATION COMPLETE!")
        print("=" * 60)
        
        # Get final statistics
        cur.execute("SELECT COUNT(*) FROM product_master WHERE brand_id = %s", (brand_id,))
        final_masters = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM product_variants WHERE brand_id = %s", (brand_id,))
        final_variants = cur.fetchone()[0]
        
        print(f"\n📊 Migration Results:")
        print(f"   • Product masters created: {migrated_masters}")
        print(f"   • Product variants created: {migrated_variants}")
        print(f"   • Total masters in DB: {final_masters}")
        print(f"   • Total variants in DB: {final_variants}")
        
        # Show storage efficiency
        cur.execute("SELECT COUNT(*) FROM jcrew_product_cache")
        cache_records = cur.fetchone()[0]
        
        print(f"\n💾 Storage Efficiency:")
        print(f"   • Old: {cache_records} cache records (with duplicates)")
        print(f"   • New: {final_masters} masters + {final_variants} variants")
        print(f"   • Reduction: {cache_records - (final_masters + final_variants)} records")
        
        # Show sample data
        print("\n📋 Sample migrated products:")
        cur.execute("""
            SELECT 
                pm.product_code,
                pm.base_name,
                COUNT(DISTINCT pv.color_name) as colors,
                COUNT(DISTINCT pv.fit_option) as fits,
                COUNT(pv.id) as total_variants
            FROM product_master pm
            LEFT JOIN product_variants pv ON pm.id = pv.product_master_id
            WHERE pm.brand_id = %s
            GROUP BY pm.product_code, pm.base_name
            LIMIT 5
        """, (brand_id,))
        
        for code, name, colors, fits, variants in cur.fetchall():
            print(f"   • {code}: {name[:40]}")
            print(f"     {colors} colors × {fits} fits = {variants} variants")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔄 J.Crew Product Migration Tool")
    print("Migrating from jcrew_product_cache to product_master/variants")
    print("=" * 60)
    
    success = migrate_jcrew_products()
    
    if success:
        print("\n✨ Migration successful!")
        print("💡 Next: Update scrapers to capture richer product data")
    else:
        print("\n❌ Migration failed")
        print("💾 Your backup is safe at: database_dumps/tailor3_dump_2025-09-14_01-59-30.sql")

